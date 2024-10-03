from fastapi import APIRouter, HTTPException, Depends

from api.schemas import MessageModel
from auth import oauth2
from modules.manager_modules import module_manager
from websocket import settings
from websocket.ws_server import manager
from api.utils import encrypt_message

api_router = APIRouter(prefix="/api/v1", tags=["Api"])


@api_router.get("/connected_clients/")
async def get_connected_clients(
    current_user: int = Depends(oauth2.get_current_user),
):
    if current_user:
        return list(manager.active_connections)
    return {}


# Эндпоинт для широковещательной передачи
@api_router.post("/broadcast/")
async def broadcast_data(
    message: MessageModel,
    current_user: int = Depends(oauth2.get_current_user),
):
    if current_user:
        await manager.broadcast(
            encrypt_message(message.message),
            is_admin=True,
        )
        return {"message": f"Broadcast message sent {message.message}"}
    return {}


# Эндпоинт для адресной передачи
@api_router.post("/send/{client_id}/")
async def send_to_client(
    client_id: str,
    message: MessageModel,
    current_user: int = Depends(oauth2.get_current_user),
):
    if current_user:
        await manager.send_personal_message(
            encrypt_message(message.message),
            encrypt_message(client_id),
            is_admin=True,
        )
        return {
            "message": f"Message sent to {client_id}, "
            f"message: {message.message}",
        }
    return {}


# Эндпоинт для отключения клиента
@api_router.delete("/disconnect/{client_id}/")
async def disconnect_client(
    client_id: str,
    current_user: int = Depends(oauth2.get_current_user),
):
    if current_user:
        if client_id in manager.active_connections:
            await manager.active_connections[client_id]["websocket"].close()
            manager.disconnect(encrypt_message(client_id), is_admin=True)
            await manager.update_connected_clients()
            await manager.broadcast(
                f"Клиент {client_id} " f"вышел из чата", exclude_id=client_id
            )
            return {"message": f"Client {client_id} disconnected"}
        raise HTTPException(status_code=404, detail="Client not found")
    return {}


@api_router.post("/stop_server/")
async def shutdown_server(
    current_user: int = Depends(oauth2.get_current_user),
):
    if current_user:
        await manager.broadcast("Server is shutting down.")
        await manager.disconnect_all()
        settings.WS_RUN = False
        return {"message": "Server shutdown initiated."}
    return {}


@api_router.post("/run_server/")
async def shutdown_server(
    current_user: int = Depends(oauth2.get_current_user),
):
    if current_user:
        settings.WS_RUN = True
        return {"message": "Server run initiated."}
    return {}


@api_router.get("/modules/")
def get_all_modules():
    return list(module_manager.modules.keys())


@api_router.get("/modules/{module_name}/")
def get_module_data(module_name: str):
    if module_name in module_manager.modules_states:
        return {
            "module_name": module_name,
            "status": module_manager.modules_states[module_name],
        }
    raise HTTPException(status_code=404, detail="Module not found")
