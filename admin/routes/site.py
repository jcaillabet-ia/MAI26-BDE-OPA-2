from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import requests

apiUrl = 'http://api:8000'

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    coins = requests.get(apiUrl + '/coin').json()
    
    return templates.TemplateResponse(
        request=request, 
        name="index.html",
        context={"coins": coins}
    )