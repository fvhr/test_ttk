import json
import uuid

from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Depends, APIRouter

from websocket import settings

ws_router = APIRouter(
    prefix="/socket",
    tags=["WebSocket"]
)


def check_ws_router_enabled():
    if not settings.WS_RUN:
        raise HTTPException(status_code=503, detail="WebSocket server is disabled")


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        client_id = str(uuid.uuid4())
        self.active_connections[client_id] = {
            "websocket": websocket,
            "ip": websocket.client.host,
            "port": websocket.client.port,
        }
        # Отправляем UUID клиенту
        await websocket.send_json({"type": "uuid", "client_id": client_id})
        await self.update_connected_clients()

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        websocket = self.active_connections[client_id]["websocket"]
        if websocket:
            await websocket.send_json({"type": "message", "message": message})

    async def broadcast(self, message: str, exclude_id: str = None):
        for client_id, connection in self.active_connections.items():
            if client_id != exclude_id:
                await connection["websocket"].send_json({"type": "message", "message": message})

    async def update_connected_clients(self):
        client_list = list(self.active_connections.keys())
        for connection in self.active_connections.values():
            await connection["websocket"].send_json({"type": "users", "users": client_list})


manager = ConnectionManager()


@ws_router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, enabled: bool = Depends(check_ws_router_enabled)):
    if client_id != settings.WS_TOKEN:
        await websocket.close()
        return {"data": "invalid token"}

    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                # Предполагаем, что данные могут быть в JSON (для личных сообщений)
                message_data = json.loads(data)
                target_client_id = message_data.get('target')
                message = message_data.get('message')
                if target_client_id and target_client_id in manager.active_connections:
                    await manager.send_personal_message(f"Private from {client_id}: {message}", target_client_id)
                else:
                    await manager.broadcast(f"Client {client_id} сказал: {message}", exclude_id=client_id)
            except json.JSONDecodeError:
                # Обычные сообщения (не JSON)
                await manager.broadcast(f"Client {client_id} сказал: {data}", exclude_id=client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"Клиент {client_id} вышел из чата")
        await manager.update_connected_clients()
