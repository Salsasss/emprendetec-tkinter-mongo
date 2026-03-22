from customtkinter import CTkToplevel, CTkLabel, CTkEntry, CTkCheckBox, CTkOptionMenu, CTkButton, CTkTextbox, StringVar, BooleanVar
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from datetime import datetime

from models.Alumno import Alumno

class FormNegocio(CTkToplevel):
    def __init__(self, parent, on_close=None, objeto={}):
        super().__init__()
        self.title("Registrar Nuevo Negocio")
        self.geometry('500x500')
        self.on_close = on_close
        
        conexion = MongoClient("mongodb://localhost:27017/")
        db = conexion['emprendetec'] # Cluster
        
        # Collections
        self.db_negocios = db['negocios']
        self.db_alumnos = db['alumnos']
        
        self.nombre = StringVar()
        self.categoria = StringVar()
        self.requiere_electricidad = BooleanVar(value=False)
        self.alumnos = []
        
        # Objeto para la opción de Editar
        self.negocio = None
        
        if objeto:
            self.negocio = objeto
            self.nombre.set(self.negocio.nombre)
            self.categoria.set(self.negocio.categoria)
            self.requiere_electricidad.set(self.negocio.requiere_electricidad)
        
    def _init_interfaz(self):
        self.columnconfigure(1, weight=1)
         
        CTkLabel(self, text="Registrar Nuevo Negocio").grid(row=0, column=0, columnspan=2, padx=15, pady=10, sticky="w")
        
        # Nombre
        CTkLabel(self, text="Nombre:").grid(row=1, column=0, padx=15, pady=10, sticky="w")
        CTkEntry(self, textvariable=self.nombre, justify="center").grid(row=1, column=1, padx=15, pady=10, sticky="ew")

        # Categoria
        CTkLabel(self, text="Categoria:").grid(row=2, column=0, padx=15, pady=10, sticky="w")
        CTkEntry(self, textvariable=self.categoria, justify="center").grid(row=2, column=1, padx=15, pady=10, sticky="ew")

        # Requiere Electricidad
        CTkCheckBox(self, text="Requiere Electricidad:", variable=self.requiere_electricidad).grid(row=3, column=0, columnspan=2, padx=15, pady=10, sticky="ew")

        # Alumnos
        CTkLabel(self, text="Agregar Emprendedor:").grid(row=4, column=0, padx=15, pady=10, sticky="w")
        self.option_menu = CTkOptionMenu(self)
        self.option_menu.grid(row=4, column=1, padx=15, pady=10, sticky="ew")
        self._consultar_alumnos()
        CTkButton(self, text="+", width=20, command=self._agregar_alumno).grid(row=4, column=2, padx=10, pady=20)
        
        # Alumnos Agregados
        self.txt_alumnos = CTkTextbox(master=self, width=20, state='disabled', corner_radius=0)
        self.txt_alumnos.grid(row=5, column=0, columnspan=3, sticky="ew")
        
        # Botón guardar
        CTkButton(self, text="Guardar Negocio", command=self.guardar).grid(row=6, column=0, columnspan=2, pady=20)
    
    def _consultar_alumnos(self):
        jsons_alumnos = self.db_alumnos.find(
            {"esta_activo": True, "_id": {"$nin": self.alumnos}}
        )
        alumnos = [Alumno(json) for json in jsons_alumnos]
        
        self.map_alumnos = {}
        valores = []

        for alumno in alumnos:
            texto = f"{alumno.id} - {alumno.nombre} {alumno.primer_apellido}"
            self.map_alumnos[texto] = alumno.id
            valores.append(texto)
            
        self.option_menu.configure(values=valores)
          
    def _agregar_alumno(self):
        value_combo = self.option_menu.get()
        alumno_id = self.map_alumnos[value_combo]
        
        self.txt_alumnos.configure(state="normal")
        self.txt_alumnos.insert("0.0", f'{value_combo} \n')
        self.txt_alumnos.configure(state="disabled")
        
        self.alumnos.append(alumno_id)
        self.option_menu.set("")
        self._consultar_alumnos()
    
    def _limpiar_form(self):
        self.nombre.set("")
        self.categoria.set("")
        self.requiere_electricidad.set(False)
    
    def guardar(self):
        if self.negocio:
            valores = {
                "nombre": self.nombre.get(),
                "categoria": str(self.categoria.get()).lower(),
                "requiere_electricidad": self.requiere_electricidad.get(),
            }
        else:
            valores = {
                "nombre": self.nombre.get(),
                "categoria": str(self.categoria.get()).lower(),
                "requiere_electricidad": self.requiere_electricidad.get(),
                "alumnos": self.alumnos,
                "fecha_creacion": datetime.utcnow(),
                "esta_activo": True,
            }
            
            if len(valores['alumnos']) == 0:
                print('Error: Almenos se debe registrar un Alumno en el negocio')
            return
        
        if len(valores['nombre']) <= 0 or len(valores['nombre']) > 200:
            print('Error: El formato del Nombre es incorrecto')
            return
        
        if len(valores['categoria']) <= 0 or len(valores['categoria']) > 200:
            print('Error: El formato la Categoria es incorrecto')
            return
        
        try: # Si se logró insertar el negocio
            if self.negocio: # Editando
                self.db_negocios.update_one({'_id': self.negocio.id}, {'$set': valores})
            else: # Insertando
                self.db_negocios.insert_one(valores)
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