// Карусель отзывов
document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.querySelector('.carousel');
    let currentIndex = 0;

    setInterval(() => {
        const items = carousel.querySelectorAll('.item');
        items[currentIndex].classList.remove('active');
        currentIndex = (currentIndex + 1) % items.length;
        items[currentIndex].classList.add('active');
    }, 5000);
});

// Валидация и отправка формы
document.getElementById('contact-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const name = event.target.querySelector('input[type="text"]').value;
    const email = event.target.querySelector('input[type="email"]').value;
    const message = event.target.querySelector('textarea').value;

    if (name && email && message) {
        alert('Спасибо за ваше сообщение!');
        // Здесь может быть вызов AJAX для отправки данных на сервер
    } else {
        alert('Пожалуйста, заполните все поля формы.');
    }
});
