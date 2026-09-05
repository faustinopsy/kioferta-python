from usuario import Usuario

class Contribuidor(Usuario):
    def pode_publicar(self):
        return True