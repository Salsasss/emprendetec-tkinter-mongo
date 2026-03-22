from pymongo import MongoClient

from models.Negocio import Negocio

class Agenda:
    
    def __init__(self, datos):
        conexion = MongoClient("mongodb://localhost:27017/")
        db = conexion['emprendetec'] # Cluster
        
        self.db_negocios = db['negocios']
        
        self.fecha = datos.get('fecha', '')
        self.negocio = self.get_negocio(datos.get('id_negocio', ''))
        self.esta_ocupado = datos.get('esta_ocupado', '')
        
    def get_negocio(self, id):
        json_encontrado = self.db_negocios.find_one(
            {'_id': id}
        )
        return Negocio(json_encontrado)
    
    def __str__(self):
        return f'{self.fecha} - {self.negocio.nombre}'