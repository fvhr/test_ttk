from fastapi import APIRouter, HTTPException, Depends

from api.schemas import MessageModel
from auth import oauth2
from modules.manager_modules import module_manager
from websocket import settings
from websocket.ws_server import manager
from .utils import encrypt_message

api_router = APIRouter(
    prefix="/api/v1",
    tags=["Api"]
)


@api_router.get("/connected_clients/")
async def get_connected_clients(current_user: int = Depends(oauth2.get_current_user)):
    if current_user:
        return list(manager.active_connections)


# Эндпоинт для широковещательной передачи
@api_router.post("/broadcast/")
async def broadcast_data(message: MessageModel, current_user: int = Depends(oauth2.get_current_user)):
    if current_user:
        await manager.broadcast(encrypt_message(message.message), is_admin=True)
        return {"message": f"Broadcast message sent {message.message}"}


# Эндпоинт для адресной передачи
@api_router.post("/send/{client_id}/")
async def send_to_client(client_id: str, message: MessageModel, current_user: int = Depends(oauth2.get_current_user)):
    if current_user:
        await manager.send_personal_message(encrypt_message(message.message), encrypt_message(client_id), is_admin=True)
        return {"message": f"Message sent to {client_id}, message: {message.message}"}


# Эндпоинт для отключения клиента
@api_router.delete("/disconnect/{client_id}/")
async def disconnect_client(client_id: str, current_user: int = Depends(oauth2.get_current_user)):
    if current_user:
        if client_id in manager.active_connections:
            websocket = manager.active_connections[client_id]['websocket']
            await websocket.close()
            manager.disconnect(client_id, is_admin=True)
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
        settings.WS_RUN = True
        return {"message": "Server run initiated."}


@api_router.get("/modules/")
def get_all_modules():
    return list(module_manager.modules.keys())


@api_router.get("/modules/{module_name}/")
def get_module_data(module_name: str):
    if module_name in module_manager.modules_states:
        return {"module_name": module_name, "status": module_manager.modules_states[module_name]}
    raise HTTPException(status_code=404, detail="Module not found")
