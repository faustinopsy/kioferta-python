from app.data.mercados_mock import MERCADOS


class Mercado:
    """Um estabelecimento. Guarda a localização para o cálculo de distância."""

    def __init__(self, id, nome, curto, endereco, bairro, lat, lng):
        self._id = id
        self.alterar_nome(nome, curto)
        self._endereco = endereco
        self._bairro = bairro
        self.alterar_localizacao(lat, lng)

    # --- leitura ---
    def mostrar_id(self):
        return self._id

    def mostrar_nome(self):
        return self._nome

    def mostrar_curto(self):
        return self._curto

    def mostrar_endereco(self):
        return self._endereco

    def mostrar_bairro(self):
        return self._bairro

    def mostrar_localizacao(self):
        return (self._lat, self._lng)

    # --- alteração, com regra ---
    def alterar_nome(self, novo_nome, curto):
        if novo_nome.strip() == '':
            raise ValueError('nome não pode ser vazio')
        self._nome = novo_nome.strip()
        self._curto = curto.strip() or self._nome   # nome curto, para as listas

    def alterar_localizacao(self, lat, lng):
        if not (-90 <= lat <= 90):
            raise ValueError('latitude precisa estar entre -90 e 90')
        if not (-180 <= lng <= 180):
            raise ValueError('longitude precisa estar entre -180 e 180')
        self._lat = lat
        self._lng = lng

    # --- comportamento ---
    def distancia_ate(self, lat, lng):
        """Aproximação plana em km, suficiente para distâncias curtas."""
        dy = (self._lat - lat) * 111
        dx = (self._lng - lng) * 111 * 0.92
        return round((dx ** 2 + dy ** 2) ** 0.5, 2)

    def __repr__(self):
        return f'Mercado({self._nome})'


def carregar_mercados():
    return [Mercado(m['id'], m['nome'], m['curto'], m['endereco'], m['bairro'],
                    m['lat'], m['lng'])
            for m in MERCADOS]
