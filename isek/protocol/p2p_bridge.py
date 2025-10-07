# p2p_bridge.py
import argparse
import asyncio
import json
import base64
import uuid
import logging
from aiohttp import web, ClientSession, ClientTimeout
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCIceServer,
    RTCConfiguration,
)
import aiohttp

logger = logging.getLogger("p2p_bridge")


def b64e(b: bytes) -> str:
    return base64.b64encode(b).decode()


def b64d(s: str) -> bytes:
    return base64.b64decode(s.encode())


# Bob
"""
python p2p_bridge.py \
  --listen-http 9000 \
  --upstream http://127.0.0.1:9999 \
  --role answer \
  --room ROOM123 \
  --signal ws://localhost:7999/ws
"""

# Alice
"""
python p2p_bridge.py \
  --listen-http 8000 \
  --role offer \
  --room ROOM123 \
  --signal ws://localhost:7999/ws
"""


async def signaling_exchange(signal_url, room, is_offer, pc):
    async with aiohttp.ClientSession() as sess:
        logger.info(
            "Connecting to signaling server",
            extra={
                "signal_url": signal_url,
                "room": room,
                "role": "offer" if is_offer else "answer",
            },
        )
        async with sess.ws_connect(f"{signal_url}?room={room}") as ws:

            @pc.on("icecandidate")
            def on_ice_candidate(event):
                if event.candidate:
                    logger.debug(
                        "ICE candidate gathered",
                        extra={"candidate": str(event.candidate)},
                    )
                    asyncio.create_task(
                        ws.send_str(
                            json.dumps(
                                {
                                    "type": "candidate",
                                    "candidate": event.candidate.to_sdp(),
                                    "sdpMid": event.candidate.sdpMid,
                                    "sdpMLineIndex": event.candidate.sdpMLineIndex,
                                }
                            )
                        )
                    )

            if is_offer:
                logger.info("Creating and sending SDP offer")
                offer = await pc.createOffer()
                await pc.setLocalDescription(offer)
                await ws.send_str(
                    json.dumps({"type": "offer", "sdp": pc.localDescription.sdp})
                )
                logger.debug("Offer sent")

            async for msg in ws:
                if msg.type != aiohttp.WSMsgType.TEXT:
                    continue
                data = json.loads(msg.data)
                if data["type"] == "offer" and not is_offer:
                    logger.info("Received offer; creating answer")
                    await pc.setRemoteDescription(
                        RTCSessionDescription(sdp=data["sdp"], type="offer")
                    )
                    answer = await pc.createAnswer()
                    await pc.setLocalDescription(answer)
                    await ws.send_str(
                        json.dumps({"type": "answer", "sdp": pc.localDescription.sdp})
                    )
                    logger.debug("Answer sent")
                elif data["type"] == "answer" and is_offer:
                    logger.info("Received answer; setting remote description")
                    await pc.setRemoteDescription(
                        RTCSessionDescription(sdp=data["sdp"], type="answer")
                    )
                elif data["type"] == "candidate":
                    from aiortc.sdp import candidate_from_sdp

                    c = candidate_from_sdp(data["candidate"])
                    c.sdpMid = data.get("sdpMid")
                    c.sdpMLineIndex = data.get("sdpMLineIndex")
                    logger.debug(
                        "Applying remote ICE candidate",
                        extra={"sdpMid": c.sdpMid, "sdpMLineIndex": c.sdpMLineIndex},
                    )
                    await pc.addIceCandidate(c)


async def run_bridge(listen_http, upstream, role, room, signal_url, timeout_s):
    ice_servers = [RTCIceServer("stun:stun.l.google.com:19302")]
    pc = RTCPeerConnection(configuration=RTCConfiguration(iceServers=ice_servers))

    req_waiters = {}  # id -> Future (waiting for http_res)
    channel_ready = asyncio.Event()
    dc = None  # will hold the DataChannel reference

    def attach_channel(ch):
        nonlocal dc
        dc = ch

        @dc.on("open")
        def _on_open():
            logger.info(
                "DataChannel opened (%s side)", "offer" if role == "offer" else "answer"
            )
            channel_ready.set()

        @dc.on("message")
        async def _on_message(msg):
            try:
                data = json.loads(msg if isinstance(msg, str) else msg.decode())
            except Exception:
                logger.warning("Received non-JSON message on datachannel; ignoring")
                return

            typ = data.get("typ")
            if typ == "http_res":
                fut = req_waiters.pop(data["id"], None)
                if fut and not fut.done():
                    logger.debug(
                        "Received http_res from remote",
                        extra={"id": data["id"], "status": data.get("status")},
                    )
                    fut.set_result(data)

            elif typ == "http_req":
                # GATEWAY: replay to upstream and send back http_res
                if not upstream:
                    res_env = {
                        "typ": "http_res",
                        "id": data["id"],
                        "status": 502,
                        "headers": [["content-type", "text/plain"]],
                        "body": b64e(b"no upstream"),
                    }
                    dc.send(json.dumps(res_env))
                    logger.error(
                        "Received http_req but no upstream configured; responded 502",
                        extra={"id": data.get("id")},
                    )
                    return

                path = data["path"]
                q = data.get("query", "")
                url = (
                    upstream.rstrip("/") + ("" if path.startswith("/") else "/") + path
                )
                if q:
                    url += "?" + q
                method = data["method"]
                headers = [
                    (k, v)
                    for k, v in data.get("headers", [])
                    if k.lower()
                    not in {
                        "host",
                        "content-length",
                        "connection",
                        "keep-alive",
                        "proxy-connection",
                        "upgrade",
                        "trailers",
                    }
                ]
                body = b64d(data.get("body", "")) if data.get("body") else b""

                try:
                    logger.info(
                        "Forwarding http_req to upstream",
                        extra={
                            "id": data["id"],
                            "method": method,
                            "url": url,
                            "body_bytes": len(body),
                        },
                    )
                    async with ClientSession(
                        timeout=ClientTimeout(total=timeout_s)
                    ) as s:
                        async with s.request(
                            method, url, headers=headers, data=body
                        ) as resp:
                            rb = await resp.read()
                            res_env = {
                                "typ": "http_res",
                                "id": data["id"],
                                "status": resp.status,
                                "headers": list(resp.headers.items()),
                                "body": b64e(rb),
                            }
                            logger.info(
                                "Upstream responded",
                                extra={
                                    "id": data["id"],
                                    "status": resp.status,
                                    "resp_bytes": len(rb),
                                },
                            )
                except Exception as e:
                    logger.exception(
                        "Error while proxying to upstream",
                        extra={"id": data.get("id"), "url": url},
                    )
                    res_env = {
                        "typ": "http_res",
                        "id": data["id"],
                        "status": 502,
                        "headers": [["content-type", "text/plain"]],
                        "body": b64e(str(e).encode()),
                    }

                dc.send(json.dumps(res_env))

    # Create or wait for channel
    if role == "offer":
        attach_channel(pc.createDataChannel("tunnel"))
    else:

        @pc.on("datachannel")
        def _on_datachannel(ch):
            attach_channel(ch)

    # Local HTTP server (unchanged)
    async def handle_any(request: web.Request):
        await channel_ready.wait()
        rid = uuid.uuid4().hex
        body = await request.read()
        env = {
            "typ": "http_req",
            "id": rid,
            "method": request.method,
            "path": "/" + request.match_info.get("tail", ""),
            "query": request.query_string,
            "headers": list(request.headers.items()),
            "body": b64e(body),
        }
        fut = asyncio.get_event_loop().create_future()
        req_waiters[rid] = fut
        logger.info(
            "Sending http_req over datachannel",
            extra={
                "id": rid,
                "method": env["method"],
                "path": env["path"],
                "query": env["query"],
                "body_bytes": len(body),
            },
        )
        dc.send(json.dumps(env))

        try:
            res = await asyncio.wait_for(fut, timeout=timeout_s)
        except asyncio.TimeoutError:
            req_waiters.pop(rid, None)
            logger.error("Timeout waiting for http_res from remote", extra={"id": rid})
            return web.Response(status=504, text="gateway timeout")

        headers = res.get("headers", [])
        resp = web.Response(
            status=res.get("status", 502), body=b64d(res.get("body", ""))
        )
        for k, v in headers:
            if k.lower() not in {
                "connection",
                "transfer-encoding",
                "keep-alive",
                "proxy-authenticate",
                "proxy-authorization",
                "trailer",
                "upgrade",
            }:
                resp.headers[k] = v
        logger.debug(
            "Responded to local client",
            extra={"id": rid, "status": resp.status, "resp_headers": len(headers)},
        )
        return resp

    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", handle_any)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", listen_http)
    await site.start()
    logger.info(f"Proxy listening http://127.0.0.1:{listen_http} (transparent)")

    # Start signaling
    await signaling_exchange(signal_url, room, role == "offer", pc)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--listen-http",
        type=int,
        required=True,
        help="Local HTTP port for transparent proxy",
    )
    ap.add_argument(
        "--upstream",
        type=str,
        default="",
        help="Where to forward incoming P2P http_req (gateway mode). Example: http://127.0.0.1:8888",
    )
    ap.add_argument("--role", choices=["offer", "answer"], required=True)
    ap.add_argument("--room", required=True)
    ap.add_argument("--signal", default="ws://YOUR_SIGNALING_HOST:7000/ws")
    ap.add_argument("--timeout", type=int, default=20)
    args = ap.parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )
    logger.info(
        "Starting P2P bridge",
        extra={
            "listen_http": args.listen_http,
            "role": args.role,
            "room": args.room,
            "signal": args.signal,
            "upstream": args.upstream,
        },
    )
    asyncio.run(
        run_bridge(
            args.listen_http,
            args.upstream,
            args.role,
            args.room,
            args.signal,
            args.timeout,
        )
    )
