import asyncio
import json
import logging
from typing import Any

import jwt
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.auth.jwt_handler import decode_token
from app.services.providers.mock import MockProvider

logger = logging.getLogger("terminal.websockets")
ws_router = APIRouter(tags=["Realtime WebSockets"])
mock_provider = MockProvider()

MAX_WEBSOCKET_CONNECTIONS = 100


class WebSocketConnectionManager:
    """Manages active WebSocket client connections, quote/news broadcasting, and stale cleanup."""

    def __init__(self, max_connections: int = MAX_WEBSOCKET_CONNECTIONS) -> None:
        self.active_connections: list[WebSocket] = []
        self.max_connections = max_connections

    async def connect(self, websocket: WebSocket) -> bool:
        if len(self.active_connections) >= self.max_connections:
            logger.warning(f"Rejecting WebSocket connection: Limit of {self.max_connections} reached.")
            await websocket.close(code=4002, reason="Server connection limit reached")
            return False

        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total active connections: {len(self.active_connections)}")
        return True

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Remaining active connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict[str, Any]) -> None:
        disconnected: list[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error broadcasting to WebSocket client: {e}")
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_news_alert(self, news_alert_data: dict[str, Any]) -> None:
        """Broadcast real-time news_alert event to all connected clients."""
        payload = {
            "type": "news_alert",
            "data": news_alert_data,
        }
        await self.broadcast(payload)


manager = WebSocketConnectionManager()


@ws_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
) -> None:
    """Production Hardened WebSocket endpoint for quote streaming & news alerts (validates JWT token & handles heartbeat)."""
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if not email:
            await websocket.close(code=4001, reason="Invalid token claims")
            return
    except jwt.PyJWTError:
        await websocket.close(code=4001, reason="Invalid or expired authentication token")
        return

    connected = await manager.connect(websocket)
    if not connected:
        return

    symbols = ["RELIANCE", "TCS", "INFY", "NIFTY50"]
    streaming_task = asyncio.create_task(_stream_realtime_ticks(websocket, symbols))

    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                msg_type = msg.get("type") or msg.get("action")

                if msg_type == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": msg.get("timestamp")})
                elif msg_type == "subscribe" and msg.get("channel"):
                    logger.info(f"Client {email} subscribed to channel: {msg.get('channel')}")
                    await websocket.send_json({"status": "subscribed", "channel": msg.get("channel")})
                elif msg_type == "unsubscribe" and msg.get("channel"):
                    logger.info(f"Client {email} unsubscribed from channel: {msg.get('channel')}")
                    await websocket.send_json({"status": "unsubscribed", "channel": msg.get("channel")})
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON payload"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        streaming_task.cancel()
    except Exception as e:
        logger.error(f"WebSocket session error for {email}: {e}")
        manager.disconnect(websocket)
        streaming_task.cancel()


async def _stream_realtime_ticks(websocket: WebSocket, symbols: list[str]) -> None:
    """Stream simulated realtime quote updates every 2 seconds."""
    try:
        while True:
            await asyncio.sleep(2.0)
            for sym in symbols:
                inst = await mock_provider.get_instrument_by_symbol(sym)
                if inst:
                    q = await mock_provider.get_realtime_quote(inst)
                    payload = {
                        "type": "quote_update",
                        "data": {
                            "symbol": inst.symbol,
                            "instrument_id": str(inst.id),
                            "last_price": q.last_price,
                            "bid_price": q.bid_price,
                            "ask_price": q.ask_price,
                            "timestamp": q.timestamp.isoformat(),
                        },
                    }
                    await websocket.send_json(payload)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.warning(f"Tick streaming cancelled or failed: {e}")
