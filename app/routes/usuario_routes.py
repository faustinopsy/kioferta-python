from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.controllers.usuario_controller import UsuarioController
from app.models.erros import ConflitoError

router = APIRouter(prefix='/api', tags=['contas'])
controller = UsuarioController()


class LoginRequest(BaseModel):
    email: str
    senha: str


class CadastroRequest(BaseModel):
    nome: str
    email: str
    senha: str
    cidade: str


# Tela 7, aba Entrar
@router.post('/login')
def login(dados: LoginRequest):
    usuario = controller.login(dados.email, dados.senha)
    if usuario is None:
        raise HTTPException(401, 'e-mail ou senha não conferem')
    return usuario


# Tela 7, aba Criar conta
@router.post('/usuarios', status_code=201)
def cadastrar(dados: CadastroRequest):
    try:
        return controller.cadastrar(dados.nome, dados.email, dados.senha, dados.cidade)
    except ConflitoError as erro:          # filha de ValueError: vem primeiro
        raise HTTPException(409, str(erro))
    except ValueError as erro:
        raise HTTPException(422, str(erro))


# Telas 8 e 10: a situação da conta
@router.get('/usuarios/{id}')
def buscar(id: int):
    usuario = controller.buscar(id)
    if usuario is None:
        raise HTTPException(404, 'usuário não encontrado')
    return usuario
