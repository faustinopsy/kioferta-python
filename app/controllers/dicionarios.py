"""Objeto -> dicionário. A API nunca devolve o objeto: devolve isto.

Fica num arquivo só porque vários controllers mostram os mesmos objetos
(a oferta aparece no produto, no mercado e nas contribuições).
"""
from app.models.oferta import CONFIRMACOES_PARA_APROVAR


def produto_para_dicionario(produto):
    return {
        'id': produto.mostrar_id(),
        'nome': produto.mostrar_nome(),
        'categoria': produto.mostrar_categoria(),
        'codigo': produto.mostrar_codigo(),
        'imagem': produto.mostrar_imagem(),
    }


def mercado_para_dicionario(mercado, lat, lng):
    lat_mercado, lng_mercado = mercado.mostrar_localizacao()
    return {
        'id': mercado.mostrar_id(),
        'nome': mercado.mostrar_nome(),
        'curto': mercado.mostrar_curto(),
        'endereco': mercado.mostrar_endereco(),
        'bairro': mercado.mostrar_bairro(),
        'lat': lat_mercado,
        'lng': lng_mercado,
        'distancia_km': mercado.distancia_ate(lat, lng),
    }


def usuario_para_dicionario(usuario):
    return {                                   # a senha nunca sai daqui
        'id': usuario.mostrar_id(),
        'nome': usuario.mostrar_nome(),
        'email': usuario.mostrar_email(),
        'cidade': usuario.mostrar_cidade(),
        'perfil': usuario.mostrar_perfil(),
        'status': usuario.mostrar_status(),
        'reputacao': usuario.mostrar_reputacao(),
        'desde': usuario.mostrar_desde(),
        'horas_pedido': usuario.mostrar_horas_pedido(),
        'permissoes': usuario.mostrar_permissoes(),
        'publica_direto': usuario.publica_direto(),
    }


def oferta_para_dicionario(oferta, lat, lng):
    autor = oferta.mostrar_autor()
    return {
        'id': oferta.mostrar_id(),
        'preco': oferta.mostrar_preco(),
        'status': oferta.mostrar_status(),
        'motivo': texto_do_motivo(oferta),
        'horas_atras': oferta.mostrar_horas_atras(),
        'confirmacoes': oferta.mostrar_confirmacoes(),
        'so_cartao': oferta.mostrar_so_cartao(),
        'foto': oferta.mostrar_foto(),
        'semana': oferta.mostrar_semana(),
        'pontos': oferta.pontos(),
        'produto': produto_para_dicionario(oferta.mostrar_produto()),
        'mercado': mercado_para_dicionario(oferta.mostrar_mercado(), lat, lng),
        'autor': {
            'id': autor.mostrar_id(),
            'nome': autor.mostrar_nome(),
            'reputacao': autor.mostrar_reputacao(),
        },
    }


def texto_do_motivo(oferta):
    """Estado sem motivo gera reclamação: cada status diz o porquê."""
    confirmacoes = oferta.mostrar_confirmacoes()
    match oferta.mostrar_status():
        case 'votacao':
            return f'{confirmacoes} de {CONFIRMACOES_PARA_APROVAR} confirmações'
        case 'aprovada':
            return f'{confirmacoes} confirmações · +{oferta.pontos()} de reputação'
        case 'rejeitada':
            return oferta.mostrar_motivo()
        case 'expirada':
            return 'fim da semana'
