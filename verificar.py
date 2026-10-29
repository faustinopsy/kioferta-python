"""Verificação do modelo de referência.

Roda sem subir a API: testa as models e os controllers.
Cada bloco cria um Banco novo, para um teste não mexer no outro.
Use este arquivo como molde para verificar o seu próprio projeto.
"""
from app.models.banco import Banco
from app.models.erros import ConflitoError
from app.models.mercado import Mercado
from app.models.oferta import Oferta
from app.models.produto import Produto
from app.models.usuario import Contribuidor, Moderador, Usuario, Visitante
from app.controllers.produto_controller import ProdutoController
from app.controllers.mercado_controller import MercadoController
from app.controllers.oferta_controller import OfertaController
from app.controllers.usuario_controller import UsuarioController

falhas = 0


def checar(ok, descricao):
    global falhas
    print(('  ok      ' if ok else '  FALHOU  ') + descricao)
    if not ok:
        falhas += 1


def levanta(erro, funcao):
    """Devolve True se funcao() levantar a exceção esperada."""
    try:
        funcao()
    except erro:
        return True
    return False


b = Banco()
cafe, andorinha = b.produto(1), b.mercado(1)
marina, caio, rafael, juliana = b.usuario(1), b.usuario(2), b.usuario(3), b.usuario(6)

print('\n1. Encapsulamento: o objeto nasce válido')
checar(levanta(ValueError, lambda: Produto(99, 'X', 'Mercearia', '7891234567890')), 'recusa nome curto')
checar(levanta(ValueError, lambda: Produto(99, 'Arroz', 'Mercearia', '123')), 'recusa código sem 8 ou 13 números')
checar(levanta(ValueError, lambda: Produto(99, 'Arroz', 'Brinquedos', '7891234567890')), 'recusa categoria que não existe')
checar(Produto(99, 'Arroz', 'Mercearia', '789 1234-567890').mostrar_codigo() == '7891234567890',
       'limpa traço e espaço do código')
checar(levanta(ValueError, lambda: Mercado(99, 'X', 'X', 'r', 'b', 500, 0)), 'recusa latitude inválida')
checar(levanta(ValueError, lambda: Oferta(99, cafe, andorinha, 0, marina)), 'recusa preço zero')
checar(levanta(ValueError, lambda: Contribuidor(99, 'Ana', 'ana@x.com', '123', 'JF')), 'recusa senha curta')
checar(levanta(ValueError, lambda: Contribuidor(99, 'Ana', 'ana.x.com', '12345678', 'JF')), 'recusa e-mail sem @')
checar(not hasattr(Usuario, 'mostrar_senha'), 'não existe mostrar_senha')
checar(not hasattr(Produto, 'alterar_id') and not hasattr(Produto, 'alterar_codigo'),
       'id e código não mudam')

print('\n2. Associação: a oferta guarda objetos, não ids')
primeira = b.oferta(1)
checar(primeira.mostrar_produto() is cafe, 'guarda o mesmo objeto Produto')
checar(primeira.mostrar_mercado() is andorinha, 'guarda o mesmo objeto Mercado')
checar(primeira.mostrar_autor() is marina, 'guarda o mesmo objeto Usuario (o autor)')

print('\n3. Herança: a cadeia e a ordem de busca (MRO)')
checar(Moderador.__mro__[:4] == (Moderador, Contribuidor, Visitante, Usuario),
       'MRO: Moderador, Contribuidor, Visitante, Usuario')
checar(type(marina) is Contribuidor and type(caio) is Moderador, 'o mock virou classes diferentes')

print('\n4. Polimorfismo: a mesma chamada, respostas diferentes')
visitante = Visitante(90, 'Bia', 'bia@x.com', '12345678', 'JF', status='aprovado')
checar(len(visitante.mostrar_permissoes()) == 1, 'Visitante: 1 permissão')
checar(len(marina.mostrar_permissoes()) == 3, 'Contribuidor: 3 permissões')
checar(len(caio.mostrar_permissoes()) == 4, 'Moderador: 4 permissões')
checar(marina.status_inicial() == 'votacao', 'Contribuidor com 128 pontos: votação')
checar(rafael.status_inicial() == 'aprovada', 'Contribuidor com 212 pontos: direto')
checar(caio.status_inicial() == 'aprovada', 'Moderador: sempre direto')

print('\n5. Os roteiros ficam na base: nenhuma filha reescreve')
for classe in (Visitante, Contribuidor, Moderador):
    for roteiro in ('publicar', 'confirmar', 'decidir'):
        checar(roteiro not in classe.__dict__, f'{classe.__name__} não reescreve {roteiro}')
checar('status_inicial' in Moderador.__dict__ and 'status_inicial' not in Contribuidor.__dict__,
       'só o Moderador troca o passo status_inicial')

print('\n6. Publicar: a mesma chamada, três comportamentos')
checar(levanta(PermissionError, lambda: visitante.publicar(200, cafe, andorinha, 12.0)),
       'Visitante é barrado')
checar(levanta(PermissionError, lambda: juliana.publicar(201, cafe, andorinha, 12.0)),
       'conta pendente é barrada')
checar(marina.publicar(202, cafe, andorinha, 12.0).mostrar_status() == 'votacao',
       'Marina publica em votação')
checar(caio.publicar(203, cafe, andorinha, 12.0).mostrar_status() == 'aprovada',
       'Caio publica aprovada')

print('\n7. Confirmar: regras da votação')
em_votacao = b.oferta(4)                       # 1 de 3 confirmações
checar(levanta(PermissionError, lambda: marina.confirmar(primeira)),
       'ninguém confirma a própria oferta')
marina.confirmar(em_votacao)
checar(em_votacao.mostrar_confirmacoes() == 2, 'a confirmação conta')
checar(levanta(ConflitoError, lambda: marina.confirmar(em_votacao)), 'não confirma duas vezes')
rafael.confirmar(em_votacao)
checar(em_votacao.mostrar_status() == 'aprovada', 'com 3 confirmações, a votação aprova')
checar(levanta(PermissionError, lambda: juliana.confirmar(b.oferta(2))), 'pendente não confirma')

print('\n8. Moderação com match/case')
marcos, sandro = b.usuario(5), b.usuario(7)
checar(levanta(PermissionError, lambda: marina.decidir(marcos, 'aprovar')), 'Contribuidor não modera')
caio.decidir(marcos, 'aprovar')
checar(marcos.esta_aprovado(), 'aprovar libera a conta')
checar(levanta(ConflitoError, lambda: caio.decidir(marcos, 'recusar')), 'pedido decidido não volta atrás')
checar(levanta(ValueError, lambda: caio.decidir(sandro, 'talvez')), "case _: ação inválida")
checar(issubclass(ConflitoError, ValueError), 'ConflitoError é filha de ValueError')

print('\n9. Controllers: o que as telas pedem')
b = Banco()
produtos = ProdutoController(b)
cafes = produtos.buscar_produtos(busca='cafe')
checar(len(cafes) == 5, 'busca sem acento acha os 5 cafés')
checar(cafes[0]['menor_preco'] == 12.89, 'ordenado pelo menor preço')
checar(produtos.buscar_produtos(busca='café', ordem='distancia')[0]['mais_perto_km'] == 0.9,
       'ordenado pela distância')
checar(len(produtos.buscar_produtos(categoria='Bebidas')) == 2, 'filtra a categoria')
checar(all(r['produto']['id'] != 16 for r in produtos.buscar_produtos()),
       'produto sem oferta ativa não aparece')
resumo = produtos.resumo(1)
checar((resumo['menor_preco'], resumo['economia'], resumo['mais_perto_km']) == (13.49, 5.5, 0.9),
       'resumo de decisão: 13,49 · 5,50 · 0,9 km')
checar([o['preco'] for o in resumo['ofertas']] == sorted(o['preco'] for o in resumo['ofertas']),
       'ofertas da mais barata para a mais cara')
checar(produtos.resumo(99) is None, 'produto inexistente devolve None')
checar(levanta(ConflitoError, lambda: produtos.cadastrar('Café', 'Mercearia', '7891234567890')),
       'código repetido é conflito')

mercados = MercadoController(b)
mapa = mercados.mapa()
checar(min(m['preco'] for m in mapa) == 1.99, 'mapa: menor preço da área 1,99')
checar(len(mercados.mapa(produto_id=1)) == 4, 'mapa do café: 4 mercados')
checar(mercados.ofertas_do_mercado(99) is None, 'mercado inexistente devolve None')

ofertas = OfertaController(b)
contribuicoes = ofertas.do_autor(1)
motivos = {o['status']: o['motivo'] for o in contribuicoes}
checar(motivos['votacao'] == '2 de 3 confirmações', 'motivo da votação')
checar(motivos['aprovada'].endswith('de reputação'), 'motivo da aprovada')
checar(motivos['rejeitada'].startswith('3 contestações'), 'motivo da rejeitada')
checar(motivos['expirada'] == 'fim da semana', 'motivo da expirada')
checar(ofertas.publicar(99, 1, 1, 10.0) is None, 'autor inexistente devolve None')

contas = UsuarioController(b)
checar(contas.login('MARINA@kioferta.com', 'marina123')['nome'] == 'Marina R.', 'login ignora maiúscula')
checar('senha' not in contas.login('marina@kioferta.com', 'marina123'), 'a senha não sai')
checar(contas.login('marina@kioferta.com', 'errada') is None, 'senha errada devolve None')
nova = contas.cadastrar('Ana Teste', 'ana@teste.com', 'segredo123', 'Juiz de Fora, MG')
checar(nova['status'] == 'pendente' and nova['perfil'] == 'contribuidor', 'conta nova nasce pendente')
checar(levanta(ConflitoError, lambda: contas.cadastrar('Ana', 'ana@teste.com', 'segredo123', 'JF')),
       'e-mail repetido é conflito')
checar([u['nome'] for u in contas.pendentes(2)][0] == 'Marcos Vinícius Alves',
       'pendentes: quem espera há mais tempo primeiro')
checar(levanta(PermissionError, lambda: contas.pendentes(1)), 'Contribuidor não vê o painel')

print('\n10. Camadas: nenhum FastAPI e nenhuma pergunta de tipo fora das rotas')
import pathlib
for pasta in ('models', 'controllers'):
    for arquivo in sorted(pathlib.Path('app', pasta).glob('*.py')):
        fonte = arquivo.read_text(encoding='utf-8')
        if not fonte.strip():
            continue
        checar('fastapi' not in fonte.lower() and 'HTTPException' not in fonte,
               f'{pasta}/{arquivo.name} não conhece o FastAPI')
        checar('isinstance' not in fonte and 'type(' not in fonte and "perfil() ==" not in fonte,
               f'{pasta}/{arquivo.name} não pergunta o tipo')

print()
print('TUDO CERTO. Agora suba a API e teste no /docs.' if falhas == 0
      else f'{falhas} verificação(ões) falharam.')
