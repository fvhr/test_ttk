let currentUserId = '';
let ws;

function connectWebSocket() {
    ws = new WebSocket('ws://localhost:8000/socket/ws');

    ws.onopen = function () {
        console.log("Connected to WebSocket");
        hideServerStatus();
        hideReconnectButton();  // Скрыть кнопку при успешном соединении
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
        } else if (data.type === 'disconnect') {
            // Если сервер отключает пользователя
            handleDisconnect();
        }
    };

    ws.onclose = function () {
        console.log("Disconnected from WebSocket");
        showReconnectButton();
        showServerStatus("Сервер был остановлен.");
    };

    ws.onerror = function (error) {
        console.error("WebSocket error:", error);
        showReconnectButton();
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

// Обработчик отключения пользователя
function handleDisconnect() {
    console.log("You have been disconnected by the server.");
    showReconnectButton();
    showServerStatus("Вы были отключены от сервера.");
}

// Показать кнопку reconnect
function showReconnectButton() {
    document.getElementById('reconnect-btn').classList.remove('hidden');
}

// Скрыть кнопку reconnect
function hideReconnectButton() {
    document.getElementById('reconnect-btn').classList.add('hidden');
}

// Логика для кнопки reconnect
function reconnect() {
    window.location.reload();  // Перезагружает страницу, чтобы восстановить соединение
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
