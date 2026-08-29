from dominio.produto import Produto
from dominio.mercado import Mercado
from dominio.oferta import Oferta

# python não usa a palavra new para criar objetos
arroz = Produto(12, "Tio João", 23.50)
feijao = Produto(10, "carioca", 10.50 )
cafe = Produto(4, "Três corações", 13.60)
lista_de_produtos = [arroz, feijao, cafe]
for i in lista_de_produtos:
    print(f" Nome: {i._nome} e o preço é {i._preco} ")

resultado = cafe.alterar_preco(23.80)
print( f" Novo preço do café { cafe.mostrar_preco() }"  )