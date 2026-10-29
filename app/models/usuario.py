from app.data.usuarios_mock import USUARIOS
from app.models.erros import ConflitoError
from app.models.oferta import Oferta

REPUTACAO_SEM_VOTACAO = 200
STATUS_DA_CONTA = ('pendente', 'aprovado', 'recusado')


class Usuario:
    """Classe base. As filhas mudam só o que podem fazer e como a oferta nasce."""

    def __init__(self, id, nome, email, senha, cidade, reputacao=0,
                 status='pendente', desde='', horas_pedido=0):
        self._id = id
        self.alterar_nome(nome)
        self.alterar_email(email)
        self._definir_senha(senha)
        self.alterar_cidade(cidade)
        self._reputacao = reputacao
        self._definir_status(status)
        self._desde = desde
        self._horas_pedido = horas_pedido

    # --- leitura ---
    def mostrar_id(self):
        return self._id

    def mostrar_nome(self):
        return self._nome

    def mostrar_email(self):
        return self._email

    def mostrar_cidade(self):
        return self._cidade

    def mostrar_reputacao(self):
        return self._reputacao

    def mostrar_status(self):
        return self._status

    def mostrar_desde(self):
        return self._desde

    def mostrar_horas_pedido(self):
        return self._horas_pedido

    def mostrar_perfil(self):
        return self.__class__.__name__.lower()

    # não existe mostrar_senha: a senha só pode ser conferida
    def verificar_senha(self, senha):
        return self._senha == senha

    def esta_aprovado(self):
        return self._status == 'aprovado'

    # --- alteração, com regra ---
    def alterar_nome(self, novo_nome):
        if len(novo_nome.strip()) < 2:
            raise ValueError('digite o nome')
        self._nome = novo_nome.strip()

    def alterar_email(self, novo_email):
        email = novo_email.strip().lower()
        usuario, _, dominio = email.partition('@')
        if not usuario or '.' not in dominio or ' ' in email:
            raise ValueError('o e-mail precisa ter @ e domínio')
        self._email = email

    def alterar_cidade(self, nova_cidade):
        if nova_cidade.strip() == '':
            raise ValueError('digite a cidade')
        self._cidade = nova_cidade.strip()

    def _definir_senha(self, senha):
        if len(senha) < 8:
            raise ValueError('a senha precisa ter pelo menos 8 caracteres')
        self._senha = senha

    def _definir_status(self, status):
        if status not in STATUS_DA_CONTA:
            raise ValueError(f'status precisa ser um de: {", ".join(STATUS_DA_CONTA)}')
        self._status = status

    # --- a conta é decidida uma vez só ---
    def aprovar(self):
        self._decidir('aprovado')

    def recusar(self):
        self._decidir('recusado')

    def _decidir(self, novo_status):
        if self._status != 'pendente':
            raise ConflitoError('este pedido já foi decidido')
        self._status = novo_status

    # --- polimorfismo: cada filha responde do seu jeito ---
    def mostrar_permissoes(self):
        return []

    def pode(self, acao):
        return acao in self.mostrar_permissoes()

    def status_inicial(self):
        """Com reputação alta, a oferta não passa pela votação."""
        if self._reputacao >= REPUTACAO_SEM_VOTACAO:
            return 'aprovada'
        return 'votacao'

    def publica_direto(self):
        return self.status_inicial() == 'aprovada'

    # --- roteiros: ficam na base, nenhuma filha reescreve ---
    def publicar(self, id, produto, mercado, preco, so_cartao=False, foto=''):
        self._validar('enviar_oferta')
        return Oferta(id, produto, mercado, preco, self,
                      status=self.status_inicial(), so_cartao=so_cartao, foto=foto)

    def confirmar(self, oferta):
        self._validar('confirmar_oferta')
        oferta.receber_confirmacao(self)
        return oferta

    def decidir(self, conta, acao):
        self._validar('moderar_contas')
        match acao:
            case 'aprovar':
                conta.aprovar()
            case 'recusar':
                conta.recusar()
            case _:
                raise ValueError("a ação precisa ser 'aprovar' ou 'recusar'")
        return conta

    def _validar(self, acao):
        if not self.pode(acao):
            raise PermissionError(f'o perfil {self.mostrar_perfil()} não pode {acao}')
        if not self.esta_aprovado():
            raise PermissionError('a conta ainda está em análise')

    def __repr__(self):
        return f'{self.__class__.__name__}({self._nome})'


class Visitante(Usuario):
    """Quem só consulta. Nenhuma linha de regra: sem permissão, já é barrado."""

    def mostrar_permissoes(self):
        return ['ver_ofertas']


class Contribuidor(Visitante):
    def mostrar_permissoes(self):
        return super().mostrar_permissoes() + ['enviar_oferta', 'confirmar_oferta']


class Moderador(Contribuidor):
    def mostrar_permissoes(self):
        return super().mostrar_permissoes() + ['moderar_contas']

    def status_inicial(self):
        return 'aprovada'                      # a oferta do moderador entra aprovada


# o valor do dicionário é a própria CLASSE, não um texto
PERFIS = {
    'visitante': Visitante,
    'contribuidor': Contribuidor,
    'moderador': Moderador,
}


def carregar_usuarios():
    return [PERFIS[u['perfil']](u['id'], u['nome'], u['email'], u['senha'], u['cidade'],
                                reputacao=u['reputacao'], status=u['status'],
                                desde=u['desde'], horas_pedido=u['horas_pedido'])
            for u in USUARIOS]
