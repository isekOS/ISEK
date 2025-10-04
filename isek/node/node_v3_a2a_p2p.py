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
from typing import Optional
from httpx import ASGITransport

# Alias for consistency with other modules
logger = log

NodeDetails = Dict[str, Any]
AGENT_CARD_WELL_KNOWN_PATH = "/.well-known/agent.json"

# --- P2P <-> ASGI bridge (drop-in, no changes to your app logic) ---

try:
    # If py-libp2p isn't installed at import time, we still want your module to import cleanly.
    from libp2p.host.basic_host import BasicHost  # type: ignore
except Exception:  # pragma: no cover
    BasicHost = Any  # type: ignore


class A2AP2PNode:
    """
    Libp2p transport adapter for A2AStarletteApplication.

    - Registers a libp2p stream handler for `protocol_id`.
    - For each stream: read 1 length-prefixed JSON-RPC request -> POST it into your
      Starlette app via in-process ASGI -> write back the response -> close.
    """

    def __init__(
        self,
        app: "A2AStarletteApplication",
        host: BasicHost,
        *,
        protocol_id: str = "/a2a/1.0.0",
        rpc_url: str = "/",
        agent_card_url: str = "/.well-known/agent.json",
        extended_agent_card_url: str = "/agent/authenticatedExtendedCard",
        starlette_kwargs: Optional[dict[str, Any]] = None,
        max_message_bytes: int = 32 * 1024 * 1024,
    ) -> None:
        self.app = app
        self.host = host
        self.protocol_id = protocol_id
        self.rpc_url = rpc_url
        self.max_message_bytes = max_message_bytes

        # Build the ASGI app exactly as your HTTP server would
        self._starlette_app = self.app.build(
            agent_card_url=agent_card_url,
            rpc_url=rpc_url,
            extended_agent_card_url=extended_agent_card_url,
            **(starlette_kwargs or {}),
        )
        # Zero-copy in-process calls to your routes
        self._transport = ASGITransport(app=self._starlette_app)
        self._started = False

    async def start(self) -> None:
        if self._started:
            return
        self.host.set_stream_handler(self.protocol_id, self._on_stream)  # type: ignore[attr-defined]
        self._started = True

    async def stop(self) -> None:
        if not self._started:
            return
        try:
            self.host.remove_stream_handler(self.protocol_id)  # type: ignore[attr-defined]
        except Exception:
            self.host.set_stream_handler(self.protocol_id, lambda *_: None)  # type: ignore[attr-defined]
        finally:
            self._started = False

    @staticmethod
    async def rpc_call_over_p2p(
        host: BasicHost,
        peer_id: Any,
        body: bytes,
        *,
        protocol_id: str = "/a2a/1.0.0",
        timeout: Optional[float] = 60.0,
    ) -> bytes:
        """
        Convenience client: open a stream to `peer_id`, send one JSON-RPC request
        (length-prefixed), return the response bytes.
        """
        stream = await host.new_stream(peer_id, [protocol_id])  # type: ignore[attr-defined]
        try:
            await _write_msg(stream, body)
            return await _read_msg(stream, timeout=timeout)
        finally:
            try:
                await stream.close()
            except Exception:
                pass

    async def _on_stream(self, stream: Any) -> None:
        try:
            req_bytes = await _read_msg(stream, max_len=self.max_message_bytes)
            async with httpx.AsyncClient(
                transport=self._transport, base_url="http://a2a"
            ) as client:
                resp = await client.post(
                    self.rpc_url,
                    content=req_bytes,
                    headers={"content-type": "application/json"},
                )
            await _write_msg(stream, resp.content)
        except Exception as e:
            # Best-effort JSON-RPC error envelope
            try:
                import json

                err = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e),
                    },
                    "id": None,
                }
                await _write_msg(stream, json.dumps(err).encode("utf-8"))
            except Exception:
                pass
        finally:
            try:
                await stream.close()
            except Exception:
                pass


# ---- simple 4-byte big-endian length-prefixed framing ----


async def _read_exact(stream: Any, n: int, *, timeout: Optional[float] = None) -> bytes:
    buf = bytearray()
    remaining = n
    while remaining > 0:
        chunk = await (
            asyncio.wait_for(stream.read(remaining), timeout)
            if timeout is not None
            else stream.read(remaining)
        )  # type: ignore[attr-defined]
        if not chunk:
            raise EOFError("Unexpected EOF while reading from P2P stream")
        buf += chunk
        remaining -= len(chunk)
    return bytes(buf)


async def _read_msg(
    stream: Any, *, timeout: Optional[float] = None, max_len: int = 32 * 1024 * 1024
) -> bytes:
    import struct as _struct

    header = await _read_exact(stream, 4, timeout=timeout)
    (length,) = _struct.unpack(">I", header)
    if length > max_len:
        raise ValueError(f"P2P message too large: {length} > {max_len}")
    return await _read_exact(stream, length, timeout=timeout)


async def _write_msg(stream: Any, payload: bytes) -> None:
    import struct as _struct

    header = _struct.pack(">I", len(payload))
    await stream.write(header + payload)  # type: ignore[attr-defined]
    try:
        await stream.drain()  # optional in some libp2p impls
    except Exception:
        pass


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
        self._p2p_host: Optional[BasicHost] = None
        self._p2p_protocol_id: str = "/a2a/1.0.0"
        self._p2p_server: Optional[A2AP2PNode] = None

    # ---- P2P wiring (optional) ----

    def attach_p2p_host(
        self, p2p_host: BasicHost, *, protocol_id: str = "/a2a/1.0.0"
    ) -> None:
        """
        Provide a libp2p host the node can use. Call this once you have a host.
        Does not start serving; see start_p2p_server().
        """
        self._p2p_host = p2p_host
        self._p2p_protocol_id = protocol_id
        logger.info("P2P host attached (protocol_id=%s)", protocol_id)

    async def start_p2p_server(
        self,
        app: "A2AStarletteApplication",
        *,
        rpc_url: str = "/",
        agent_card_url: str = "/.well-known/agent.json",
        extended_agent_card_url: str = "/agent/authenticatedExtendedCard",
        starlette_kwargs: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Run the same Starlette app over libp2p. Keeps HTTP server independent.
        """
        if self._p2p_host is None:
            raise RuntimeError("No P2P host attached. Call attach_p2p_host() first.")
        if self._p2p_server is not None:
            logger.info("P2P server already started; ignoring duplicate start.")
            return

        self._p2p_server = A2AP2PNode(
            app=app,
            host=self._p2p_host,
            protocol_id=self._p2p_protocol_id,
            rpc_url=rpc_url,
            agent_card_url=agent_card_url,
            extended_agent_card_url=extended_agent_card_url,
            starlette_kwargs=starlette_kwargs,
        )
        await self._p2p_server.start()
        logger.info("P2P server started (protocol_id=%s)", self._p2p_protocol_id)

    async def stop_p2p_server(self) -> None:
        """
        Stop serving over libp2p (no effect on HTTP server).
        """
        if self._p2p_server is None:
            return
        try:
            await self._p2p_server.stop()
            logger.info("P2P server stopped.")
        finally:
            self._p2p_server = None

    async def send_jsonrpc_over_p2p(
        self,
        peer_id: Any,
        request_body: bytes,
        *,
        timeout: Optional[float] = 60.0,
    ) -> bytes:
        """
        Send a raw JSON-RPC request body to a remote peer over libp2p and return raw bytes.
        You control the envelope; this avoids assumptions about your JSON-RPC method names.
        """
        if self._p2p_host is None:
            raise RuntimeError("No P2P host attached. Call attach_p2p_host() first.")
        return await A2AP2PNode.rpc_call_over_p2p(
            host=self._p2p_host,
            peer_id=peer_id,
            body=request_body,
            protocol_id=self._p2p_protocol_id,
            timeout=timeout,
        )

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
            await self.run_server(app, port=self.port, name=name)

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
        request_handler = DefaultRequestHandler(
            agent_executor=agent_executor, task_store=InMemoryTaskStore()
        )

        app = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )

        return app

    @staticmethod
    async def run_server(app: A2AStarletteApplication, port: int, name: str):
        try:
            config = uvicorn.Config(
                app.build(),
                host="127.0.0.1",
                port=port,
                log_level="error",
                loop="asyncio",
            )

            server = uvicorn.Server(config)

            log_a2a_api_call(
                "server.serve()", f"server: {name}, port: {port}, host: 127.0.0.1"
            )
            await server.serve()
        except Exception as e:
            log_error(f"run_server() error: {e} - name: {name}, port: {port}")
