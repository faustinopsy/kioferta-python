from app.data.ofertas_mock import OFERTAS
from app.models.erros import ConflitoError

STATUS = ('votacao', 'aprovada', 'rejeitada', 'expirada')
STATUS_ATIVOS = ('votacao', 'aprovada')        # o que o público vê
CONFIRMACOES_PARA_APROVAR = 3


class Oferta:
    """O preço de um Produto em um Mercado, enviado por um Usuario.

    Associação: a oferta guarda os OBJETOS produto, mercado e autor, não os ids.
    """

    def __init__(self, id, produto, mercado, preco, autor, status='votacao',
                 horas_atras=0, confirmacoes=0, so_cartao=False, foto='',
                 motivo='', semana=''):
        self._id = id
        self._produto = produto
        self._mercado = mercado
        self._autor = autor
        self.alterar_preco(preco)
        self._definir_status(status)
        self._horas_atras = horas_atras
        self._confirmacoes = confirmacoes
        self._confirmado_por = []              # ids de quem já confirmou
        self._so_cartao = so_cartao
        self._foto = foto
        self._motivo = motivo
        self._semana = semana

    # --- leitura ---
    def mostrar_id(self):
        return self._id

    def mostrar_produto(self):
        return self._produto

    def mostrar_mercado(self):
        return self._mercado

    def mostrar_autor(self):
        return self._autor

    def mostrar_preco(self):
        return self._preco

    def mostrar_status(self):
        return self._status

    def mostrar_horas_atras(self):
        return self._horas_atras

    def mostrar_confirmacoes(self):
        return self._confirmacoes

    def mostrar_so_cartao(self):
        return self._so_cartao

    def mostrar_foto(self):
        return self._foto

    def mostrar_motivo(self):
        return self._motivo

    def mostrar_semana(self):
        return self._semana

    # --- alteração, com regra ---
    def alterar_preco(self, novo_preco):
        if not (0 < novo_preco < 10000):
            raise ValueError('preço precisa ser maior que zero, como está na etiqueta')
        self._preco = round(novo_preco, 2)

    def _definir_status(self, status):
        if status not in STATUS:
            raise ValueError(f'status precisa ser um de: {", ".join(STATUS)}')
        self._status = status

    # --- comportamento ---
    def esta_ativa(self):
        return self._status in STATUS_ATIVOS

    def e_do_produto(self, produto_id):
        return self._produto.mostrar_id() == produto_id

    def e_do_mercado(self, mercado_id):
        return self._mercado.mostrar_id() == mercado_id

    def e_do_autor(self, usuario_id):
        return self._autor.mostrar_id() == usuario_id

    def receber_confirmacao(self, usuario):
        """Mais uma pessoa viu o mesmo preço. Com 3, a votação aprova."""
        if not self.esta_ativa():
            raise ConflitoError('esta oferta não está mais ativa')
        if self.e_do_autor(usuario.mostrar_id()):
            raise PermissionError('a confirmação precisa vir de outra pessoa')
        if usuario.mostrar_id() in self._confirmado_por:
            raise ConflitoError('você já confirmou este preço')

        self._confirmado_por.append(usuario.mostrar_id())
        self._confirmacoes += 1
        if self._status == 'votacao' and self._confirmacoes >= CONFIRMACOES_PARA_APROVAR:
            self._status = 'aprovada'

    def pontos(self):
        """Uma oferta aprovada rende 4 pontos de reputação, mais 1 por confirmação."""
        return 4 + self._confirmacoes if self._status == 'aprovada' else 0

    def __repr__(self):
        return (f'Oferta({self._produto.mostrar_nome()} '
                f'no {self._mercado.mostrar_nome()})')


def carregar_ofertas(produtos, mercados, usuarios):
    """Transforma os ids do mock em referências para os objetos já carregados.

    É o que um banco de dados faria com um JOIN.
    """
    por_id = lambda lista: {item.mostrar_id(): item for item in lista}
    produtos, mercados, usuarios = por_id(produtos), por_id(mercados), por_id(usuarios)

    return [Oferta(o['id'], produtos[o['produto_id']], mercados[o['mercado_id']],
                   o['preco'], usuarios[o['autor_id']],
                   status=o['status'],
                   horas_atras=o['horas_atras'],
                   confirmacoes=o['confirmacoes'],
                   so_cartao=o['so_cartao'],
                   motivo=o.get('motivo', ''),
                   semana=o.get('semana', ''))
            for o in OFERTAS]
