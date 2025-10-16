import threading
import uuid
from abc import ABC
from typing import Dict, Any
from isek.utils.log import log
import httpx
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard
from a2a.types import MessageSendParams, SendMessageRequest
from a2a.client import A2AClient
from a2a.types import JSONRPCErrorResponse
from isek.utils.common import log_a2a_api_call, log_error
from uuid import uuid4
from a2a.types import Message, Part, Role, TextPart
import asyncio
from isek.web3.isek_identiey import ensure_identity

# Alias for consistency with other modules
logger = log

NodeDetails = Dict[str, Any]
AGENT_CARD_WELL_KNOWN_PATH = "/.well-known/agent.json"


class Node(ABC):
    def __init__(
        self,
        host: str,
        port: int,
        node_id: str,
        **kwargs: Any,  # To absorb any extra arguments
    ):
        if not host:
            raise ValueError("Node host cannot be empty.")
        if not isinstance(port, int) or not (0 < port < 65536):
            raise ValueError(f"Invalid port number for Node: {port}")
        if not node_id:
            node_id = uuid.uuid4().hex

        self.host: str = host
        self.port: int = port
        self.node_id: str = node_id
        self.all_nodes: Dict[str, NodeDetails] = {}

    async def get_agent_card_by_url(self, agent_url: str) -> dict:
        """Fetch and cache agent cards from all configured agent URLs.

        The function uses a simple in-memory cache (``_agent_info_cache``) to avoid
        fetching the ­same agent card repeatedly.  If a card is not cached, it is
        retrieved from the agent’s “well-known” endpoint and stored in the cache.

        Args:
            agent_url: The URL of the agent to fetch the agent card from.

        Returns:
            dict: ``AgentCard`` fully JSON-serialisable object for interoperability with the rest of the MCP pipeline.
        """
        timeout_config = httpx.Timeout(10.0)  # seconds
        log_a2a_api_call(
            "get_agent_card_by_url", f"Fetching agent card for {agent_url}"
        )

        async with httpx.AsyncClient(timeout=timeout_config) as httpx_client:
            response = await httpx_client.get(
                f"{agent_url}{AGENT_CARD_WELL_KNOWN_PATH}"
            )
            response.raise_for_status()
            card_data = response.json()
            return card_data

    async def send_message(self, agent_url: str, query: str) -> str:
        """Execute a task on a remote agent and return the aggregated response.

        Args:
            query: The query to send to the agent.

        Returns:
            str: The content of the task result.
        """
        # Fetch the agent-card data and build a proper ``AgentCard`` instance.
        agent_card_data = await self.get_agent_card_by_url(agent_url)
        agent_card = AgentCard(**agent_card_data)

        logger.info(
            "[send_message] Executing task on agent %s with query: %s",
            agent_card.name,
            query,
        )

        # Build request params
        msg_params = MessageSendParams(
            message=Message(
                role=Role.user,
                parts=[Part(TextPart(text=query))],
                messageId=uuid4().hex,  # Include required messageId field
            )
        )

        logger.debug("[execute_task] Sending non-streaming request …")
        timeout_config = httpx.Timeout(10.0)
        async with httpx.AsyncClient(timeout=timeout_config) as httpx_client:
            client = A2AClient(httpx_client, agent_card=agent_card)
            response = await client.send_message(
                SendMessageRequest(id=uuid4().hex, params=msg_params)
            )

            if isinstance(response, JSONRPCErrorResponse):
                logger.error("[execute_task] Error response received: %s", response)
                return "Error: Unable to execute task"

            message_content = response.root.result.status.message

            logger.info("[execute_task] Task result content: %s", message_content)

            return message_content

    def build_server(
        self,
        app: A2AStarletteApplication,
        name: str = "A2A-Agent",
        daemon: bool = False,
    ):
        """Bootstrap the A2A HTTP server.

        If *daemon* is ``True`` the server will be started in a background thread,
        allowing the current process to continue executing (e.g. to send outbound
        messages) while still accepting inbound HTTP requests.

        Parameters
        ----------
        app : A2AStarletteApplication
            The Starlette application returned from
            ``Node.create_agent_a2a_server``.
        name : str, optional
            A human-readable name for the server, only used for logging.
        daemon : bool, default ``False``
            Whether to start the server in a daemon thread (non-blocking) or run
            it in the foreground (blocking call).
        """

        async def _runner():
            await self.run_server(app, host=self.host, port=self.port, name=name)

        if not daemon:
            # Blocking – run the server in the current thread.
            asyncio.run(_runner())
        else:
            # Non-blocking – run the server in a daemonised background thread
            # so that the main thread can still send outbound messages.
            server_thread = threading.Thread(
                target=lambda: asyncio.run(_runner()), daemon=True
            )
            server_thread.start()
            logger.info(
                "A2A server started in daemon thread (name=%s, port=%s)",
                name,
                self.port,
            )

    @staticmethod
    def create_server(agent_executor, agent_card: AgentCard) -> A2AStarletteApplication:
        """Create the A2A application and ensure wallet/identity for the agent.

        This will:
        - Create or load a wallet scoped to ``agent_card.name``
        - Resolve or register an on-chain identity, if registry settings are provided
        """
        # Ensure wallet + identity, without preventing server startup on failure
        try:
            address, agent_id, tx_hex = ensure_identity(agent_card)
            if agent_id:
                logger.info(
                    "[create_server] Wallet ready: %s; on-chain agentId=%s%s",
                    address,
                    agent_id,
                    f" (tx={tx_hex})" if tx_hex else "",
                )
            else:
                logger.info(
                    "[create_server] Wallet ready: %s; identity not registered or registry not configured",
                    address,
                )
        except Exception as e:
            logger.info("[create_server] Wallet/identity setup skipped: %s", e)

        request_handler = DefaultRequestHandler(
            agent_executor=agent_executor, task_store=InMemoryTaskStore()
        )

        app = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )
        return app

    @staticmethod
    async def run_server(
        app: A2AStarletteApplication,
        host: str = "127.0.0.1",
        port: int = 8080,
        name: str = "node",
    ):
        try:
            config = uvicorn.Config(
                app.build(),
                host=host,
                port=port,
                log_level="error",
                loop="asyncio",
            )

            server = uvicorn.Server(config)

            log_a2a_api_call(
                "server.serve()", f"server: {name}, port: {port}, host: {host}"
            )
            await server.serve()
        except Exception as e:
            log_error(f"run_server() error: {e} - name: {name}, port: {port}")
