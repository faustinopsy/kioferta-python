from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.catalogo_routes import router as catalogo_router
from app.routes.produto_routes import router as produto_router
from app.routes.mercado_routes import router as mercado_router
from app.routes.oferta_routes import router as oferta_router
from app.routes.usuario_routes import router as usuario_router
from app.routes.moderacao_routes import router as moderacao_router

app = FastAPI(title='KiOferta API', version='2.0')

# o app do celular roda em outra origem (localhost:5173, https://localhost):
# sem CORS liberado, o navegador bloqueia a resposta
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(catalogo_router)
app.include_router(produto_router)
app.include_router(mercado_router)
app.include_router(oferta_router)
app.include_router(usuario_router)
app.include_router(moderacao_router)


@app.get('/')
def raiz():
    return {'api': 'KiOferta', 'docs': '/docs'}

if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)