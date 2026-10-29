# KiOferta API — repositório modelo

Backend de referência da disciplina de **Programação Orientada a Objetos**.
Quatro camadas, padrão **MVC**, FastAPI, **sem banco de dados**: tudo fica em
listas na memória até a API reiniciar.

Atende as **onze telas** do app KiOferta (disciplina de Dispositivos Móveis):
cada rota existe porque uma tela precisa dela.

---

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux e macOS

pip install -r requirements.txt
uv run fastapi dev

```

Abra `http://127.0.0.1:8000/docs`. Precisa de **Python 3.10 ou mais novo** (por causa do `match`).

## Verificar

```bash
python verificar.py        # 91 checagens nas models e controllers, sem subir a API
python testar_rotas.py     # 62 checagens nas 19 rotas
```

---

## Estrutura

```
kioferta-python/
├── main.py                  liga os módulos à aplicação
├── verificar.py             testa models e controllers
├── testar_rotas.py          testa as rotas
└── app/
    ├── data/                dados provisórios (mock): só dicionários
    │   ├── produtos_mock.py     CATEGORIAS e PRODUTOS
    │   ├── mercados_mock.py     MERCADOS e POSICAO_PADRAO
    │   ├── usuarios_mock.py
    │   ├── ofertas_mock.py
    │   └── semana_mock.py
    ├── models/              M — classes e regras
    │   ├── produto.py           Produto + carregar_produtos()
    │   ├── mercado.py           Mercado + distancia_ate()
    │   ├── oferta.py            Oferta + votação + carregar_ofertas()
    │   ├── usuario.py           Usuario + 3 filhas + PERFIS + roteiros
    │   ├── erros.py             ConflitoError (vira 409)
    │   └── banco.py             o "banco": os objetos na memória
    ├── controllers/         C — casos de uso, um por assunto
    │   ├── dicionarios.py       objeto -> dicionário (e o motivo com match)
    │   ├── produto_controller.py
    │   ├── mercado_controller.py
    │   ├── oferta_controller.py
    │   └── usuario_controller.py
    └── routes/              V — endereços HTTP e códigos de resposta
        ├── catalogo_routes.py
        ├── produto_routes.py
        ├── mercado_routes.py
        ├── oferta_routes.py
        ├── usuario_routes.py
        └── moderacao_routes.py
```

A dependência aponta só para baixo: `main → routes → controllers → models → data`.

**Teste prático:** abra qualquer arquivo de `models/` ou `controllers/`.
Se aparecer `fastapi`, `HTTPException` ou `router`, a camada foi violada.

---

## Sem banco de dados: `models/banco.py`

```python
class Banco:
    def __init__(self):
        self.produtos = carregar_produtos()
        self.mercados = carregar_mercados()
        self.usuarios = carregar_usuarios()
        self.ofertas = carregar_ofertas(self.produtos, self.mercados, self.usuarios)

banco = Banco()          # a instância única que a API usa
```

- Os objetos são carregados **uma vez** e todos os controllers usam a mesma
  instância. Por isso, a oferta publicada pela tela 9 já aparece na busca da tela 2.
- A oferta recebe as listas já carregadas e liga os ids aos objetos (o JOIN).
- Os testes criam o próprio `Banco()`, para um teste não mexer no outro:
  `ProdutoController(Banco())`.
- Na aula de persistência, o `Banco` dá lugar a um banco de verdade e os
  controllers não mudam.

---

## Quem decide o quê

| Pergunta | Camada | Como |
|---|---|---|
| O código de barras tem 8 ou 13 números? | model | `raise ValueError` → 422 |
| Este perfil pode publicar? | model | `raise PermissionError` → 403 |
| Já confirmou este preço? | model | `raise ConflitoError` → 409 |
| O produto 99 existe? | controller | devolve `None` → 404 |
| Em que ordem as ofertas saem? | controller | `sorted` com `key` |
| Que código HTTP responder? | routes | `except` na ordem certa |

### A ordem dos `except` importa

`ConflitoError` é filha de `ValueError`. Se o `except ValueError` vier antes,
ele captura o conflito também e a resposta sai 422 em vez de 409.

```python
try:
    oferta = controller.confirmar(id, dados.usuario_id)
except ConflitoError as erro:          # filha de ValueError: vem primeiro
    raise HTTPException(409, str(erro))
except PermissionError as erro:
    raise HTTPException(403, str(erro))
```

---

## Herança e polimorfismo: a mesma chamada, um comportamento por perfil

```python
class Usuario:
    def publicar(self, id, produto, mercado, preco, so_cartao=False, foto=''):
        self._validar('enviar_oferta')                     # passo
        return Oferta(id, produto, mercado, preco, self,
                      status=self.status_inicial())        # passo

    def status_inicial(self):
        if self._reputacao >= REPUTACAO_SEM_VOTACAO:       # 200 pontos
            return 'aprovada'
        return 'votacao'

class Visitante(Usuario):            # só consulta
class Contribuidor(Visitante):       # + enviar_oferta, confirmar_oferta
class Moderador(Contribuidor):       # + moderar_contas
    def status_inicial(self):
        return 'aprovada'
```

| Quem | Permissões | A oferta nasce |
|---|---|---|
| Visitante | ver_ofertas | — (403) |
| Contribuidor com menos de 200 | + enviar e confirmar | `votacao` |
| Contribuidor com 200 ou mais | + enviar e confirmar | `aprovada` |
| Moderador | + moderar_contas | `aprovada` |
| Qualquer conta `pendente` | — | — (403: conta em análise) |

Os roteiros `publicar`, `confirmar` e `decidir` ficam na base e **nenhuma filha
os reescreve**: elas trocam só o passo (`mostrar_permissoes`, `status_inicial`).
Nenhum `if` pergunta o perfil nas models e nos controllers.

## `match/case` na moderação e no motivo

```python
def decidir(self, conta, acao):
    self._validar('moderar_contas')
    match acao:
        case 'aprovar':
            conta.aprovar()
        case 'recusar':
            conta.recusar()
        case _:
            raise ValueError("a ação precisa ser 'aprovar' ou 'recusar'")
```

O mesmo padrão escreve o motivo de cada contribuição (tela 10), em
`controllers/dicionarios.py`.

## A votação

- Toda oferta de contribuidor com menos de 200 pontos nasce `votacao`.
- Cada confirmação de **outra pessoa** soma 1. Com **3**, vira `aprovada`.
- Ninguém confirma a própria oferta (403), nem duas vezes (409).
- Uma oferta aprovada rende 4 pontos, mais 1 por confirmação.

---

## As 19 rotas

| Tela | Verbo | Endereço | Respostas |
|---|---|---|---|
| 1 | GET | `/api/semana` | 200 |
| 1 | GET | `/api/categorias` | 200 |
| 2 | GET | `/api/produtos?busca=café&categoria=Mercearia&ordem=distancia` | 200, 422 |
| 3 | GET | `/api/produtos/{id}` | 200, 404 |
| 9 | GET | `/api/produtos/codigo/{codigo}` | 200, 404, 422 |
| 9 | POST | `/api/produtos` | 201, 409, 422 |
| 4 | GET | `/api/mercados` | 200 |
| 5 | GET | `/api/mercados/{id}` | 200, 404 |
| 5 | GET | `/api/mercados/{id}/ofertas` | 200, 404 |
| 4 | GET | `/api/mapa?produto_id=1` | 200 |
| 3 | GET | `/api/ofertas/{id}` | 200, 404 |
| 9 | POST | `/api/ofertas` | 201, 403, 404, 422 |
| 3 | POST | `/api/ofertas/{id}/confirmacoes` | 200, 403, 404, 409 |
| 10 | GET | `/api/usuarios/{id}/ofertas` | 200, 404 |
| 7 | POST | `/api/login` | 200, 401, 422 |
| 7 | POST | `/api/usuarios` | 201, 409, 422 |
| 8 e 10 | GET | `/api/usuarios/{id}` | 200, 404 |
| 11 | GET | `/api/moderacao/contas?moderador_id=2` | 200, 403, 404 |
| 11 | PATCH | `/api/moderacao/contas/{id}` | 200, 403, 404, 409, 422 |

As rotas de busca, mapa e mercado aceitam `lat` e `lng`. Sem eles, a distância
é calculada a partir da `POSICAO_PADRAO` (o GPS do app entra depois).

### Exemplos

```
POST /api/ofertas
{ "usuario_id": 1, "produto_id": 10, "mercado_id": 5, "preco": 5.49 }

201 { "id": 52, "preco": 5.49, "status": "votacao",
      "motivo": "0 de 3 confirmações", ... }
```

```
PATCH /api/moderacao/contas/6
{ "moderador_id": 2, "acao": "aprovar" }

200 { "id": 6, "nome": "Juliana Prado Fonseca", "status": "aprovado", ... }
```

A senha nunca aparece na resposta. Não existe `mostrar_senha`.

### Sem login de verdade, por enquanto

Quem faz a ação manda o próprio id no corpo (`usuario_id`, `moderador_id`).
Token e sessão ficam para depois: o assunto aqui é a orientação a objetos.

---

## Contas de teste

| E-mail | Senha | Perfil | Situação |
|---|---|---|---|
| marina@kioferta.com | marina123 | contribuidor | 128 pontos: vai para votação |
| rafael@kioferta.com | rafael123 | contribuidor | 212 pontos: publica direto |
| bruna@kioferta.com | bruna123 | contribuidor | 86 pontos |
| caio@kioferta.com | caio1234 | moderador | publica direto e modera |
| marcos@email.com | marcos123 | contribuidor | pendente |
| juliana@email.com | juliana123 | contribuidor | pendente |
| sandro@email.com | sandro123 | contribuidor | pendente |

---

## Erros comuns

| Sintoma | Causa | Correção |
|---|---|---|
| `ModuleNotFoundError: app` | rodou de dentro de uma subpasta | `uvicorn` a partir da raiz |
| `SyntaxError` no `match` | Python antigo | use 3.10 ou mais novo |
| a oferta publicada não aparece na busca | controller criou o próprio `Banco()` | use o `banco` de `models/banco.py` |
| 409 saiu como 422 | `except ValueError` antes do `ConflitoError` | a filha vem primeiro |
| `/api/produtos?ordem=nome` dá 422 | `ordem` é `Literal['preco', 'distancia']` | o FastAPI valida sozinho |
| `Unable to serialize` | devolveu o objeto | use as funções de `dicionarios.py` |
