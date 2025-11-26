"""
Settings WebSocket Endpoint
Real-time settings updates, system status streaming, and notifications
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set, Dict, Any
import asyncio
import json
from datetime import datetime

router = APIRouter()

# Store active WebSocket connections
active_connections: Set[WebSocket] = set()


class ConnectionManager:
    """Manages WebSocket connections for settings updates"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"Settings WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        print(f"Settings WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.add(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def send_setting_update(self, setting_key: str, old_value: Any, new_value: Any):
        """Broadcast a setting update to all clients"""
        message = {
            "type": "setting_update",
            "data": {
                "key": setting_key,
                "old_value": old_value,
                "new_value": new_value,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
        await self.broadcast(message)

    async def send_system_status(self, status: Dict[str, Any]):
        """Broadcast system status update"""
        message = {
            "type": "system_status",
            "data": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast(message)

    async def send_notification(self, notification_type: str, message_text: str, level: str = "info"):
        """Send a notification to all clients"""
        message = {
            "type": "notification",
            "data": {
                "notification_type": notification_type,
                "message": message_text,
                "level": level,  # info, warning, error
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
        await self.broadcast(message)

    async def send_performance_metrics(self, metrics: Dict[str, Any]):
        """Broadcast performance metrics"""
        message = {
            "type": "performance_metrics",
            "data": metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast(message)


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/settings")
async def settings_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time settings updates.

    Streams:
    - Setting changes (setting_update)
    - System status updates (system_status)
    - Performance metrics (performance_metrics)
    - Notifications (notification)

    Messages format:
    {
        "type": "setting_update" | "system_status" | "performance_metrics" | "notification",
        "data": {...},
        "timestamp": "ISO 8601 timestamp"
    }
    """
    await manager.connect(websocket)

    try:
        # Send initial connection confirmation
        await manager.send_personal_message(
            {
                "type": "connection_established",
                "data": {
                    "message": "Connected to settings stream",
                    "client_id": id(websocket),
                },
                "timestamp": datetime.utcnow().isoformat(),
            },
            websocket,
        )

        # Send initial system status
        initial_status = {
            "status": "healthy",
            "worker_id": "worker-001",
            "uptime": 0,
            "hardware_type": "CPU",
            "active_cameras": 0,
            "active_models": 0,
        }
        await manager.send_personal_message(
            {
                "type": "system_status",
                "data": initial_status,
                "timestamp": datetime.utcnow().isoformat(),
            },
            websocket,
        )

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Receive messages from client (if any)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)

                # Handle client requests
                if message.get("type") == "ping":
                    await manager.send_personal_message(
                        {
                            "type": "pong",
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                        websocket,
                    )
                elif message.get("type") == "get_status":
                    # Send current system status
                    await manager.send_personal_message(
                        {
                            "type": "system_status",
                            "data": initial_status,  # In real app, get actual status
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                        websocket,
                    )

            except asyncio.TimeoutError:
                # Send heartbeat if no messages received
                await manager.send_personal_message(
                    {
                        "type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    websocket,
                )
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "data": {"message": "Invalid JSON"},
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Helper function to broadcast setting updates from other parts of the app
async def broadcast_setting_update(setting_key: str, old_value: Any, new_value: Any):
    """
    Call this function from settings endpoints to broadcast updates.
    Example usage in settings.py:
        from .settings_websocket import broadcast_setting_update
        await broadcast_setting_update("hardware.type", "cpu", "gpu")
    """
    await manager.send_setting_update(setting_key, old_value, new_value)


async def broadcast_system_status(status: Dict[str, Any]):
    """Broadcast system status update"""
    await manager.send_system_status(status)


async def broadcast_notification(notification_type: str, message: str, level: str = "info"):
    """Broadcast a notification"""
    await manager.send_notification(notification_type, message, level)
