from datetime import date

from app.controllers.dicionarios import usuario_para_dicionario
from app.models.banco import banco as banco_da_api
from app.models.erros import ConflitoError
from app.models.usuario import Contribuidor

MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho',
         'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']


class UsuarioController:
    def __init__(self, banco=banco_da_api):
        self._banco = banco

    # Tela 7, aba Entrar.
    def login(self, email, senha):
        for usuario in self._banco.usuarios:
            if usuario.mostrar_email() == email.strip().lower() and usuario.verificar_senha(senha):
                return usuario_para_dicionario(usuario)
        return None

    # Tela 7, aba Criar conta: quatro campos, a conta nasce pendente.
    def cadastrar(self, nome, email, senha, cidade):
        if any(u.mostrar_email() == email.strip().lower() for u in self._banco.usuarios):
            raise ConflitoError('este e-mail já tem conta')
        novo = Contribuidor(self._banco.proximo_id(self._banco.usuarios),
                            nome, email, senha, cidade, status='pendente',
                            desde=MESES[date.today().month - 1])
        self._banco.usuarios.append(novo)
        return usuario_para_dicionario(novo)

    def buscar(self, id):
        usuario = self._banco.usuario(id)
        if usuario is None:
            return None
        return usuario_para_dicionario(usuario)

    # Tela 11: quem espera há mais tempo aparece primeiro.
    def pendentes(self, moderador_id):
        moderador = self._banco.usuario(moderador_id)
        if moderador is None:
            return None
        if not moderador.pode('moderar_contas'):
            raise PermissionError(f'o perfil {moderador.mostrar_perfil()} não pode moderar_contas')
        pendentes = [u for u in self._banco.usuarios if u.mostrar_status() == 'pendente']
        ordenados = sorted(pendentes, key=lambda u: u.mostrar_horas_pedido(), reverse=True)
        return [usuario_para_dicionario(u) for u in ordenados]

    def decidir(self, moderador_id, conta_id, acao):
        moderador = self._banco.usuario(moderador_id)
        conta = self._banco.usuario(conta_id)
        if moderador is None or conta is None:
            return None
        moderador.decidir(conta, acao)
        return usuario_para_dicionario(conta)
