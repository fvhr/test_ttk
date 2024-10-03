document.addEventListener('DOMContentLoaded', function () {
  document.getElementById('loginForm').onsubmit = function (event) {
      event.preventDefault(); // Отменяем стандартное поведение формы
      console.log('Форма отправлена');

      const formData = new FormData(event.target);

      // Отправка POST запроса для авторизации
      fetch('/pages/login', {
          method: 'POST',
          body: formData,
      })
      .then(response => {
          if (response.ok) {
              return response.json(); // Преобразуем ответ в JSON
          } else {
              return response.json().then(errorData => {
                  document.querySelector('.text-red-500').textContent = errorData.message;
                  throw new Error(errorData.message);
              });
          }
      })
      .then(data => {
          localStorage.setItem('access_token', data.access_token);
          console.log(data.access_token);
          window.location.href = "/pages/api";
      })
      .catch(error => {
          console.error('Ошибка:', error);
      });
  };
});