from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import re
import pymysql

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print('Request for index page received')
    return templates.TemplateResponse('index.html', {"request": request})

@app.get('/favicon.ico')
async def favicon():
    file_name = 'favicon.ico'
    file_path = './static/' + file_name
    return FileResponse(path=file_path, headers={'mimetype': 'image/vnd.microsoft.icon'})

@app.post('/hello', response_class=HTMLResponse)
async def hello(request: Request, name: str = Form(...)):
    if name:
        match= re.search(r"@([\w.-]+)", name)
        if match: 
            domain = match.group(1) 
            print('Request for hello page received with name=%s' % domain)
            connection = pymysql.connect(host="serverdivalto.mysql.database.azure.com",     user="newuser",     password="Azertyuiop123@", database="newtable", cursorclass=pymysql.cursors.DictCursor)
            try:
                with connection.cursor() as cursor:         # Execute raw SQL query
                    command = "SELECT idp_metadata_url FROM Domain_IdP_Mapping WHERE domain_suffix = %s;"
                    domain_suffix=domain
                    cursor.execute(command,(domain_suffix,)) 
                    result = cursor.fetchone()
                    url = result["idp_metadata_url"]
                    #return templates.TemplateResponse('hello.html', {"request": request, 'name':result["idp_metadata_url"]})
                    return RedirectResponse(url)
            finally: 
                connection.close() 
            #return templates.TemplateResponse('hello.html', {"request": request, 'name':domain})
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return RedirectResponse(request.url_for("index"), status_code=status.HTTP_302_FOUND)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)
