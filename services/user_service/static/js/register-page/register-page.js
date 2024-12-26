// Вспомогательная функция для переключения видимости пароля
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    // Меняем тип поля между 'password' и 'text'
    const newType = input.type === 'password' ? 'text' : 'password';
    input.type = newType;
}

/**
 * Проверяет соответствие пароля требованиям безопасности
 * @param {string} password - пароль для проверки
 * @returns {boolean} - результат проверки
 */
function validatePassword(password) {
    const requirements = {
        minLength: 8,              // минимальная длина
        hasUpperCase: /[A-Z]/,     // минимум одна заглавная буква
        hasLowerCase: /[a-z]/,     // минимум одна строчная буква
        hasNumbers: /\d/,          // минимум одна цифра
    };

    const checks = {
        length: password.length >= requirements.minLength,
        upper: requirements.hasUpperCase.test(password),
        lower: requirements.hasLowerCase.test(password),
        number: requirements.hasNumbers.test(password),
    };

    // Возвращаем true только если все проверки пройдены
    return Object.values(checks).every(check => check === true);
}

/**
 * Валидация отдельного поля ввода
 * @param {HTMLInputElement} input - поле ввода для валидации
 * @returns {boolean} - результат валидации
 */
function validateInput(input) {
    const value = input.value.trim();
    let isValid = true;
    let errorMessage = '';

    // Объект с правилами валидации для каждого поля
    const validationRules = {
        first_name: {
            validate: (val) => val.length >= 2 && val.length <= 30,
            message: 'Длина должна быть от 2 до 30 символов'
        },
        last_name: {
            validate: (val) => val.length >= 2 && val.length <= 30,
            message: 'Длина должна быть от 2 до 30 символов'
        },
        username: {
            validate: (val) => /^[A-Za-z0-9_-]{3,50}$/.test(val),
            message: 'Используйте только латинские буквы, цифры, _ и - (от 3 до 50 символов)'
        },
        email: {
            validate: (val) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val),
            message: 'Введите корректный email'
        },
        phone_number: {
            validate: (val) => /^\+\d{1,3}\d{4,14}$/.test(val),
            message: 'Формат: +79188888888'
        },
        password: {
            validate: validatePassword,
            message: 'Пароль должен содержать минимум 8 символов, включая заглавные, строчные буквы и цифры'
        },
        confirm_password: {
            validate: (val) => val === document.getElementById('password').value,
            message: 'Пароли не совпадают'
        }
    };

    // Если для поля есть правила валидации
    if (validationRules[input.name]) {
        const rule = validationRules[input.name];
        isValid = rule.validate(value);
        errorMessage = rule.message;
    }

    // Получаем элемент для отображения ошибки
    const errorElement = document.getElementById(`${input.name}-error`);

    // Обновляем классы и сообщения об ошибках
    updateValidationUI(input, errorElement, isValid, errorMessage, value);

    return isValid;
}

/**
 * Обновляет UI элементы в соответствии с результатами валидации
 * @param {HTMLInputElement} input - поле ввода
 * @param {HTMLElement} errorElement - элемент для отображения ошибки
 * @param {boolean} isValid - результат валидации
 * @param {string} errorMessage - сообщение об ошибке
 * @param {string} value - значение поля
 */
function updateValidationUI(input, errorElement, isValid, errorMessage, value) {
    if (!isValid && value !== '') {
        errorElement.textContent = errorMessage;
        input.classList.add('invalid');
        input.classList.remove('valid');
    } else {
        errorElement.textContent = '';
        input.classList.remove('invalid');
        if (value !== '') {
            input.classList.add('valid');
        }
    }
}

/**
 * Обработчик отправки формы
 * @param {Event} event - событие отправки формы
 */
// Обновляем функцию handleSubmit
async function handleSubmit(event) {
    event.preventDefault();

    // Валидация всех полей перед отправкой
    const inputs = document.querySelectorAll('.form-control');
    let isValid = true;

    inputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;
        }
    });

    if (!isValid) {
        return;
    }

    const form = event.target;
    const formData = new FormData(form);

    // Удаляем поле confirm_password
    formData.delete('confirm_password');

    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/user/user/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'  // Добавляем заголовок для определения AJAX запроса
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            window.location.href = '/auth/login';
        } else {
            const errorData = await response.json();
            handleServerErrors(errorData);
        }
    } catch (error) {
        console.error('Error:', error);
        const firstErrorElement = document.querySelector('.error-message');
        if (firstErrorElement) {
            firstErrorElement.textContent = 'Произошла ошибка при регистрации. Попробуйте позже.';
        }
    }
}

/**
 * Обработка ошибок, полученных от сервера
 * @param {Object} data - ответ сервера
 */
function handleServerErrors(data) {
    if (data.detail) {
        if (Array.isArray(data.detail)) {
            // Если сервер вернул массив ошибок
            data.detail.forEach(error => {
                const errorElement = document.getElementById(`${error.loc[1]}-error`);
                if (errorElement) {
                    errorElement.textContent = error.msg;
                }
            });
        } else {
            // Если сервер вернул общую ошибку
            const firstErrorElement = document.querySelector('.error-message');
            if (firstErrorElement) {
                firstErrorElement.textContent = data.detail;
            }
        }
    }
}

// Инициализация обработчиков событий при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    // Добавляем валидацию при вводе для всех полей
    document.querySelectorAll('.form-control').forEach(input => {
        input.addEventListener('input', () => validateInput(input));
        input.addEventListener('blur', () => validateInput(input));
    });

    // Добавляем обработчик отправки формы
    document.getElementById('registerForm').addEventListener('submit', handleSubmit);
});