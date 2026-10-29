from fastapi import APIRouter, HTTPException

from app.controllers.mercado_controller import MercadoController

router = APIRouter(prefix='/api', tags=['mercados'])
controller = MercadoController()


@router.get('/mercados')
def listar(lat: float | None = None, lng: float | None = None):
    return controller.listar(lat, lng)


@router.get('/mercados/{id}')
def buscar(id: int, lat: float | None = None, lng: float | None = None):
    mercado = controller.buscar(id, lat, lng)
    if mercado is None:
        raise HTTPException(404, 'mercado não encontrado')
    return mercado


# Tela 5
@router.get('/mercados/{id}/ofertas')
def ofertas_do_mercado(id: int, lat: float | None = None, lng: float | None = None):
    ofertas = controller.ofertas_do_mercado(id, lat, lng)
    if ofertas is None:
        raise HTTPException(404, 'mercado não encontrado')
    return ofertas


# Tela 4: /api/mapa  ou  /api/mapa?produto_id=1
@router.get('/mapa')
def mapa(produto_id: int | None = None, lat: float | None = None, lng: float | None = None):
    return controller.mapa(produto_id, lat, lng)
