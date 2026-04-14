/**
 * Kwork Parser - JavaScript для страницы списка заказов
 * Обработка парсинга, фильтрации и статусов
 */

let pollInterval = null;
let totalNewProjects = 0;

// Обработчик кнопки "Откликнулся"
document.addEventListener('click', function (e) {
    if (e.target.closest('.respond-btn')) {
        const btn = e.target.closest('.respond-btn');
        const projectId = btn.dataset.projectId;

        if (confirm('Отметить заказ как "Отклик отправлен"?')) {
            markAsResponded(projectId, btn);
        }
    }
});

function markAsResponded(projectId, btn) {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Отправка...';

    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCSRFToken());

    fetch(`/projects/${projectId}/respond/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRFToken() },
        body: formData,
    })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const card = document.querySelector(`[data-project-id="${projectId}"]`);
                const statusBadge = card.querySelector('.status-badge');
                statusBadge.className = 'badge bg-warning status-badge';
                statusBadge.textContent = 'Отклик отправлен';

                btn.remove();
                showNotification('Статус обновлен!', 'success');
            } else {
                showNotification('Ошибка: ' + (data.error || 'Не удалось обновить статус'), 'danger');
                btn.disabled = false;
                btn.innerHTML = 'Откликнулся';
            }
        })
        .catch(error => {
            showNotification('Ошибка подключения: ' + error.message, 'danger');
            btn.disabled = false;
            btn.innerHTML = 'Откликнулся';
        });
}

function getCSRFToken() {
    // Из скрытого input
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    if (input) return input.value;

    // Из cookie csrftoken
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];

    return cookieValue || '';
}

function showNotification(message, type) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alert.innerHTML = `
        ${escapeHtml(message)}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);

    setTimeout(() => {
        alert.remove();
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

// Запуск парсинга
document.addEventListener('DOMContentLoaded', function () {
    const startBtn = document.getElementById('startParseBtn');
    if (startBtn) {
        startBtn.addEventListener('click', handleStartParse);
    }
});

function handleStartParse() {
    const categoryId = document.getElementById('category_select').value;

    if (!categoryId) {
        alert('Выберите категорию');
        return;
    }

    const btn = document.getElementById('startParseBtn');
    btn.disabled = true;
    document.getElementById('btnText').textContent = 'Парсинг...';
    document.getElementById('category_select').disabled = true;

    document.getElementById('parseStatus').style.display = 'block';
    totalNewProjects = 0;

    const formData = new FormData();
    formData.append('category_id', categoryId);
    formData.append('csrfmiddlewaretoken', getCSRFToken());

    const parseStartUrl = document.getElementById('parse-start-url')?.dataset.url || '/projects/parse-start/';

    fetch(parseStartUrl, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRFToken() },
        body: formData,
    })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            return response.json();
        })
        .then(data => {
            if (data.status === 'started') {
                pollInterval = setInterval(checkStatus, 1000);
            } else {
                showError(data.error || 'Ошибка запуска парсинга');
            }
        })
        .catch(error => {
            showError('Ошибка подключения: ' + error.message);
        });
}

function checkStatus() {
    const parseStatusUrl = document.getElementById('parse-status-url')?.dataset.url || '/projects/parse-status/';

    fetch(parseStatusUrl)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            return response.json();
        })
        .then(data => {
            if (data.events && data.events.length > 0) {
                data.events.forEach(event => handleParseEvent(event));
            }

            if (!data.running && pollInterval) {
                clearInterval(pollInterval);
                pollInterval = null;
            }
        })
        .catch(error => {
            console.error('Ошибка получения статуса:', error);
        });
}

function handleParseEvent(data) {
    const statusEl = document.getElementById('statusText');
    const countEl = document.getElementById('newCount');

    switch (data.type) {
        case 'category_start':
            statusEl.textContent = `Парсинг категории: ${data.category}`;
            break;

        case 'page_start':
            statusEl.textContent = `Загрузка страницы ${data.page}...`;
            break;

        case 'new_project':
            totalNewProjects++;
            countEl.textContent = `${totalNewProjects} новых`;
            addProjectCard(data.project);
            break;

        case 'page_done':
            statusEl.textContent = `Страница ${data.page} обработана (${data.count} новых)`;
            break;

        case 'category_done':
            statusEl.textContent = `Категория "${data.category}" завершена (${data.count} новых)`;
            break;

        case 'complete':
            if (pollInterval) {
                clearInterval(pollInterval);
                pollInterval = null;
            }
            statusEl.textContent = `Парсинг завершен! Всего новых заказов: ${data.total}`;

            setTimeout(() => {
                document.getElementById('startParseBtn').disabled = false;
                document.getElementById('btnText').textContent = 'Запустить парсинг';
                document.getElementById('category_select').disabled = false;
                document.getElementById('parseStatus').style.display = 'none';
            }, 3000);
            break;

        case 'error':
            showError(data.message);
            break;
    }
}

function addProjectCard(project) {
    const projectsList = document.querySelector('#projectsList .row');

    const emptyAlert = projectsList?.querySelector('.alert-info');
    if (emptyAlert) {
        emptyAlert.parentElement.remove();
    }

    const card = document.createElement('div');
    card.className = 'col-md-12 mb-3';

    const cardInner = document.createElement('div');
    cardInner.className = 'card project-card';
    cardInner.style.animation = 'slideIn 0.3s ease-out';

    const cardBody = document.createElement('div');
    cardBody.className = 'card-body';

    const row = document.createElement('div');
    row.className = 'd-flex justify-content-between align-items-start';

    const leftCol = document.createElement('div');
    leftCol.className = 'flex-grow-1';

    const titleEl = document.createElement('h5');
    titleEl.className = 'card-title';
    const titleLink = document.createElement('a');
    titleLink.href = project.url;
    titleLink.target = '_blank';
    titleLink.className = 'text-decoration-none';
    titleLink.textContent = project.title;
    titleEl.appendChild(titleLink);

    const descEl = document.createElement('p');
    descEl.className = 'card-text text-muted small';
    descEl.textContent = project.description
        ? project.description.substring(0, 200) + '...'
        : '';

    const badgesRow = document.createElement('div');
    badgesRow.className = 'd-flex gap-2 flex-wrap';

    const categoryBadge = document.createElement('span');
    categoryBadge.className = 'badge bg-secondary';
    categoryBadge.textContent = project.category;
    badgesRow.appendChild(categoryBadge);

    const statusBadge = document.createElement('span');
    statusBadge.className = 'badge bg-success status-badge';
    statusBadge.textContent = 'Новый';
    badgesRow.appendChild(statusBadge);

    if (project.price) {
        const priceBadge = document.createElement('span');
        priceBadge.className = 'badge bg-primary';
        priceBadge.textContent = project.price + ' RUB';
        badgesRow.appendChild(priceBadge);
    }

    leftCol.appendChild(titleEl);
    leftCol.appendChild(descEl);
    leftCol.appendChild(badgesRow);

    const rightCol = document.createElement('div');
    rightCol.className = 'text-end ms-3';

    const timeEl = document.createElement('small');
    timeEl.className = 'text-muted d-block';
    timeEl.textContent = 'Только что';
    rightCol.appendChild(timeEl);

    if (project.author) {
        const authorEl = document.createElement('small');
        authorEl.className = 'text-muted d-block';
        authorEl.textContent = project.author;
        rightCol.appendChild(authorEl);
    }

    row.appendChild(leftCol);
    row.appendChild(rightCol);
    cardBody.appendChild(row);
    cardInner.appendChild(cardBody);
    card.appendChild(cardInner);

    projectsList.insertBefore(card, projectsList.firstChild);
}

function showError(message) {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }

    const statusEl = document.getElementById('statusText');
    statusEl.innerHTML = `<span class="text-danger">Ошибка: ${escapeHtml(message)}</span>`;

    document.getElementById('startParseBtn').disabled = false;
    document.getElementById('btnText').textContent = 'Запустить парсинг';
    document.getElementById('category_select').disabled = false;

    setTimeout(() => {
        document.getElementById('parseStatus').style.display = 'none';
    }, 5000);
}
