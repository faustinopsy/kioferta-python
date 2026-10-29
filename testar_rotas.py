"""Testa todas as rotas da API sem subir o servidor.

Precisa de: pip install httpx
"""
from fastapi.testclient import TestClient

from main import app

c = TestClient(app)
falhas = 0


def t(desc, resp, esperado, verif=None):
    global falhas
    ok = resp.status_code == esperado
    extra = ''
    if ok and verif:
        try:
            ok = verif(resp.json())
        except Exception as e:
            ok = False
            extra = f' ({e})'
    print(('  ok      ' if ok else '  FALHOU  ') + f'{desc} -> {resp.status_code}{extra}')
    if not ok:
        falhas += 1


print('\nCATÁLOGO')
t('GET   /api/semana', c.get('/api/semana'), 200, lambda j: j['inicio'] == '10/08')
t('GET   /api/categorias', c.get('/api/categorias'), 200, lambda j: len(j) == 6)

print('\nTELA 2 · BUSCA')
t('GET   /api/produtos', c.get('/api/produtos'), 200, lambda j: len(j) == 18)
t('GET   /api/produtos?busca=café', c.get('/api/produtos', params={'busca': 'café'}), 200,
  lambda j: len(j) == 5 and j[0]['menor_preco'] == 12.89 and 'ofertas' not in j[0])
t('GET   /api/produtos?busca=cafe&ordem=distancia',
  c.get('/api/produtos', params={'busca': 'cafe', 'ordem': 'distancia'}), 200,
  lambda j: j[0]['mais_perto_km'] == 0.9)
t('GET   /api/produtos?categoria=Bebidas', c.get('/api/produtos', params={'categoria': 'Bebidas'}),
  200, lambda j: len(j) == 2)
t('GET   /api/produtos?busca=xyz', c.get('/api/produtos', params={'busca': 'xyz'}), 200,
  lambda j: j == [])
t('GET   /api/produtos?ordem=nome', c.get('/api/produtos', params={'ordem': 'nome'}), 422)

print('\nTELA 3 · PRODUTO')
t('GET   /api/produtos/1', c.get('/api/produtos/1'), 200,
  lambda j: j['menor_preco'] == 13.49 and j['economia'] == 5.5 and len(j['ofertas']) == 4)
t('GET   /api/produtos/1 traz os sinais de confiança', c.get('/api/produtos/1'), 200,
  lambda j: j['ofertas'][0]['autor'] == {'id': 1, 'nome': 'Marina R.', 'reputacao': 128}
  and j['ofertas'][0]['mercado']['distancia_km'] == 0.9)
t('GET   /api/produtos/16 (sem oferta ativa)', c.get('/api/produtos/16'), 200,
  lambda j: j['ofertas'] == [] and j['menor_preco'] is None)
t('GET   /api/produtos/99', c.get('/api/produtos/99'), 404)
t('GET   /api/produtos/codigo/7891234567890', c.get('/api/produtos/codigo/7891234567890'), 200,
  lambda j: j['id'] == 1)
t('GET   /api/produtos/codigo/7894900011517', c.get('/api/produtos/codigo/7894900011517'), 404)
t('GET   /api/produtos/codigo/123', c.get('/api/produtos/codigo/123'), 422)

print('\nTELAS 4 e 5 · MAPA E MERCADO')
t('GET   /api/mercados', c.get('/api/mercados'), 200,
  lambda j: [m['distancia_km'] for m in j] == [0.9, 1.2, 1.7, 2.6, 3.4])
t('GET   /api/mercados/1', c.get('/api/mercados/1'), 200, lambda j: j['curto'] == 'Andorinha')
t('GET   /api/mercados/99', c.get('/api/mercados/99'), 404)
t('GET   /api/mercados/1/ofertas', c.get('/api/mercados/1/ofertas'), 200,
  lambda j: len(j) == 13 and j[0]['horas_atras'] <= j[-1]['horas_atras'])
t('GET   /api/mercados/99/ofertas', c.get('/api/mercados/99/ofertas'), 404)
t('GET   /api/mapa', c.get('/api/mapa'), 200, lambda j: len(j) == 5 and min(m['preco'] for m in j) == 1.99)
t('GET   /api/mapa?produto_id=1', c.get('/api/mapa', params={'produto_id': 1}), 200,
  lambda j: len(j) == 4 and min(m['preco'] for m in j) == 13.49)
t('GET   /api/mapa com outra posição', c.get('/api/mapa', params={'lat': -21.733, 'lng': -43.3403}),
  200, lambda j: j[0]['mercado']['curto'] == 'Bom Preço' and j[0]['mercado']['distancia_km'] == 0)

print('\nTELA 7 · CONTAS')
t('POST  /api/login marina', c.post('/api/login', json={'email': 'marina@kioferta.com', 'senha': 'marina123'}),
  200, lambda j: j['perfil'] == 'contribuidor' and not j['publica_direto'] and 'senha' not in j)
t('POST  /api/login caio', c.post('/api/login', json={'email': 'caio@kioferta.com', 'senha': 'caio1234'}),
  200, lambda j: j['perfil'] == 'moderador' and 'moderar_contas' in j['permissoes'])
t('POST  /api/login senha errada', c.post('/api/login', json={'email': 'marina@kioferta.com', 'senha': 'x'}), 401)
t('POST  /api/login sem campo', c.post('/api/login', json={'email': 'marina@kioferta.com'}), 422)
nova = {'nome': 'Ana Teste', 'email': 'ana@teste.com', 'senha': 'segredo123', 'cidade': 'São Paulo, SP'}
t('POST  /api/usuarios', c.post('/api/usuarios', json=nova), 201, lambda j: j['status'] == 'pendente')
t('POST  /api/usuarios e-mail repetido', c.post('/api/usuarios', json=nova), 409)
t('POST  /api/usuarios senha curta', c.post('/api/usuarios', json={**nova, 'email': 'b@b.com', 'senha': '123'}), 422)
t('GET   /api/usuarios/1', c.get('/api/usuarios/1'), 200, lambda j: j['reputacao'] == 128)
t('GET   /api/usuarios/99', c.get('/api/usuarios/99'), 404)

print('\nTELA 9 · PUBLICAR: a mesma rota, um comportamento por perfil')
pub = lambda u, p=10, m=5, preco=5.49: c.post('/api/ofertas', json={
    'usuario_id': u, 'produto_id': p, 'mercado_id': m, 'preco': preco})
t('POST  /api/ofertas marina (128)', pub(1), 201, lambda j: j['status'] == 'votacao')
t('POST  /api/ofertas rafael (212)', pub(3), 201, lambda j: j['status'] == 'aprovada')
t('POST  /api/ofertas caio (moderador)', pub(2), 201, lambda j: j['status'] == 'aprovada')
t('POST  /api/ofertas juliana (pendente)', pub(6), 403)
t('POST  /api/ofertas preço zero', pub(1, preco=0), 422)
t('POST  /api/ofertas produto 99', pub(1, p=99), 404)
t('POST  /api/ofertas sem campo', c.post('/api/ofertas', json={'usuario_id': 1}), 422)
t('GET   /api/produtos?busca=guaran já mostra o preço novo', c.get('/api/produtos', params={'busca': 'guaran'}),
  200, lambda j: j[0]['menor_preco'] == 5.49)
produto = {'nome': 'Refrigerante Coca-Cola 2 L', 'categoria': 'Bebidas', 'codigo': '7894900011517'}
t('POST  /api/produtos (veio do Open Food Facts)', c.post('/api/produtos', json=produto), 201,
  lambda j: j['codigo'] == '7894900011517')
t('POST  /api/produtos código repetido', c.post('/api/produtos', json=produto), 409)
t('POST  /api/produtos categoria inválida',
  c.post('/api/produtos', json={**produto, 'codigo': '12345678', 'categoria': 'X'}), 422)

print('\nTELA 3 · CONFIRMAR')
conf = lambda oferta, u: c.post(f'/api/ofertas/{oferta}/confirmacoes', json={'usuario_id': u})
t('POST  confirmar a própria oferta', conf(1, 1), 403)
t('POST  confirmar oferta 4 (1 de 3)', conf(4, 1), 200, lambda j: j['confirmacoes'] == 2)
t('POST  confirmar de novo', conf(4, 1), 409)
t('POST  terceira confirmação aprova', conf(4, 3), 200, lambda j: j['status'] == 'aprovada')
t('POST  confirmar oferta expirada', conf(43, 1), 409)
t('POST  confirmar oferta 999', conf(999, 1), 404)

print('\nTELA 10 · CONTRIBUIÇÕES')
t('GET   /api/usuarios/1/ofertas', c.get('/api/usuarios/1/ofertas'), 200,
  lambda j: j[0]['horas_atras'] == 0 and {o['status'] for o in j} >= {'votacao', 'aprovada', 'rejeitada', 'expirada'})
t('GET   /api/usuarios/99/ofertas', c.get('/api/usuarios/99/ofertas'), 404)

print('\nTELA 11 · MODERAÇÃO (match/case)')
t('GET   /api/moderacao/contas caio', c.get('/api/moderacao/contas', params={'moderador_id': 2}), 200,
  lambda j: [u['nome'] for u in j][:3] == ['Marcos Vinícius Alves', 'Juliana Prado Fonseca', 'Sandro Kühn'])
t('GET   /api/moderacao/contas marina', c.get('/api/moderacao/contas', params={'moderador_id': 1}), 403)
t('GET   /api/moderacao/contas 99', c.get('/api/moderacao/contas', params={'moderador_id': 99}), 404)
decidir = lambda conta, acao, mod=2: c.patch(f'/api/moderacao/contas/{conta}', json={'moderador_id': mod, 'acao': acao})
t('PATCH aprovar juliana', decidir(6, 'aprovar'), 200, lambda j: j['status'] == 'aprovado')
t('PATCH aprovar juliana de novo', decidir(6, 'recusar'), 409)
t('PATCH ação inválida', decidir(7, 'talvez'), 422)
t('PATCH marina tentando moderar', decidir(7, 'aprovar', mod=1), 403)
t('PATCH conta 99', decidir(99, 'aprovar'), 404)
t('POST  /api/ofertas juliana, agora aprovada', pub(6), 201, lambda j: j['status'] == 'votacao')

print('\nRAIZ E DOCS')
t('GET   /', c.get('/'), 200)
t('GET   /docs', c.get('/docs'), 200)

print()
print('TODAS AS ROTAS OK' if falhas == 0 else f'{falhas} falha(s)')
