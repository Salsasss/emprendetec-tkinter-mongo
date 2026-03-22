class Alumno:
    columnas = ["No Control", "Nombre", "Primer Apellido", "Segundo Apellido", "Activo", "Acciones"]
    campos = ["id", "nombre", "primer_apellido", "segundo_apellido", "esta_activo"]
    
    def __init__(self, datos):
        self.id = datos.get('_id', '')
        self.nombre = datos.get('nombre', '')
        self.primer_apellido = datos.get('primer_apellido', '')
        self.segundo_apellido = datos.get('segundo_apellido', '')
        self.fecha_creacion = datos.get('fecha_creacion', '')
        self.esta_activo = datos.get('esta_activo', '')

    def __str__(self):
        return f'{self.id} - {self.nombre} {self.primer_apellido} {self.segundo_apellido}'