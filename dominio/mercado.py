class Mercado:
    def __init__(self, id, nome, lat, lng):
        self._id = id
        self._nome = nome
        self._lat = lat
        self._lng = lng
    def mostrar_id(self):
        return self._id
    def mostrar_nome(self):
        return self._nome
    def mostrar_localizacao(self):
        return (self._lat, self._lng)
    def alterar_nome(self, novo_nome):
        if novo_nome.strip() == '':
            raise ValueError('nome não pode ser vazio')
        self._nome = novo_nome.strip()
    def alterar_localizacao(self, lat, lng):
        if not (-90 <= lat <= 90):
            raise ValueError('latitude entre -90 e 90')
        if not (-180 <= lng <= 180):
            raise ValueError('longitude entre -180 e 180')
        self._lat = lat
        self._lng = lng
    def __repr__(self):
        return f'Mercado({self._nome})'
