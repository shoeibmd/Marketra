import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.services.providers.mock import MockProvider

logger = logging.getLogger("terminal.websockets")
ws_router = APIRouter(tags=["Realtime WebSockets"])
mock_provider = MockProvider()


class WebSocketConnectionManager:
    """Manages active WebSocket client connections and quote broadcasting."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total active connections: {len(self.active_connections)}")

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


manager = WebSocketConnectionManager()


@ws_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query("valid_token"),
) -> None:
    """WebSocket endpoint for streaming realtime quotes (Indian Market NSE/BSE)."""
    await manager.connect(websocket)

    # Start background loop streaming simulated realtime tick updates for Indian stocks
    symbols = ["RELIANCE", "TCS", "INFY", "NIFTY50"]
    streaming_task = asyncio.create_task(_stream_realtime_ticks(websocket, symbols))

    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                action = msg.get("action")
                channel = msg.get("channel")
                if action == "subscribe" and channel:
                    logger.info(f"Client subscribed to channel: {channel}")
                    await websocket.send_json({"status": "subscribed", "channel": channel})
                elif action == "unsubscribe" and channel:
                    logger.info(f"Client unsubscribed from channel: {channel}")
                    await websocket.send_json({"status": "unsubscribed", "channel": channel})
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON payload"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        streaming_task.cancel()
    except Exception as e:
        logger.error(f"WebSocket session error: {e}")
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
