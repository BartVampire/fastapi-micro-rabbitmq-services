document.addEventListener('DOMContentLoaded', () => {
    const categoryLinks = document.querySelectorAll('.filters_menu .filter-link');
    const productGrid = document.querySelector('.filters-content .row.grid');
    const paginationContainer = document.querySelector('.pagination');

    let isLoading = false; // Индикатор состояния загрузки

    function fetchMenuData(url) {
        if (isLoading) return; // Прерываем, если запрос уже выполняется.
        isLoading = true;

        // Показываем индикатор загрузки
        productGrid.innerHTML = `
            <div class="col-12 text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
            </div>
        `;

        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка загрузки');
            }
            return response.text();
        })
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Обновляем DOM, заменяя содержимое
            const newProductGrid = doc.querySelector('.filters-content .row.grid');
            const newPagination = doc.querySelector('.pagination');

            if (newProductGrid) {
                productGrid.replaceChildren(...newProductGrid.children);
            }

            if (newPagination) {
                paginationContainer.replaceChildren(...newPagination.children);
                updateEventListeners(); // Обновляем слушатели для новых элементов
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            productGrid.innerHTML = `
                <div class="col-12 text-center text-danger">
                    Не удалось загрузить данные. Попробуйте позже.
                </div>
            `;
        })
        .finally(() => {
            isLoading = false; // Снимаем блокировку после завершения
        });
    }

    function updateEventListeners() {
        const newCategoryLinks = document.querySelectorAll('.filters_menu .filter-link');
        const newPaginationLinks = document.querySelectorAll('.pagination .page-link');

        newCategoryLinks.forEach(link => {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                if (!isLoading) {
                    history.pushState(null, '', this.href);
                    fetchMenuData(this.href);
                }
            });
        });

        newPaginationLinks.forEach(link => {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                if (!isLoading) {
                    history.pushState(null, '', this.href);
                    fetchMenuData(this.href);
                }
            });
        });
    }

    // Первоначальная установка слушателей
    updateEventListeners();

    // Обработка кнопки "назад" в браузере
    window.addEventListener('popstate', () => {
        fetchMenuData(window.location.href);
    });
});