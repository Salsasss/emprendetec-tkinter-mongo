from tkinter import messagebox
from customtkinter import CTkToplevel, CTkLabel, CTkEntry, CTkCheckBox, CTkOptionMenu, CTkButton, CTkTextbox, StringVar, BooleanVar
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from datetime import datetime

from models.Alumno import Alumno

class FormNegocio(CTkToplevel):
    def __init__(self, parent, on_close=None, objeto={}):
        super().__init__()
        self.title("Registrar Nuevo Negocio")
        self.resizable(False, False)
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
        
        if objeto: # Editando
            self.negocio = objeto
            self.nombre.set(self.negocio.nombre)
            self.categoria.set(self.negocio.categoria)
            self.requiere_electricidad.set(self.negocio.requiere_electricidad)
            self.alumnos = self.negocio.alumnos
                    
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
        self.option_menu = CTkOptionMenu(self, command=self.revisar_seleccion)
        self.option_menu.set("Selecciona un Alumno...")
        self.option_menu.grid(row=4, column=1, padx=15, pady=10, sticky="ew")
        self._consultar_alumnos()

        self.btn_agregar = CTkButton(self, text="+", width=20, command=self._agregar_alumno, state='disabled')
        self.btn_agregar.grid(row=4, column=2, padx=10, pady=20)
        
        # Alumnos Agregados
        self.txt_alumnos = CTkTextbox(master=self, width=20, state='disabled', corner_radius=0)
        self.txt_alumnos.grid(row=5, column=0, columnspan=3, sticky="ew")
        
        if self.negocio: # Editando
            self._agregar_alumnos() # Llenar txt_alumnos con los alumnos registrados en el Negocio
        
        # Botón guardar
        CTkButton(self, text="Guardar Negocio", command=self.guardar).grid(row=6, column=0, columnspan=2, pady=20)
    
    def revisar_seleccion(self, e):
        self.btn_agregar.configure(state="normal")

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
        self.txt_alumnos.insert("0.0", f'{value_combo} \n', alumno_id)
        self.txt_alumnos.tag_bind(alumno_id, "<Double-Button-1>", lambda e, id=alumno_id: self._quitar_alumno(id))
        self.txt_alumnos.configure(state="disabled")
        
        self.alumnos.append(alumno_id)
        self.option_menu.set("Selecciona un Alumno...")
        self.btn_agregar.configure(state='disabled')
        self._consultar_alumnos()
        
    def _agregar_alumnos(self):
        for id_alumno in self.alumnos:
            json_alumno = self.db_alumnos.find(
                {"_id": id_alumno}
            )[0]
            alumno = Alumno(json_alumno)
                
            self.txt_alumnos.configure(state="normal")
            self.txt_alumnos.insert("0.0", f'{alumno.id} - {alumno.nombre} \n', alumno.id)
            self.txt_alumnos.tag_bind(alumno.id, "<Double-Button-1>", lambda e, id=alumno.id: self._quitar_alumno(id))
            self.txt_alumnos.configure(state="disabled")
        
    def _quitar_alumno(self, alumno_id):
        self.txt_alumnos.configure(state="normal")
        
        # 2. Borrar el texto usando el inicio y el fin del tag
        self.txt_alumnos.delete(f"{alumno_id}.first", f"{alumno_id}.last")
        
        self.txt_alumnos.configure(state="disabled")
        
        # 4. Remover el alumno de la lista de seleccionados e invocar la consulta
        if alumno_id in self.alumnos:
            self.alumnos.remove(alumno_id)
            self._consultar_alumnos()

    def _limpiar_form(self):
        self.nombre.set("")
        self.categoria.set("")
        self.requiere_electricidad.set(False)
    
    def guardar(self):
        if self.negocio: # Editando
            valores = {
                "nombre": self.nombre.get(),
                "categoria": str(self.categoria.get()).lower(),
                "requiere_electricidad": self.requiere_electricidad.get(),
                "alumnos": self.alumnos,
            }
        else: # Guardando
            valores = {
                "nombre": self.nombre.get(),
                "categoria": str(self.categoria.get()).lower(),
                "requiere_electricidad": self.requiere_electricidad.get(),
                "alumnos": self.alumnos,
                "fecha_creacion": datetime.utcnow(),
                "esta_activo": True,
            }
            
        if len(valores['alumnos']) == 0:
            messagebox.showinfo("Error", "Debe registrar al menos un Alumno en el negocio.")
            return
        
        if len(valores['nombre']) <= 0 or len(valores['nombre']) > 200:
            messagebox.showinfo("Error", "El formato del Nombre es incorrecto.")
            return
        
        if len(valores['categoria']) <= 0 or len(valores['categoria']) > 200:
            messagebox.showinfo("Error", "El formato de la Categoria es incorrecto.")
            return

        try: # Si se logró insertar el negocio
            if self.negocio: # Editando
                self.db_negocios.update_one({'_id': self.negocio.id}, {'$set': valores})
            else: # Insertando
                self.db_negocios.insert_one(valores)
            self._limpiar_form()
            self._cerrar()
            
        except PyMongoError as e:
            messagebox.showinfo("Error", f"Error de MongoDB: {type(e)}, {e}")
        
    def _cerrar(self):
        if self.on_close:
            self.on_close()
        self.destroy()
    
    def desplegar(self):
        self._init_interfaz()
        self.mainloop()