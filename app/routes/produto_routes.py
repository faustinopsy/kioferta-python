from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.controllers.produto_controller import ProdutoController
from app.models.erros import ConflitoError

router = APIRouter(prefix='/api/produtos', tags=['produtos'])
controller = ProdutoController()


class ProdutoRequest(BaseModel):
    nome: str
    categoria: str
    codigo: str
    imagem: str = ''


# Tela 2: /api/produtos?busca=café&categoria=Mercearia&ordem=distancia
@router.get('')
def buscar_produtos(busca: str = '', categoria: str = '',
                    ordem: Literal['preco', 'distancia'] = 'preco',
                    lat: float | None = None, lng: float | None = None):
    return controller.buscar_produtos(busca, categoria, ordem, lat, lng)


# Tela 9: o produto já está no catálogo? Formato errado é 422; não achou é 404.
@router.get('/codigo/{codigo}')
def por_codigo(codigo: str):
    try:
        produto = controller.por_codigo(codigo)
    except ValueError as erro:
        raise HTTPException(422, str(erro))
    if produto is None:
        raise HTTPException(404, 'nenhum produto com este código')
    return produto


# Tela 3: resumo de decisão e ofertas ativas
@router.get('/{id}')
def resumo(id: int, lat: float | None = None, lng: float | None = None):
    dados = controller.resumo(id, lat, lng)
    if dados is None:
        raise HTTPException(404, 'produto não encontrado')
    return dados


@router.post('', status_code=201)
def cadastrar(dados: ProdutoRequest):
    try:
        return controller.cadastrar(dados.nome, dados.categoria, dados.codigo, dados.imagem)
    except ConflitoError as erro:          # filha de ValueError: vem primeiro
        raise HTTPException(409, str(erro))
    except ValueError as erro:
        raise HTTPException(422, str(erro))
