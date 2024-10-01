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
        await websocket.send_text(f"Your UUID: {client_id}")
        await self.update_connected_clients()

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        websocket = self.active_connections[client_id]["websocket"]
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str, exclude_id: str = None):
        for client_id, connection in self.active_connections.items():
            if client_id != exclude_id:
                await connection["websocket"].send_text(message)

    async def update_connected_clients(self):
        client_list = list(self.active_connections.keys())
        for connection in self.active_connections.values():
            await connection["websocket"].send_text(f"Connected clients: {client_list}")


manager = ConnectionManager()


@ws_router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, enabled: bool = Depends(check_ws_router_enabled)):
    if client_id != settings.WS_TOKEN or not enabled:
        await websocket.close()
        return {"data": "invalid token"}

    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id} сказал: {data}", exclude_id=client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"Клиент {client_id} вышел из чата")
