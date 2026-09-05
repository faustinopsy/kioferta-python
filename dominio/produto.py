class Produto:
    def __init__(self, id, nome, preco):
        self._id = id
        self._nome = nome
        self._preco = preco

    def mostrar_nome(self):
        pass

    def alterar_preco(self, novo_preco):
        if novo_preco < 0:
            raise ValueError('preço não pode ser negativo')
        self._preco = novo_preco

    def mostrar_preco(self):
        return self._preco
