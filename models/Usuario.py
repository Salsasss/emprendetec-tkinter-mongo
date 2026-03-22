class Usuario:
    columnas = ["Nombre", "Correo", "Rol", "Activo", "Acciones"]
    campos = ["nombre", "primer_apellido", "segundo_apellido", "esta_activo"]
    
    def __init__(self, datos):
        self.id = datos.get('_id', '')
        self.nombre = datos.get('nombre', '')
        self.correo = datos.get('correo', '')
        self.password = datos.get('password', '')
        self.rol = datos.get('rol', '')
        self.fecha_creacion = datos.get('fecha_creacion', '')
        self.esta_activo = datos.get('esta_activo', '')

    def __str__(self):
        return f'{self.id} - {self.nombre} {self.rol}'