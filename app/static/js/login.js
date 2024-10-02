// Обработка отправки формы
document.getElementById('loginForm').onsubmit = async function (event) {
    event.preventDefault(); // Отменяем стандартное поведение формы

    const formData = new FormData(event.target);

    // Отправка POST запроса для авторизации
    const response = await fetch('/pages/login', {
        method: 'POST',
        body: formData,
    });

    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token); // Сохраняем токен в localStorage
        window.location.href = "/pages/api"; // Перенаправление на страницу API
    } else {
        const errorData = await response.json();
        document.querySelector('.text-red-500').textContent = errorData.message; // Отображаем сообщение об ошибке
    }
};