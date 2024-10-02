// Функция для отображения ответа
function showResponse(data) {
    document.getElementById("response").textContent = JSON.stringify(data, null, 2);
}

// Получение подключенных клиентов
function getConnectedClients() {
    fetch("/api/v1/connected_clients/", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem('access_token')}`
        }
    })
        .then(response => response.json())
        .then(data => showResponse(data));
}

// Широковещательное сообщение
function broadcastMessage() {
    const message = prompt("Enter a broadcast message:");
    if (message) {
        fetch("/api/v1/broadcast/", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem('access_token')}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({message})
        })
            .then(response => response.json())
            .then(data => showResponse(data));
    }
}

// Личное сообщение клиенту
function sendToClient() {
    const clientId = prompt("Enter client ID:");
    const message = prompt("Enter a message to send:");
    if (clientId && message) {
        fetch(`/api/v1/send/${clientId}/`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem('access_token')}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({message})
        })
            .then(response => response.json())
            .then(data => showResponse(data));
    }
}

// Отключение клиента
function disconnectClient() {
    const clientId = prompt("Enter client ID to disconnect:");
    if (clientId) {
        fetch(`/api/v1/disconnect/${clientId}/`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem('access_token')}`
            }
        })
            .then(response => response.json())
            .then(data => showResponse(data));
    }
}

// Остановка сервера
function stopServer() {
    fetch("/api/v1/stop_server/", {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem('access_token')}`
        }
    })
        .then(response => response.json())
        .then(data => showResponse(data));
}

// Запуск сервера
function runServer() {
    fetch("/api/v1/run_server/", {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem('access_token')}`
        }
    })
        .then(response => response.json())
        .then(data => showResponse(data));
}