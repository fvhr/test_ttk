import json
import uuid

from fastapi import WebSocket, WebSocketDisconnect, APIRouter

from api.utils import decrypt_message
from websocket import settings

ws_router = APIRouter(prefix="/socket", tags=["WebSocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket):
        if not settings.WS_RUN:
            await websocket.accept()
            await websocket.send_json(
                {"type": "error", "message": "Сервер временно недоступен."},
            )
            await websocket.close()
            return
        await websocket.accept()
        client_id = str(uuid.uuid4())
        self.active_connections[client_id] = {
            "websocket": websocket,
            "ip": websocket.client.host,
            "port": websocket.client.port,
        }
        await websocket.send_json({"type": "uuid", "client_id": client_id})
        await self.update_connected_clients()

    def disconnect(self, client_id: str, is_admin: bool = False):
        if is_admin:
            client_id = decrypt_message(client_id)
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(
        self,
        message: str,
        client_id: str,
        is_admin: bool = False,
    ):
        if is_admin:
            client_id = decrypt_message(client_id)
            message = "Сообщение от администратора: " + decrypt_message(
                message,
            )
        websocket = self.active_connections[client_id]["websocket"]
        if websocket:
            await websocket.send_json({"type": "message", "message": message})

    async def broadcast(
        self,
        message,
        exclude_id: str = None,
        is_admin: bool = False,
    ):
        if is_admin:
            message = "Сообщение от администратора: " + decrypt_message(
                message,
            )
        for client_id, connection in self.active_connections.items():
            if client_id != exclude_id:
                await connection["websocket"].send_json(
                    {"type": "message", "message": message},
                )

    async def disconnect_all(self):
        for client_id, connection in list(self.active_connections.items()):
            self.disconnect(client_id)
            if connection["websocket"]:
                await connection["websocket"].send_json(
                    {"type": "error", "message": "Сервер был остановлен."},
                )
                await connection["websocket"].close()

    async def update_connected_clients(self):
        client_list = list(self.active_connections.keys())
        for connection in self.active_connections.values():
            try:
                await connection["websocket"].send_json(
                    {"type": "users", "users": client_list},
                )
            except Exception:
                pass


manager = ConnectionManager()


@ws_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    client_id = [
        client_id
        for client_id, values in manager.active_connections.items()
        if values["websocket"] == websocket
    ][0]
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                target_client_id = message_data.get("target")
                message = message_data.get("message")
                if (
                    target_client_id
                    and target_client_id in manager.active_connections
                ):
                    await manager.send_personal_message(
                        f"Private from {client_id}: {message}",
                        target_client_id,
                    )
                else:
                    await manager.broadcast(
                        f"Client {client_id} сказал: {message}",
                    )
            except json.JSONDecodeError:
                await manager.broadcast(
                    f"Client {client_id} сказал: {data}",
                )

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.update_connected_clients()
        await manager.broadcast(
            f"Клиент {client_id} " f"вышел из чата", exclude_id=client_id,
        )
