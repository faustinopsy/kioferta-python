from usuario import Usuario

class Visitante(Usuario):
    def __init__(self):
        super().__init__(0, 'Visitante')


