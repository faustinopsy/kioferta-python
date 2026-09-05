class Usuario:

    def __init__(self, id, nome):
        self._id = id
        self._nome = nome
        self._favoritos = []

    def mostrar_nome(self):
        return self._nome

    def favoritar(self, oferta):
        if oferta not in self._favoritos:
            self._favoritos.append(oferta)

    def mostrar_favoritos(self):
        return list(self._favoritos)

    def pode_publicar(self):
        return False

    def __repr__(self):
        return f'{type(self).__name__}({self._nome})'
