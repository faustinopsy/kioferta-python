from contribuidor import Contribuidor

class Moderador(Contribuidor):
    def pode_publicar(self):
        return True