from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from services.coin import list_coins

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    coins = list_coins()
    return templates.TemplateResponse(
        request=request, 
        name="index.html",
        context={"coins": coins}
    )