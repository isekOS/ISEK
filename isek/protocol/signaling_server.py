# signaling_server.py
import logging
from aiohttp import web

logger = logging.getLogger("signaling_server")

rooms = {}  # room -> set of websockets


async def ws_handler(request):
    room = request.query.get("room")
    if not room:
        return web.Response(status=400, text="room is required")
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    room_set = rooms.setdefault(room, set())
    room_set.add(ws)
    logger.info("Client joined room", extra={"room": room, "peers": len(room_set)})
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                # broadcast to others in the same room
                broadcast_count = 0
                for peer in list(room_set):
                    if peer is not ws:
                        try:
                            await peer.send_str(msg.data)
                            broadcast_count += 1
                        except Exception:
                            logger.exception(
                                "Failed to send message to peer", extra={"room": room}
                            )
                logger.debug(
                    "Broadcasted message to peers",
                    extra={
                        "room": room,
                        "broadcast_count": broadcast_count,
                        "payload_bytes": len(msg.data),
                    },
                )
            elif msg.type == web.WSMsgType.ERROR:
                logger.error(
                    "WebSocket error",
                    extra={"room": room, "exception": str(ws.exception())},
                )
    finally:
        room_set.discard(ws)
        logger.info("Client left room", extra={"room": room, "peers": len(room_set)})
        if not room_set:
            rooms.pop(room, None)
            logger.info("Room removed (empty)", extra={"room": room})
    return ws


app = web.Application()
app.add_routes([web.get("/ws", ws_handler)])

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )
    logger.info("Starting signaling server", extra={"host": "0.0.0.0", "port": 7999})
    web.run_app(app, host="0.0.0.0", port=7999)
