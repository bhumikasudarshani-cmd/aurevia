import asyncio
import json
import logging
from typing import Dict

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status

# Aapka redis_manager import kar rahe hain
from app.cache.redis_client import redis_manager

logger = logging.getLogger(__name__)
router = APIRouter()

# Mocking verify_token function for now. Replace with actual logic.
async def verify_token_and_get_user_id(token: str):
    return token  # Placeholder

async def get_current_user_id(websocket: WebSocket) -> str:
    """Validate auth (token/cookie/session) before accepting the connection."""
    token = websocket.query_params.get("token")
    user_id = await verify_token_and_get_user_id(token)  # your auth logic
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect()
    return user_id

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()
        self.pubsub_task = None  # Background task for Redis listener

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        await websocket.accept()
        async with self._lock:
            # Close any existing connection for this user first
            existing = self.active_connections.get(user_id)
            if existing:
                await existing.close(code=status.WS_1000_NORMAL_CLOSURE)
            self.active_connections[user_id] = websocket
        logger.info("User %s connected. Total active locally: %d", user_id, len(self.active_connections))

        # Start listening to Redis if it's the first connection
        if self.pubsub_task is None:
            self.pubsub_task = asyncio.create_task(self.listen_to_redis())

    async def disconnect(self, user_id: str) -> None:
        async with self._lock:
            self.active_connections.pop(user_id, None)
        logger.info("User %s disconnected.", user_id)

    async def send_personal_message(self, message: dict, user_id: str) -> None:
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(message)

    # User's robust broadcast renamed to broadcast_local
    async def broadcast_local(self, message: dict, exclude: str | None = None) -> None:
        dead_connections = []

        async def _send(uid: str, ws: WebSocket):
            try:
                await ws.send_json(message)
            except Exception:
                logger.warning("Failed to send to %s, marking for cleanup", uid)
                dead_connections.append(uid)

        await asyncio.gather(*[
            _send(uid, ws)
            for uid, ws in self.active_connections.items()
            if uid != exclude
        ])

        for uid in dead_connections:
            await self.disconnect(uid)

    # --- REDIS INTEGRATION ---
    async def broadcast_to_redis(self, message: dict):
        """Publish message to Redis channel so ALL servers get it."""
        try:
            client = await redis_manager.get_client()
            # Redis only accepts strings/bytes, so we dump JSON
            await client.publish("aurevia_global_chat", json.dumps(message))
        except Exception as e:
            logger.error("Failed to publish to Redis: %s", e)

    async def listen_to_redis(self):
        """Listen to Redis channel and broadcast to local connections."""
        try:
            client = await redis_manager.get_client()
            pubsub = client.pubsub()
            await pubsub.subscribe("aurevia_global_chat")
            
            async for message in pubsub.listen():
                if message["type"] == "message":
                    # Convert Redis string back to dictionary
                    data = json.loads(message["data"])
                    # Send it to all users connected to THIS specific server
                    await self.broadcast_local(data)
        except Exception as e:
            logger.error("Redis PubSub listener error: %s", e)


manager = ConnectionManager()
MAX_MESSAGE_LENGTH = 2000

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str = Depends(get_current_user_id),  # enforce auth
):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            if len(data) > MAX_MESSAGE_LENGTH:
                await websocket.send_json({"type": "error", "detail": "Message too long"})
                continue
                
            # Send ACK to sender
            await manager.send_personal_message(
                {"type": "ack", "content": data}, user_id
            )
            
            # INSTEAD of local broadcast, we push to Redis
            await manager.broadcast_to_redis(
                {"type": "message", "from": user_id, "content": data}
            )
            
    except WebSocketDisconnect:
        await manager.disconnect(user_id)
        await manager.broadcast_to_redis({"type": "system", "content": f"User {user_id} left the chat"})