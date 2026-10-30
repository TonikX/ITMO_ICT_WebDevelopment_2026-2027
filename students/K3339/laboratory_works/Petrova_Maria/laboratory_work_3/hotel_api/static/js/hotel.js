// Общие функции для трёх страниц. Данные выводятся как текст, без HTML.
function showMessage(text, success = false) {
    const box = document.getElementById('message');
    box.textContent = text;
    box.className = `alert alert-${success ? 'success' : 'danger'}`;
}
const fieldNames = {
    number: 'Номер', floor: 'Этаж', room_type: 'Тип номера', phone: 'Телефон',
    last_name: 'Фамилия', first_name: 'Имя', middle_name: 'Отчество',
    passport_series: 'Серия паспорта', passport_number: 'Номер паспорта',
    arrival_city: 'Город прибытия', room: 'Номер', guests: 'Гости',
    check_in: 'Дата заселения', planned_check_out: 'Дата выезда'
};
function errorText(data) {
    if (Array.isArray(data)) return data.map(errorText).join('\n');
    if (data && typeof data === 'object') {
        return Object.entries(data).map(([key, value]) =>
            `${fieldNames[key] || key}: ${errorText(value)}`).join('\n');
    }
    return String(data);
}
async function api(url, data) {
    const options = {credentials: 'same-origin', headers: {'Accept': 'application/json'}};
    if (data !== undefined) {
        options.method = 'POST';
        options.headers['Content-Type'] = 'application/json';
        options.headers['X-CSRFToken'] = document.querySelector('[name=csrfmiddlewaretoken]').value;
        options.body = JSON.stringify(data);
    }
    let response;
    try { response = await fetch(url, options); }
    catch { throw new Error('Не удалось связаться с сервером. Проверьте соединение.'); }
    const result = await response.json().catch(() => null);
    if (!response.ok) {
        if (response.status === 403) throw new Error('Нет доступа. Войдите под активной учётной записью сотрудника гостиницы.');
        throw new Error(result ? errorText(result) : `Ошибка сервера (${response.status}). Попробуйте позже.`);
    }
    return result;
}
function fillSelect(id, items, label) {
    const select = document.getElementById(id);
    select.replaceChildren();
    if (!select.multiple) select.add(new Option('Выберите…', ''));
    items.forEach(item => select.add(new Option(label(item), item.id)));
}
function fillTable(id, rows) {
    const body = document.getElementById(id);
    body.replaceChildren();
    rows.forEach(values => {
        const row = body.insertRow();
        values.forEach(value => { row.insertCell().textContent = value ?? '—'; });
    });
}
function bindForm(url, successText, afterSave) {
    const form = document.getElementById('create-form');
    form.addEventListener('submit', async event => {
        event.preventDefault();
        const button = form.querySelector('button[type=submit]');
        button.disabled = true;
        try {
            const data = Object.fromEntries(new FormData(form));
            delete data.csrfmiddlewaretoken;
            if (form.elements.guests) data.guests = Array.from(form.elements.guests.selectedOptions, option => Number(option.value));
            await api(url, data);
            form.reset();
            showMessage(successText, true);
            if (afterSave) {
                try { await afterSave(); }
                catch (error) { showMessage(`${successText} Не удалось обновить список: ${error.message}`); }
            }
        } catch (error) { showMessage(error.message); }
        finally { button.disabled = false; }
    });
}
