if (window.location.pathname === '/query_history') {
    localStorage.removeItem("requestId");
document.addEventListener("DOMContentLoaded", function() {
    let container = document.getElementById('results-container');
    let rawResults = JSON.parse(container.dataset.results);
    document.getElementById("result").style.display="block";
    if (rawResults.length > 0) {
    const lastItem = rawResults.pop();
    localStorage.setItem("requestId", lastItem.uq_id)
}
    renderContent(1, 1, rawResults);
});
}

let currentPostId = null;
const backBtn = document.getElementById('backBtn');
if (backBtn !== null) {
    backBtn.addEventListener("click", function() {
        window.location.href = '/history';
    });
}

 async function submitForm(event) {
        event.preventDefault();
        const form = document.querySelector('#filter');
        const formData = new FormData(form);
        let data = {};
        formData.forEach((value, key) => {
            if (key === 'SelectedType' || key === 'SelectedRegPeriod' || key === 'SelectedReg') {
                if (!Array.isArray(data[key])) {
                    data[key] = [];
                }
                data[key].push(value);
            } else {
                data[key] = value;
            }
        });
        try {
            const response = await fetch('/getInfo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data),
            });
            if (!response.ok) {
                throw new Error(`Ошибка сети: ${response.status}, ${response.statusText}`);
            }
            const result = await response.json();
            // console.log(result)
            document.getElementById("filter").style.display="none";
            document.getElementById("result").style.display="block";
            window.localStorage.setItem("requestId", result.request_id);
            renderContent(result.current_page, result.total_pages, result.data);
      
        } catch (error) {
            console.error('Ошибка:', error.message || error);
        }
    }

const backStage = document.getElementById('back') || null;
if (backStage !== null) {
backStage.addEventListener("click", () =>{
    delete result.data;
    document.getElementById("filter").style.display="block";
    document.getElementById("result").style.display="none";
    
    });
}

function clearForm(e) {
    e.preventDefault(); 
    document.getElementById('data').reset();
    delete result.data; 
}

const PAGED_DATA = 'http://localhost/paged_data/';
const contentDiv = document.querySelector("#content");
if (contentDiv) { 
    async function loadData(url, pageNumber, requestId) {
        let baseUrl = new URL(window.location.href);
        baseUrl.pathname = '/paged_data';
        baseUrl.searchParams.append('page', pageNumber);
        baseUrl.searchParams.append('unique_request_id', window.localStorage.getItem("requestId"))

     try {  
            // const requestId = window.localStorage.getItem("requestId"); 
            // console.log(requestId)
            const response = await fetch(baseUrl.toString());
            // console.log(baseUrl.toString())
            const rawData = await response.json();
            // console.log(rawData)
            const { current_page, total_pages, data } = rawData;
            renderContent(current_page, total_pages, data);
        } catch (error) {
            console.error("Ошибка:", error.message);
        }
    }

    function renderContent(currentPage, totalPages, data) {
    const contentDiv = document.querySelector("#content");
    if (totalPages === 0 || data.length === 0) { 
        contentDiv.innerHTML = `<p>Нет данных для отображения.</p>`; 
        return;
    }
        contentDiv.innerHTML = data.map(item => {
            let dateObj = new Date(item.publication_date);
            let formatPublicationDate = dateObj.toISOString().split('T')[0].replace(/-/g, '');
            return `
                <div class="data-block">
                    Номер публикации: ${item.publication_number} &nbsp;&nbsp;&nbsp;&nbsp; Дата публикации: ${new Date(item.publication_date).toLocaleDateString()} 
                    
                    <button class="comment-button" data-key="${item.document_unique_key}">Комментарий</button><br/><br/>
                    <a href="doc/${item.publishing_country}${item.publication_number}${item.doc_kind}_${formatPublicationDate}" target="_blank">
                        Документ ${item.publishing_country} ${item.publication_number} ${item.doc_kind} &nbsp; ${new Date(item.publication_date).toLocaleDateString()}
                    </a><br/>
                    <div class="comment-block" id="${item.document_unique_key}">
                    ${item.comment && item.comment.trim().length > 0 ? prepareComment(item.comment) : ''}</div>
                </div>
            `;
        }).join('');
            document.querySelectorAll('.comment-button').forEach(button => {
                button.addEventListener('click', function(event) {
                currentPostId = this.dataset.key;
                window.localStorage.setItem("currentPostId", currentPostId);
                openModal(data);
            });
});
        updatePagination(totalPages, currentPage);
    }

function updatePagination(totalPages, currentPage) {
    const paginationList = document.querySelector("#pagination");
    paginationList.innerHTML = ""; // Очистка текущего содержимого

    // Функция для создания элемента страницы
    function createLink(pageNumber, activePage) {
        const pageItem = document.createElement("li");
        pageItem.className = "page-item" + (activePage === pageNumber ? " active" : "");
        
        const pageLink = document.createElement("a");
        pageLink.href = "#";
        pageLink.className = "page-link";
        pageLink.textContent = pageNumber.toString(); // Преобразуем номер страницы в строку
        
        pageLink.addEventListener("click", () => {
            let baseUrl = new URL(window.location.href);
            baseUrl.pathname = '/paged_data';
            baseUrl.searchParams.append('page', pageNumber);
            baseUrl.searchParams.append('unique_request_id', window.localStorage.getItem("requestId"))
            loadData(PAGED_DATA, pageNumber, UNIQUE_REQUEST_ID); // Загрузка данных для выбранной страницы
        });
        
        pageItem.appendChild(pageLink);
        paginationList.appendChild(pageItem);
    }
    
    // Основная логика построения пагинации
    if (totalPages > 10) {
        // Определим границы показываемых страниц вокруг текущей
        const startPage = Math.max(currentPage - 4, 1); // Начало видимых страниц (не менее 1-й)
        const endPage = Math.min(startPage + 8, totalPages); // Окончание видимых страниц (не более общей суммы)
        
        // Построение основных номеров страниц
        for (let i = startPage; i <= endPage; i++) {
            createLink(i, currentPage);
        }
        
        // Элементы пропуска и дополнительные страницы
        if (startPage > 1) { // Проверяем необходимость вставки первого пропускающего эллипса
            const firstEllipsisItem = document.createElement("li");
            firstEllipsisItem.className = "page-item disabled";
            
            const firstEllipsisLink = document.createElement("span");
            firstEllipsisLink.className = "page-link";
            firstEllipsisLink.textContent = "...";
            
            firstEllipsisItem.appendChild(firstEllipsisLink);
            // paginationList.insertBefore(firstEllipsisItem, paginationList.firstChild.nextSibling); // После первой страницы
        }
        
        if (endPage < totalPages) { // Проверяем необходимость последнего пропускающего эллипса
            const lastEllipsisItem = document.createElement("li");
            lastEllipsisItem.className = "page-item disabled";
            
            const lastEllipsisLink = document.createElement("span");
            lastEllipsisLink.className = "page-link";
            lastEllipsisLink.textContent = "...";
            
            lastEllipsisItem.appendChild(lastEllipsisLink);
            paginationList.appendChild(lastEllipsisItem); // Перед последней страницей
        }
        
        // Добавляем первую и последнюю страницы, если это имеет смысл
        if (currentPage !== 1 && startPage > 1) {
            createLink(1, currentPage); // Первая страница
            }
        
        if (currentPage !== totalPages && endPage < totalPages) {
            createLink(totalPages, currentPage); // Последняя страница
        }
        
        // Добавление кнопок "Назад" и "Вперед"
        if (currentPage > 1) {
            const prevButton = document.createElement("li");
            prevButton.className = "page-item";
            
            const prevLink = document.createElement("a");
            prevLink.href = "#";
            prevLink.className = "page-link";
            prevLink.textContent = "Назад";
            
            prevLink.addEventListener("click", () => {
                loadData(PAGED_DATA, currentPage - 1, UNIQUE_REQUEST_ID); // Переход на предыдущую страницу
            });
            
            prevButton.appendChild(prevLink);
            paginationList.prepend(prevButton); // Добавляем перед всеми элементами
        }
        
        if (currentPage < totalPages) {
            const nextButton = document.createElement("li");
            nextButton.className = "page-item";
            
            const nextLink = document.createElement("a");
            nextLink.href = "#";
            nextLink.className = "page-link";
            nextLink.textContent = "Вперед";
            
            nextLink.addEventListener("click", () => {
                loadData(PAGED_DATA, currentPage + 1, UNIQUE_REQUEST_ID); // Переход на следующую страницу
            });
            
            nextButton.appendChild(nextLink);
            paginationList.appendChild(nextButton); // Добавляем после всех элементов
        }
    } else { // Когда всего страниц меньше или равно 10
        for (let i = 1; i <= totalPages; i++) {
            createLink(i, currentPage);
        }
    }


    function createLink(pageNumber, activePage) {
        const item = document.createElement('li');
        item.className = 'page-item';
        const link = document.createElement('a');
        link.href = '#';
        link.className = 'page-link';
        link.textContent = pageNumber.toString();
        link.addEventListener('click', function(event) {
            event.preventDefault();
            loadData(PAGED_DATA, pageNumber, UNIQUE_REQUEST_ID);
        });
        if (pageNumber === activePage) {
            link.className += ' active';
        }
        item.appendChild(link);
        paginationList.appendChild(item);
    }
}
    const UNIQUE_REQUEST_ID = 0;
    // console.log(UNIQUE_REQUEST_ID)

    // Первый запрос к /search для получения первоначальных данных
    async function initialLoad() {
        await loadData(PAGED_DATA, 1, UNIQUE_REQUEST_ID);
    }

    // Выполняем первый запрос при загрузке страницы
    window.onload = initialLoad;
}

// Проверяем, было ли перенаправление успешным
const notification = document.getElementById('notification');

// Проверяем наличие параметра status в URL
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.has('status') && urlParams.get('status') === 'success') {
    notification.style.display = 'block';
            setTimeout(() => {
                notification.classList.remove('show'); // Запуск анимации исчезания
            }, 5000); 
}


function openModal(data) {
    document.getElementById("commentModal").style.display = "block";
    let postID = window.localStorage.getItem("currentPostId")
    const result = data.find(item => item.document_unique_key === postID);
    if (result !== undefined && result.comment !== null) {
        document.getElementById("commentText").value = result.comment;
    } else {
        document.getElementById("commentText").value = '';
    }
        
}
// Закрытие модального окна
function closeModal() {
    document.getElementById("commentModal").style.display = "none";
}

async function sendComment(event) {
    const commentText = document.getElementById("commentText").value.trim();
    if (!commentText) return alert("Введите комментарий!");
        let postID = window.localStorage.getItem('currentPostId');
    try {
        await fetch('/save_comment', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: commentText, button_id: postID })
        });
        document.getElementById("commentText").value = "";
        
        alert("Ваш комментарий отправлен успешно.");
        closeModal();
        const commentBlock = document.getElementById(postID);
        if (commentBlock) {
            commentBlock.innerHTML = prepareComment(commentText);
        }
        console.log(document.getElementById(postID).value)
    } catch (err) {
        console.error(err);
        alert("Ошибка при отправке комментария.");
    }
}

function prepareComment(comment) {
    /** Обрезает комментарий для вывода */
    const words = comment.split(' ');
    const truncatedWords = words.slice(0, 30);
    return truncatedWords.join(' ') + '...';
}