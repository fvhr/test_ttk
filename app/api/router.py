from fastapi import APIRouter, HTTPException, Depends

from api import settings
from auth import oauth2
from websocket.ws_server import manager

api_router = APIRouter(
    prefix="/api/v1",
    tags=["Api"]
)


@api_router.get("/connected_clients/")
async def get_connected_clients(current_user: int = Depends(oauth2.get_current_user)):
    if current_user:
        return manager.active_connections


# Эндпоинт для широковещательной передачи
@api_router.post("/broadcast/")
async def broadcast_data(message: str, current_user: int = Depends(oauth2.get_current_user)):
    if current_user:
        await manager.broadcast(message)
        return {"message": "Broadcast message sent"}


# Эндпоинт для адресной передачи
@api_router.post("/send/{client_id}/")
async def send_to_client(client_id: str, message: str, current_user: int = Depends(oauth2.get_current_user)):
    if current_user:
        await manager.send_personal_message(message, client_id)
        return {"message": f"Message sent to {client_id}"}


# Эндпоинт для отключения клиента
@api_router.delete("/disconnect/{client_id}/")
async def disconnect_client(client_id: str, current_user: int = Depends(oauth2.get_current_user)):
    if current_user:
        if client_id in manager.active_connections:
            websocket = manager.active_connections[client_id]['websocket']
            await websocket.close()
            manager.disconnect(client_id)
            return {"message": f"Client {client_id} disconnected"}
        raise HTTPException(status_code=404, detail="Client not found")


@api_router.post("/stop_server/")
async def shutdown_server(current_user: int = Depends(oauth2.get_current_user)):
    if current_user:
        await manager.broadcast("Server is shutting down.")
        settings.WS_RUN = False
        return {"message": "Server shutdown initiated."}


@api_router.post("/run_server/")
async def shutdown_server(current_user: int = Depends(oauth2.get_current_user)):
    if current_user:
        await manager.broadcast("Server is shutting down.")
        settings.WS_RUN = True
        return {"message": "Server shutdown initiated."}



