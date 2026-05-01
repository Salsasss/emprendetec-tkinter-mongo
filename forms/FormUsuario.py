from tkinter import messagebox
import bcrypt
from customtkinter import CTkOptionMenu, CTkToplevel, CTkLabel, CTkEntry, CTkButton, StringVar
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import re
from datetime import datetime

from models.Usuario import Usuario

class FormUsuario(CTkToplevel):
    def __init__(self, parent, on_close=None, objeto={}):
        super().__init__()
        self.title("Registrar Nuevo Usuario")
        self.on_close = on_close
        
        conexion = MongoClient('mongodb+srv://aaronsalasn_db_user:4lGNYrzHie9kCzfM@cluster0.vss7zgu.mongodb.net/')
        db = conexion['emprendetec'] # Cluster
        
        # Collections
        self.db_usuarios = db['usuarios']
        
        self.nombre = StringVar()
        self.correo = StringVar()
        self.contrasena1 = StringVar()
        self.contrasena2 = StringVar()
        
        self.roles = list(Usuario.roles.values());

        # Objeto para la opción de Editar
        self.usuario = None
        
        if objeto:
            self.usuario = objeto
            self.nombre.set(self.usuario.nombre)
            self.correo.set(self.usuario.correo)
        
    def _init_interfaz(self):
        self.columnconfigure(1, weight=1)
        
        CTkLabel(self, text="Registrar Nuevo Usuario").grid(row=0, column=0, columnspan=2, padx=15, pady=10, sticky="w")
        
        # Nombre
        CTkLabel(self, text="Nombre:").grid(row=1, column=0, padx=15, pady=10, sticky="w")
        CTkEntry(self, textvariable=self.nombre, justify="center").grid(row=1, column=1, padx=15, pady=10, sticky="ew")

        # Correo
        CTkLabel(self, text="Correo:").grid(row=2, column=0, padx=15, pady=10, sticky="w")
        entry_correo = CTkEntry(self, textvariable=self.correo, justify="center")
        entry_correo.grid(row=2, column=1, padx=15, pady=10, sticky="ew")

        if self.usuario: # Editando
            entry_correo.configure(state='disabled')

        # Contraseña 1
        CTkLabel(self, text="Contraseña:").grid(row=3, column=0, padx=15, pady=10, sticky="w")
        CTkEntry(self, textvariable=self.contrasena1, justify="center", show="*").grid(row=3, column=1, padx=15, pady=10, sticky="ew")

        # Contraseña 2
        CTkLabel(self, text="Repite la Contraseña:").grid(row=4, column=0, padx=15, pady=10, sticky="w")
        CTkEntry(self, textvariable=self.contrasena2, justify="center", show="*").grid(row=4, column=1, padx=15, pady=10, sticky="ew")

        # Rol
        CTkLabel(self, text="Rol:").grid(row=5, column=0, padx=15, pady=10, sticky="w")
        self.option_menu_rol = CTkOptionMenu(self, values=self.roles)
        self.option_menu_rol.set("Selecciona un Rol...")
        self.option_menu_rol.grid(row=5, column=1, padx=15, pady=10, sticky="ew")

        if self.usuario: # Editando
            self.option_menu_rol.set(self.usuario.rol)

        # Botón guardar
        CTkButton(self, text="Guardar Usuario", command=self.guardar).grid(row=6, column=0, columnspan=2, pady=20)
    
    def _limpiar_form(self):
        self.nombre.set("")
        self.correo.set("")
        self.contrasena1.set("")
        self.contrasena2.set("")
        self.option_menu_rol.set("")
    
    def guardar(self):
        if self.usuario: # Editando
            valores = {
                "nombre": self.nombre.get(),
                "contrasena": self.contrasena1.get(),
                "contrasena2": self.contrasena2.get(),
                "rol": self.option_menu_rol.get(),
            }
            
            if valores["contrasena"] or valores["contrasena2"]:
                # Si no son validas las contraseñas -> return
                if not self.validar_contrasenas(valores['contrasena'], valores["contrasena2"]):
                    return 
                
        else: # Insertando
            valores = {
                "nombre": self.nombre.get(),
                "correo": self.correo.get(),
                "contrasena": self.contrasena1.get(),
                "contrasena2": self.contrasena2.get(),
                "rol": self.option_menu_rol.get(),
                "fecha_creacion": datetime.utcnow(),
                "esta_activo": True,
            }
            
            if len(valores['correo']) <= 0 or len(valores['correo']) > 200 or re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', valores['correo']) is None:
                messagebox.showinfo("Error", "El formato del Correo es incorrecto.")
                return
            
            # Si no son validas las contraseñas -> return
            if not self.validar_contrasenas(valores['contrasena'], valores["contrasena2"]):
                return
                           
        if len(valores['nombre']) <= 0 or len(valores['nombre']) > 200:
            messagebox.showinfo("Error", "El formato del Nombre es incorrecto.")
            return
        
        if not valores['rol'] or valores['rol'] not in self.roles:
            messagebox.showinfo("Error", "Seleccione un Rol.")
            return
        
        del valores['contrasena2'] # Eliminando ese elemento
        valores['contrasena'] = bcrypt.hashpw(valores['contrasena'].encode('utf-8'), bcrypt.gensalt())
        
        try: # Si se logró insertar el usuario
            if self.usuario: # Editando
                # Hashear la contraseña (bcrypt requiere que el texto esté codificado a bytes)
                self.db_usuarios.update_one({'_id': self.usuario.id}, {'$set': valores})
            else: # Insertando
                self.db_usuarios.insert_one(valores)
            self._limpiar_form()
            self._cerrar()
            
        except PyMongoError as e:
            messagebox.showinfo("Error", f"Error de MongoDB: {type(e)}, {e}")
        
    def validar_contrasenas(self, contrasena1, contrasena2):
        if len(contrasena1) < 8 or len(contrasena1) > 200:
            messagebox.showinfo("Error", "El formato de la Contraseña es incorrecto (8 caracteres mínimo).")
            return False
    
        if len(contrasena2) < 8 or len(contrasena2) > 200:
            messagebox.showinfo("Error", "El formato de la Contraseña es incorrecto (8 caracteres mínimo).")
            return False

        if contrasena1 != contrasena2:
            messagebox.showinfo("Error", "Las Contraseñas no coinciden.")
            return False
        return True
        
    def _cerrar(self):
        if self.on_close:
            self.on_close()
        self.destroy()
    
    def desplegar(self):
        self._init_interfaz()
        self.mainloop()