import atexit
import json
import os
import subprocess
import threading
import time
import urllib
from typing import Any, Optional

import httpx

from uuid import uuid4

from isek.utils.log import log


class A2AProtocolV2:
    """
    Minimal A2A protocol helper for p2p only.

    Responsibilities:
    - Spawn the Node.js p2p bridge (`p2p_server.js`).
    - Send JSON-RPC messages via the local p2p bridge to a remote peer.
    - Expose discovered p2p `peer_id` and `p2p_address`.
    """

    def __init__(
        self,
        *,
        host: str = "127.0.0.1",
        port: int = 8080,
        p2p_enabled: bool = False,
        p2p_server_port: int = 9000,
        relay_ip: str = "",
        relay_peer_id: str = "",
    ) -> None:
        if not isinstance(port, int) or not (0 < port < 65536):
            raise ValueError(f"Invalid agent port: {port}")
        if not isinstance(p2p_server_port, int) or not (0 < p2p_server_port < 65536):
            raise ValueError(f"Invalid p2p server port: {p2p_server_port}")

        self.host = host
        self.port = port
        self.p2p_enabled = p2p_enabled
        self.p2p_server_port = p2p_server_port
        self.relay_ip = relay_ip
        self.relay_peer_id = relay_peer_id

        self.peer_id: Optional[str] = None
        self.p2p_address: Optional[str] = None

        self._p2p_process: Optional[subprocess.Popen] = None
        self._p2p_stdout_thread: Optional[threading.Thread] = None

    # ----------------------------- P2P bootstrap -----------------------------
    def start_p2p_server(self, wait_until_ready: bool = True) -> None:
        """
        Start the Node.js p2p bridge process. If `wait_until_ready` is True,
        block until the bridge exposes a valid `peer_id` and `p2p_address`.
        """
        if not self.p2p_enabled:
            log.debug("p2p disabled; skipping p2p server startup")
            return

        dirc = os.path.dirname(__file__)
        p2p_file_path = os.path.join(dirc, "p2p", "p2p_server.js")

        if not os.path.exists(p2p_file_path):
            raise FileNotFoundError(f"p2p_server.js not found at {p2p_file_path}")

        # Spawn node process
        process = subprocess.Popen(
            [
                "node",
                p2p_file_path,
                f"--port={self.p2p_server_port}",
                f"--agent_port={self.port}",
                f"--relay_ip={self.relay_ip}",
                f"--relay_peer_id={self.relay_peer_id}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        self._p2p_process = process

        def _cleanup() -> None:
            if self._p2p_process and self._p2p_process.poll() is None:
                self._p2p_process.terminate()
            log.debug(f"p2p_server[port:{self.p2p_server_port}] process terminated")

        atexit.register(_cleanup)

        # Stream output in background for visibility
        def _stream_output(stream) -> None:
            for line in iter(stream.readline, ""):
                log.debug(line.rstrip())

        stdout_thread = threading.Thread(
            target=_stream_output, args=(process.stdout,), daemon=True
        )
        stdout_thread.start()
        self._p2p_stdout_thread = stdout_thread

        if not wait_until_ready:
            return

        # Wait for the bridge to be ready and expose context
        while True:
            if process.poll() is not None:
                raise RuntimeError(
                    f"p2p_server process exited with code {process.returncode}"
                )

            context = self._load_p2p_context()
            if context and self.peer_id and self.p2p_address:
                log.debug(f"p2p ready: {context}")
                break
            time.sleep(1)

    def _load_p2p_context(self) -> Optional[dict]:
        try:
            response = httpx.get(
                f"http://localhost:{self.p2p_server_port}/p2p_context",
                timeout=5.0,
            )
            response_body = json.loads(response.content)
            self.peer_id = response_body.get("peer_id")
            self.p2p_address = response_body.get("p2p_address")
            log.debug(f"_load_p2p_context response[{response_body}]")
            return response_body
        except Exception:
            log.exception("Load p2p server context error.")
            return None

    # ------------------------------- Messaging -------------------------------
    def send_message(
        self, sender_node_id: str, receiver_peer_id: str, message: str
    ) -> dict[str, Any]:
        """
        Send a JSON-RPC 2.0 'message/send' request via the local p2p bridge.

        Args:
            sender_node_id: ID of the sender node
            receiver_peer_id: Peer ID of the receiver (not full p2p address)
            message: Message content to send

        Returns the full JSON-RPC response body, mirroring standard A2A.
        """
        # Construct the p2p address using relay information
        receiver_p2p_address = f"/ip4/{self.relay_ip}/tcp/9090/ws/p2p/{self.relay_peer_id}/p2p-circuit/p2p/{receiver_peer_id}"

        request_body = self._build_jsonrpc_send_message_request(sender_node_id, message)
        response = httpx.post(
            url=(
                f"http://localhost:{self.p2p_server_port}/call_peer"
                f"?p2p_address={urllib.parse.quote(receiver_p2p_address)}"
            ),
            json=request_body,
            headers={"Content-Type": "application/json"},
            timeout=60.0,
        )
        return json.loads(response.content)

    # no HTTP direct method; this helper is p2p-only by design

    # ------------------------------- Utilities -------------------------------
    @staticmethod
    def _build_jsonrpc_send_message_request(
        sender_node_id: str, message: str
    ) -> dict[str, Any]:
        """
        Build a JSON-RPC 2.0 request body aligned with SendMessageRequest.
        """
        return {
            "id": uuid4().hex,
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": message}],
                    "messageId": uuid4().hex,
                },
                "metadata": {"sender_node_id": sender_node_id},
            },
        }
