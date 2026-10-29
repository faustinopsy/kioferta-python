import unicodedata

from app.data.produtos_mock import CATEGORIAS, PRODUTOS

NOMES_DAS_CATEGORIAS = [c['nome'] for c in CATEGORIAS]


def normalizar(texto):
    """'Café' -> 'cafe': compara sem acento e sem maiúscula."""
    sem_acento = unicodedata.normalize('NFD', texto)
    sem_acento = ''.join(letra for letra in sem_acento
                         if unicodedata.category(letra) != 'Mn')
    return sem_acento.lower().strip()


class Produto:
    """Um item do catálogo. O código de barras identifica o produto."""

    def __init__(self, id, nome, categoria, codigo, imagem=''):
        self._id = id
        self._codigo = Produto.limpar_codigo(codigo)   # identidade: não muda
        self.alterar_nome(nome)
        self.alterar_categoria(categoria)
        self._imagem = imagem

    # --- leitura ---
    def mostrar_id(self):
        return self._id

    def mostrar_nome(self):
        return self._nome

    def mostrar_categoria(self):
        return self._categoria

    def mostrar_codigo(self):
        return self._codigo

    def mostrar_imagem(self):
        return self._imagem

    # --- alteração, com regra ---
    def alterar_nome(self, novo_nome):
        if len(novo_nome.strip()) < 3:
            raise ValueError('nome do produto precisa ter pelo menos 3 letras')
        self._nome = novo_nome.strip()

    def alterar_categoria(self, nova_categoria):
        if nova_categoria not in NOMES_DAS_CATEGORIAS:
            raise ValueError(f'categoria precisa ser uma de: {", ".join(NOMES_DAS_CATEGORIAS)}')
        self._categoria = nova_categoria

    # --- comportamento ---
    @staticmethod
    def limpar_codigo(texto):
        """'789 1234-567890' -> '7891234567890'. Código tem 8 ou 13 números."""
        numeros = ''.join(letra for letra in str(texto) if letra.isdigit())
        if len(numeros) not in (8, 13):
            raise ValueError('o código de barras tem 8 ou 13 números')
        return numeros

    def pertence_a(self, categoria):
        return self._categoria.lower() == categoria.strip().lower()

    def tem_no_nome(self, termo):
        return normalizar(termo) in normalizar(self._nome)

    def tem_codigo(self, codigo):
        return self._codigo == codigo

    def __repr__(self):
        return f'Produto({self._nome})'


def carregar_produtos():
    return [Produto(p['id'], p['nome'], p['categoria'], p['codigo'], p['imagem'])
            for p in PRODUTOS]
