class Ubicacion:
    def __init__(self, datos):
        self.zona = datos.get('zona', '')
        self.pasillo = datos.get('pasillo', '')
        self.numero_mesa = datos.get('numero_mesa', '')
        
    def __str__(self):
        return f'{self.zona}, {self.pasillo}, {self.numero_mesa}'