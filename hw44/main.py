#1
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, status
from jose import jwt, JWTError
from enum import Enum
from datetime import datetime, timedelta

# Налаштування JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


class UserRole(Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, dict] = {}  # {user_id: {"websocket": ws, "username": name, "role": role}}

    async def connect(self, websocket: WebSocket, user_id: str, username: str, role: UserRole):
        await websocket.accept()
        self.active_connections[user_id] = {"websocket": websocket, "username": username, "role": role}

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def broadcast(self, message: str, sender_name: str):
        for connection in self.active_connections.values():
            await connection["websocket"].send_json({"sender": sender_name, "message": message})


manager = ConnectionManager()


# Функція валідації
async def get_current_user_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Повертає {"sub": user_id, "username": name, "role": role}
    except JWTError:
        return None


# Модерація
class ModerationManager:
    BANNED_WORDS = ["badword1", "badword2"]

    @staticmethod
    def filter_message(text: str):
        for word in ModerationManager.BANNED_WORDS:
            text = text.replace(word, "***")
        return text

    @staticmethod
    async def process_command(command: str, user_role: UserRole):
        if user_role not in [UserRole.ADMIN, UserRole.MODERATOR]:
            return "Access denied"
        # Логіка парсингу команд (/kick, /ban тощо)
        return "Command executed"


@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    user_data = await get_current_user_from_token(token)
    if not user_data:
        await websocket.close(code=1008)
        return

    user_id = user_data["sub"]
    await manager.connect(websocket, user_id, user_data["username"], UserRole(user_data["role"]))

    try:
        while True:
            data = await websocket.receive_text()
            # Фільтрація
            clean_msg = ModerationManager.filter_message(data)
            await manager.broadcast(clean_msg, user_data["username"])
    except WebSocketDisconnect:
        manager.disconnect(user_id)
#2let token = localStorage.getItem("token");
let ws = new WebSocket(`ws://localhost:8000/ws/${token}`);

ws.onopen = () => console.log("Connected");

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(`${data.sender}: ${data.message}`);
};

// Авто-перепідключення
ws.onclose = () => {
    console.log("Disconnected. Refreshing token...");
    // Логіка оновлення токена (refresh token) та реконекту
    setTimeout(() => {
        token = localStorage.getItem("new_token");
        ws = new WebSocket(`ws://localhost:8000/ws/${token}`);
    }, 5000);
};