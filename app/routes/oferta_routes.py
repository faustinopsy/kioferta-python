from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.controllers.oferta_controller import OfertaController
from app.models.erros import ConflitoError

router = APIRouter(prefix='/api', tags=['ofertas'])
controller = OfertaController()


class PublicarRequest(BaseModel):
    usuario_id: int
    produto_id: int
    mercado_id: int
    preco: float
    so_cartao: bool = False
    foto: str = ''


class ConfirmarRequest(BaseModel):
    usuario_id: int


@router.get('/ofertas/{id}')
def buscar(id: int):
    oferta = controller.buscar(id)
    if oferta is None:
        raise HTTPException(404, 'oferta não encontrada')
    return oferta


# Tela 9: a mesma rota, um comportamento por perfil
@router.post('/ofertas', status_code=201)
def publicar(dados: PublicarRequest):
    try:
        oferta = controller.publicar(dados.usuario_id, dados.produto_id, dados.mercado_id,
                                     dados.preco, dados.so_cartao, dados.foto)
    except PermissionError as erro:
        raise HTTPException(403, str(erro))
    except ValueError as erro:
        raise HTTPException(422, str(erro))
    if oferta is None:
        raise HTTPException(404, 'usuário, produto ou mercado não encontrado')
    return oferta


# Tela 3: "Confirmar este preço"
@router.post('/ofertas/{id}/confirmacoes')
def confirmar(id: int, dados: ConfirmarRequest):
    try:
        oferta = controller.confirmar(id, dados.usuario_id)
    except ConflitoError as erro:          # filha de ValueError: vem primeiro
        raise HTTPException(409, str(erro))
    except PermissionError as erro:
        raise HTTPException(403, str(erro))
    if oferta is None:
        raise HTTPException(404, 'oferta ou usuário não encontrado')
    return oferta


# Tela 10: minhas contribuições
@router.get('/usuarios/{id}/ofertas')
def do_autor(id: int):
    ofertas = controller.do_autor(id)
    if ofertas is None:
        raise HTTPException(404, 'usuário não encontrado')
    return ofertas
