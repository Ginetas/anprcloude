from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for live plate event streaming"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)


manager = ConnectionManager()


@router.websocket("/ws/plate-events")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live plate event streaming"""
    await manager.connect(websocket)

    try:
        while True:
            # Keep connection alive with heartbeat
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def broadcast_plate_event(event: dict):
    """Broadcast a plate event to all connected WebSocket clients"""
    await manager.broadcast({
        "type": "plate_event",
        "data": event
    })
