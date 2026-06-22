import os
from fastapi import APIRouter

router = APIRouter()

@router.patch("/{id}/enable")
def enable(id: str):
    # TODO
    pass
    