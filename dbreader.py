import uvicorn

from os import path
from math import ceil
from fastapi import FastAPI, Request, APIRouter, Form, Query, HTTPException, Depends
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import show_full_query, PSDataBase
from models import *
from services import *
from funcs import *
from loggers import logger

PAGE_SIZE = 10
DOCS_FIELDS = ['document_unique_key', 'date', 'request_ip']
QH_FIELDS = ['ur_id', 'date', 'query', 'request_ip', 'params']
HISTORY_REQUEST = 'SELECT * FROM query_history ORDER BY date DESC LIMIT 10;'
DOCS_HISTORY = 'SELECT * FROM docs_history ORDER BY date DESC LIMIT 10;'

options = {}
cached_search_results = {}
initial_config = load_state()
config = load_state()

data = []
current_user_ip = 0

app = FastAPI()
router = APIRouter()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

db = PSDataBase(initial_config['host'], initial_config['port'], initial_config['database'], initial_config['user'], initial_config['password'])


def load_path():
    config = load_state()
    return config


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("page.html", {"request": request})


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    options = load_select()
    return templates.TemplateResponse("hist.html", {"request": request, "options": options})


@app.get("/getInfo", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})


@app.post("/getInfo")
async def search_endpoint(request: Request, query: SearchQuery, page: int = Query(default=1)):
    # Обработка параметров поиска
    try: 
        unique_request_id = get_unique_id()
        form_data = query.model_dump()
        full_query, params = form_query('inner_contour', form_data)
        raw_results = db.get_rows(full_query, params)
        cached_search_results[unique_request_id] = raw_results
        total_items = len(raw_results)
        h_query = show_full_query(full_query, params)
    except Exception as error:
        logger.error('Error in getInfo: {}'.format((str(error))))
    try:
        data_to_insert = [unique_request_id, datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), h_query, current_user_ip, params]
        query_idx = db.insert_list('query_history', QH_FIELDS, data_to_insert)
        options['options1'].clear()
        result = db.get_rows(HISTORY_REQUEST)
        options['options1'] = format_docs_options(result, options['options1'])
    except Exception as error:
        logger.error('Error to rewrite query history: {}'.format((str(error))))
    if total_items > 0:
        total_pages = max(ceil(total_items / PAGE_SIZE), 1)
        first_page_data = raw_results[:PAGE_SIZE]
    else:
        total_pages = 0
        first_page_data = []
    return {
        "current_page": 1,
        "total_pages": total_pages,
        "unique_request_id": unique_request_id,
        "data": first_page_data
    }


@app.get("/paged_data/")
async def paged_data(unique_request_id: str, page: int = Query(1, ge=1)):
    if unique_request_id not in cached_search_results or len(cached_search_results[unique_request_id]) == 0:
        return {"detail": "Нет сохранённых результатов поиска"}
    all_results = cached_search_results[unique_request_id]
    total_items = len(all_results)
    result = paginator(page, all_results, PAGE_SIZE)
    return {
        "current_page": page,
        "total_pages": ceil(total_items / PAGE_SIZE),
        "unique_request_id": unique_request_id,
        "data": result
    }


@app.get("/config", response_class=HTMLResponse)
async def config_page(request: Request, config=Depends(load_path)):
    initial_config = load_state()
    config = initial_config.copy()
    return templates.TemplateResponse("config.html",  {"request": request, "config": config})


@app.post("/config",response_class=HTMLResponse)
async def process_form(dbName: str = Form(...), dbUser: str = Form(...), dbPassword: str = Form(...),
                       dbPort: str = Form(...), dbHost: str = Form(...), docPath: str = Form()):
    # global config
    config = initial_config.copy()
    try:
        user_data = User(dbName=dbName, dbUser=dbUser, dbPassword=dbPassword, dbPort=dbPort, dbHost=dbHost, docPath=docPath)
        config = user_data.model_copy()
        res = user_data.model_dump()
        save_state(res)
        return RedirectResponse('/config?status=success', status_code=303)
    except Exception as error:
        logger.error('Error for change config: {}'.format(str(error)))
        return {'detail': 'Ошибка при сохранении данных'}


@app.get("/get_options")
async def get_options():
    return options


@app.get("/doc/{filename:path}", include_in_schema=False)
async def serve_pdf(filename: str, config=Depends(load_path)):
    """
    Роут для отправки PDF-документа пользователю.
    :param filename: Имя файла, расположенного в DOCUMENT_DIR
    :return: Файл в виде response
    """
    DOCUMENT_DIR = config['docPath']
    full_path = path.join(DOCUMENT_DIR, filename + ".pdf") 
    if not path.isfile(full_path):
        raise HTTPException(status_code=404, detail='Файл "{}" не найден.'.format(filename))
    
    headers = {"Content-Type": "application/pdf",
               "Content-Disposition": "inline; filename={}".format(path.basename(filename)),
              }
    return FileResponse(path=full_path, media_type="application/pdf", headers=headers)


@app.route('/link/<path:filename>', methods=['GET'])
def serve_path(filename):
    BASE_URL = config['docPath']
    external_base_url = "http://searchplatform.fips.rospat/doc/"
    doc_id = filename[:-9]
    try:
        final_url = external_base_url + filename
        data_to_insert = [filename, datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), current_user_ip]
        query_idx = db.insert_list('docs_history', DOCS_FIELDS, data_to_insert)
        options['options2'].clear()
        result = db.get_rows(DOCS_HISTORY)
        options['options2'] = format_docs_options(result, options['options2'])
    except Exception as error:
        logger.error("Error in save docs history: {}".format(str(error)))
    return RedirectResponse(final_url)


app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)