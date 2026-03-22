from models.Agenda import Agenda
from models.Ubicacion import Ubicacion

class Stand:
    def __init__(self, datos):
        self.id = datos.get('_id', '')
        if len(datos.get('agenda')) > 0:
            self.agenda = [Agenda(json) for json in datos.get('agenda', '')]
        else:
            self.agenda = {}
        
        if datos.get('ubicacion'):
            self.ubicacion = Ubicacion(datos.get('ubicacion', ''))
        else:
            self.ubicacion = {}
    def __str__(self):
        return f'{self.id}: {self.ubicacion}'