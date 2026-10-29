from fastapi import APIRouter

from app.controllers.produto_controller import ProdutoController

router = APIRouter(prefix='/api', tags=['catálogo'])
controller = ProdutoController()


@router.get('/semana')
def semana():
    return controller.semana()


@router.get('/categorias')
def categorias():
    return controller.categorias()
