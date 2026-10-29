from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.controllers.usuario_controller import UsuarioController
from app.models.erros import ConflitoError

router = APIRouter(prefix='/api/moderacao', tags=['moderação'])
controller = UsuarioController()


class DecisaoRequest(BaseModel):
    moderador_id: int
    acao: str                              # 'aprovar' ou 'recusar'


# Tela 11: /api/moderacao/contas?moderador_id=2
@router.get('/contas')
def pendentes(moderador_id: int):
    try:
        contas = controller.pendentes(moderador_id)
    except PermissionError as erro:
        raise HTTPException(403, str(erro))
    if contas is None:
        raise HTTPException(404, 'moderador não encontrado')
    return contas


@router.patch('/contas/{id}')
def decidir(id: int, dados: DecisaoRequest):
    try:
        conta = controller.decidir(dados.moderador_id, id, dados.acao)
    except ConflitoError as erro:          # filha de ValueError: vem primeiro
        raise HTTPException(409, str(erro))
    except PermissionError as erro:
        raise HTTPException(403, str(erro))
    except ValueError as erro:
        raise HTTPException(422, str(erro))
    if conta is None:
        raise HTTPException(404, 'moderador ou conta não encontrado')
    return conta
