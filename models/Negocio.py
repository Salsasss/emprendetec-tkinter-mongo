class Negocio:
    columnas = ["Nombre", "Categoria", "Requiere Electricidad", "Activo", "Acciones"]
    campos = ["nombre", "categoria", "requiere_electricidad", "esta_activo"]
    
    def __init__(self, datos):
        self.id = datos.get('_id', '')
        self.nombre = datos.get('nombre', '')
        self.categoria = datos.get('categoria', '')
        self.requiere_electricidad = datos.get('requiere_electricidad', '')
        self.alumnos = datos.get('alumnos', '')
        self.fecha_creacion = datos.get('fecha_creacion', '')
        self.esta_activo = datos.get('esta_activo', '')
       
    def __str__(self):
        return f'{self.id} - {self.nombre}'