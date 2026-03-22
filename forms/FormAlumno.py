from customtkinter import CTkToplevel, CTkLabel, CTkEntry, CTkButton, StringVar
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from datetime import datetime

class FormAlumno(CTkToplevel):
    def __init__(self, parent, on_close=None, objeto={}):
        super().__init__()
        self.title("Registrar Nuevo Alumno")
        self.on_close = on_close
        
        conexion = MongoClient("mongodb://localhost:27017/")
        db = conexion['emprendetec'] # Cluster
        
        # Collections
        self.db_alumnos = db['alumnos']
        
        self.no_control = StringVar()
        self.nombre = StringVar()
        self.primer_apellido = StringVar()
        self.segundo_apellido = StringVar()

        # Objeto para la opción de Editar
        self.alumno = None
        
        if objeto:  
            self.alumno = objeto
            self.no_control.set(self.alumno.id)
            self.nombre.set(self.alumno.nombre)
            self.primer_apellido.set(self.alumno.primer_apellido)
            self.segundo_apellido.set(self.alumno.segundo_apellido)
        
    def _init_interfaz(self):
        self.columnconfigure(1, weight=1)
        
        CTkLabel(self, text="Registrar Nuevo Alumno").grid(row=0, column=0, columnspan=2, padx=15, pady=10, sticky="w")
        
        # No Control
        CTkLabel(self, text="No. Control:").grid(row=1, column=0, padx=15, pady=10, sticky="w")
        CTkEntry(self, textvariable=self.no_control, justify="center").grid(row=1, column=1, padx=15, pady=10, sticky="ew")

        # Nombre
        CTkLabel(self, text="Nombre:").grid(row=2, column=0, padx=15, pady=10, sticky="w")
        CTkEntry(self, textvariable=self.nombre, justify="center").grid(row=2, column=1, padx=15, pady=10, sticky="ew")

        # Primer Apellido
        CTkLabel(self, text="Primer Apellido:").grid(row=3, column=0, padx=15, pady=10, sticky="w")
        CTkEntry(self, textvariable=self.primer_apellido, justify="center").grid(row=3, column=1, padx=15, pady=10, sticky="ew")

        # Segundo Apellido
        CTkLabel(self, text="Segundo Apellido:").grid(row=4, column=0, padx=15, pady=10, sticky="w")
        CTkEntry(self, textvariable=self.segundo_apellido, justify="center").grid(row=4, column=1, padx=15, pady=10, sticky="ew")

        # Botón guardar
        CTkButton(self, text="Guardar Alumno", command=self.guardar).grid(row=5, column=0, columnspan=2, pady=20)
    
    def _limpiar_form(self):
        self.no_control.set("")
        self.nombre.set("")
        self.primer_apellido.set("")
        self.segundo_apellido.set("")
    
    def guardar(self):
        if self.alumno:
            valores = {
                "nombre": self.nombre.get(),
                "primer_apellido": self.primer_apellido.get(),
                "segundo_apellido": self.segundo_apellido.get()    
            }
        else:
            valores = {
                "_id": self.no_control.get(),
                "nombre": self.nombre.get(),
                "primer_apellido": self.primer_apellido.get(),
                "segundo_apellido": self.segundo_apellido.get(),
                "fecha_creacion": datetime.utcnow(),
                "esta_activo": True,
            }
        
            if len(valores['_id']) != 8:
                print('Error: El formato del número de control es incorrecto')
                return
            
        if len(valores['nombre']) <= 0 or len(valores['nombre']) > 200:
            print('Error: El formato del Nombre es incorrecto')
            return
        
        if len(valores['primer_apellido']) <= 0 or len(valores['primer_apellido']) > 200:
            print('Error: El formato del Primer Apellido es incorrecto')
            return
        
        if len(valores['segundo_apellido']) <= 0 or len(valores['segundo_apellido']) > 200:
            print('Error: El formato del Segundo Apellido es incorrecto')
            return
        
        try: # Si se logró insertar el alumno
            if self.alumno: # Editando
                self.db_alumnos.update_one({'_id': self.alumno.id}, {'$set': valores})
            else: # Insertando
                self.db_alumnos.insert_one(valores)
            self._limpiar_form()
            self._cerrar()
            
        except PyMongoError as e:
            print("Error de MongoDB:")
            print(type(e))
            print(e)
        
    def _cerrar(self):
        if self.on_close:
            self.on_close()
        self.destroy()
    
    def desplegar(self):
        self._init_interfaz()
        self.mainloop()