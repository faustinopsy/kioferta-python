class ConflitoError(ValueError):
    """O pedido está bem escrito, mas bate de frente com o estado atual.

    Exemplos: confirmar duas vezes, decidir um pedido já decidido,
    cadastrar um e-mail que já existe. A rota responde 409.

    É filha de ValueError: por isso, na rota, o except dela vem PRIMEIRO.
    """
