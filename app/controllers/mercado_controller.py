from app.controllers.dicionarios import mercado_para_dicionario, oferta_para_dicionario
from app.models.banco import banco as banco_da_api


class MercadoController:
    def __init__(self, banco=banco_da_api):
        self._banco = banco

    def listar(self, lat=None, lng=None):
        lat, lng = self._posicao(lat, lng)
        ordenados = sorted(self._banco.mercados, key=lambda m: m.distancia_ate(lat, lng))
        return [mercado_para_dicionario(m, lat, lng) for m in ordenados]

    def buscar(self, id, lat=None, lng=None):
        mercado = self._banco.mercado(id)
        if mercado is None:
            return None
        lat, lng = self._posicao(lat, lng)
        return mercado_para_dicionario(mercado, lat, lng)

    # Tela 5: as promoções ativas do mercado, das mais recentes.
    def ofertas_do_mercado(self, id, lat=None, lng=None):
        if self._banco.mercado(id) is None:
            return None
        lat, lng = self._posicao(lat, lng)
        ativas = self._ativas_do_mercado(id)
        ordenadas = sorted(ativas, key=lambda o: o.mostrar_horas_atras())
        return [oferta_para_dicionario(o, lat, lng) for o in ordenadas]

    # Tela 4: um marcador por mercado. Com produto, o preço daquele produto;
    # sem produto, o menor preço de qualquer promoção do mercado.
    def mapa(self, produto_id=None, lat=None, lng=None):
        lat, lng = self._posicao(lat, lng)
        marcadores = []
        for mercado in sorted(self._banco.mercados, key=lambda m: m.distancia_ate(lat, lng)):
            ativas = self._ativas_do_mercado(mercado.mostrar_id())
            consideradas = [o for o in ativas
                            if produto_id is None or o.e_do_produto(produto_id)]
            if not consideradas:
                continue
            marcadores.append({
                'mercado': mercado_para_dicionario(mercado, lat, lng),
                'preco': min(o.mostrar_preco() for o in consideradas),
                'quantidade': len(ativas),
            })
        return marcadores

    # --- apoio ---
    def _ativas_do_mercado(self, id):
        return [o for o in self._banco.ofertas if o.e_do_mercado(id) and o.esta_ativa()]

    def _posicao(self, lat, lng):
        if lat is None or lng is None:
            return self._banco.posicao_padrao['lat'], self._banco.posicao_padrao['lng']
        return lat, lng
