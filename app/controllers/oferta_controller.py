from app.controllers.dicionarios import oferta_para_dicionario
from app.models.banco import banco as banco_da_api


class OfertaController:
    def __init__(self, banco=banco_da_api):
        self._banco = banco

    def buscar(self, id):
        oferta = self._banco.oferta(id)
        if oferta is None:
            return None
        return self._dicionario(oferta)

    # Tela 9. O controller não pergunta o perfil de ninguém:
    # autor.publicar decide sozinho se pode e como a oferta nasce.
    def publicar(self, usuario_id, produto_id, mercado_id, preco, so_cartao=False, foto=''):
        autor = self._banco.usuario(usuario_id)
        produto = self._banco.produto(produto_id)
        mercado = self._banco.mercado(mercado_id)
        if autor is None or produto is None or mercado is None:
            return None

        oferta = autor.publicar(self._banco.proximo_id(self._banco.ofertas),
                                produto, mercado, preco, so_cartao, foto)
        self._banco.ofertas.append(oferta)
        return self._dicionario(oferta)

    # Tela 3: "Confirmar este preço".
    def confirmar(self, oferta_id, usuario_id):
        oferta = self._banco.oferta(oferta_id)
        usuario = self._banco.usuario(usuario_id)
        if oferta is None or usuario is None:
            return None
        usuario.confirmar(oferta)
        return self._dicionario(oferta)

    # Tela 10: minhas contribuições, das mais recentes.
    def do_autor(self, usuario_id):
        if self._banco.usuario(usuario_id) is None:
            return None
        do_autor = [o for o in self._banco.ofertas if o.e_do_autor(usuario_id)]
        ordenadas = sorted(do_autor, key=lambda o: o.mostrar_horas_atras())
        return [self._dicionario(o) for o in ordenadas]

    def _dicionario(self, oferta):
        posicao = self._banco.posicao_padrao
        return oferta_para_dicionario(oferta, posicao['lat'], posicao['lng'])
