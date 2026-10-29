from app.controllers.dicionarios import oferta_para_dicionario, produto_para_dicionario
from app.models.banco import banco as banco_da_api
from app.models.erros import ConflitoError
from app.models.produto import Produto


class ProdutoController:
    def __init__(self, banco=banco_da_api):
        self._banco = banco

    def semana(self):
        return dict(self._banco.semana)

    def categorias(self):
        return [dict(c) for c in self._banco.categorias]

    # Tela 2: filtra por texto e categoria, ordena por preço ou distância.
    def buscar_produtos(self, busca='', categoria='', ordem='preco', lat=None, lng=None):
        lat, lng = self._posicao(lat, lng)
        resumos = []
        for produto in self._banco.produtos:
            if categoria and not produto.pertence_a(categoria):
                continue
            if not produto.tem_no_nome(busca):
                continue
            resumo = self._resumir(produto, lat, lng)
            if resumo['ofertas']:                     # sem oferta ativa não aparece
                resumos.append(resumo)

        chave = 'mais_perto_km' if ordem == 'distancia' else 'menor_preco'
        ordenados = sorted(resumos, key=lambda resumo: resumo[chave])
        # na lista não vão as ofertas: só o resumo de cada produto
        return [{k: v for k, v in r.items() if k != 'ofertas'} for r in ordenados]

    # Tela 3: o resumo de decisão e as ofertas ativas, da mais barata.
    def resumo(self, id, lat=None, lng=None):
        produto = self._banco.produto(id)
        if produto is None:
            return None
        lat, lng = self._posicao(lat, lng)
        return self._resumir(produto, lat, lng)

    def por_codigo(self, codigo):
        numeros = Produto.limpar_codigo(codigo)        # formato errado: ValueError
        for produto in self._banco.produtos:
            if produto.tem_codigo(numeros):
                return produto_para_dicionario(produto)
        return None

    # Tela 9: produto que veio do Open Food Facts e ainda não estava no catálogo.
    def cadastrar(self, nome, categoria, codigo, imagem=''):
        if self.por_codigo(codigo) is not None:
            raise ConflitoError('já existe um produto com este código de barras')
        novo = Produto(self._banco.proximo_id(self._banco.produtos),
                       nome, categoria, codigo, imagem)
        self._banco.produtos.append(novo)
        return produto_para_dicionario(novo)

    # --- apoio ---
    def _posicao(self, lat, lng):
        if lat is None or lng is None:
            return self._banco.posicao_padrao['lat'], self._banco.posicao_padrao['lng']
        return lat, lng

    def _resumir(self, produto, lat, lng):
        ativas = [o for o in self._banco.ofertas
                  if o.e_do_produto(produto.mostrar_id()) and o.esta_ativa()]
        ordenadas = sorted(ativas, key=lambda o: o.mostrar_preco())
        resumo = {
            'produto': produto_para_dicionario(produto),
            'menor_preco': None,
            'maior_preco': None,
            'economia': 0,
            'mercados': 0,
            'mais_perto_km': None,
            'ofertas': [oferta_para_dicionario(o, lat, lng) for o in ordenadas],
        }
        if ordenadas:
            menor = ordenadas[0].mostrar_preco()
            maior = ordenadas[-1].mostrar_preco()
            resumo['menor_preco'] = menor
            resumo['maior_preco'] = maior
            resumo['economia'] = round(maior - menor, 2)
            resumo['mercados'] = len({o.mostrar_mercado().mostrar_id() for o in ordenadas})
            resumo['mais_perto_km'] = min(o.mostrar_mercado().distancia_ate(lat, lng)
                                          for o in ordenadas)
        return resumo
