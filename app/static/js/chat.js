let currentUserId = '';
let token = "{{ token }}";  // Токен, переданный с сервера
let ws;

function connectWebSocket() {
    ws = new WebSocket(`ws://localhost:8000/socket/ws/${token}`);

    ws.onopen = function () {
        console.log("Connected to WebSocket");
        hideServerStatus();
    };

    ws.onmessage = function (event) {
        let data = JSON.parse(event.data);
        if (data.type === 'uuid') {
            document.getElementById('ws-id').textContent = data.client_id;
            currentUserId = data.client_id;
        } else if (data.type === 'message') {
            appendMessage(data.message);
        } else if (data.type === 'users') {
            updateUserList(data.users);
        } else if (data.type === 'error') {
            // Если сервер отправляет сообщение о проблеме
            showServerStatus(data.message);
        }
    };

    ws.onclose = function () {
        console.log("Disconnected from WebSocket");
        document.getElementById('reconnect-btn').classList.remove('hidden');
        showServerStatus("Сервер был остановлен.");
    };

    ws.onerror = function (error) {
        console.error("WebSocket error:", error);
        document.getElementById('reconnect-btn').classList.remove('hidden');
        showServerStatus("Сервер временно недоступен.");
    };
}

function appendMessage(msg) {
    let messages = document.getElementById('messages');
    let message = document.createElement('li');
    let content = document.createTextNode(msg);
    message.appendChild(content);
    messages.appendChild(message);
}

function updateUserList(users) {
    let userList = document.getElementById('user-list');
    userList.innerHTML = '';  // Очистить список
    users.forEach(user => {
        let li = document.createElement('li');
        li.textContent = user;
        if (user === currentUserId) {
            li.style.color = 'green';  // Текущий пользователь зеленым
        }
        li.onclick = () => {
            if (user !== currentUserId) {
                let personalMessage = prompt("Send a personal message to " + user);
                if (personalMessage) {
                    ws.send(JSON.stringify({target: user, message: personalMessage}));
                }
            }
        };
        userList.appendChild(li);
    });
}

function sendMessage(event) {
    let input = document.getElementById("messageText");
    ws.send(input.value);
    input.value = '';
    event.preventDefault();
}

function reconnect() {
    document.getElementById('reconnect-btn').classList.add('hidden');
    connectWebSocket();
}

function showServerStatus(message) {
    let statusDiv = document.getElementById('server-status');
    statusDiv.textContent = message;
    statusDiv.classList.remove('hidden');
    statusDiv.style.display = 'block'; // Убедитесь, что сообщение выводится
}

function hideServerStatus() {
    let statusDiv = document.getElementById('server-status');
    statusDiv.classList.add('hidden');
    statusDiv.style.display = 'none'; // Скрыть элемент явно
}

connectWebSocket();