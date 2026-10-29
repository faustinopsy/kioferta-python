"""O "banco de dados" desta fase: listas de objetos na memória.

Tudo é carregado uma vez, quando a API sobe. O que for criado ou alterado
fica aqui até a API reiniciar. Na aula de persistência, esta classe dá lugar
a um banco de verdade e os controllers nem percebem a troca.
"""
from app.data.mercados_mock import POSICAO_PADRAO
from app.data.produtos_mock import CATEGORIAS
from app.data.semana_mock import SEMANA
from app.models.mercado import carregar_mercados
from app.models.oferta import carregar_ofertas
from app.models.produto import carregar_produtos
from app.models.usuario import carregar_usuarios


class Banco:
    def __init__(self):
        self.semana = dict(SEMANA)
        self.categorias = [dict(c) for c in CATEGORIAS]
        self.posicao_padrao = dict(POSICAO_PADRAO)
        self.produtos = carregar_produtos()
        self.mercados = carregar_mercados()
        self.usuarios = carregar_usuarios()
        self.ofertas = carregar_ofertas(self.produtos, self.mercados, self.usuarios)

    # --- achar pelo id: devolve o objeto ou None ---
    def produto(self, id):
        return self._achar(self.produtos, id)

    def mercado(self, id):
        return self._achar(self.mercados, id)

    def usuario(self, id):
        return self._achar(self.usuarios, id)

    def oferta(self, id):
        return self._achar(self.ofertas, id)

    def proximo_id(self, lista):
        return max((item.mostrar_id() for item in lista), default=0) + 1

    @staticmethod
    def _achar(lista, id):
        for item in lista:
            if item.mostrar_id() == id:
                return item
        return None


# a instância única que a API usa; os testes podem criar a sua
banco = Banco()
