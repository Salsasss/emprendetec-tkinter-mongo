from subprocess import CREATE_BREAKAWAY_FROM_JOB
from customtkinter import CTkToplevel, CTkFrame, CTkLabel, CTkEntry, CTkButton, StringVar, CTkImage
from tkinter import messagebox
from pymongo import MongoClient
import bcrypt

from models.Usuario import Usuario

from PIL import Image

class FormLogin(CTkToplevel):
    def __init__(self, master, al_iniciar_sesion):
        super().__init__(master)
        self.title("Iniciar Sesión - EmprendeTec")
        self.geometry("400x380")
        self.resizable(False, False)

        # Necesario para que sea modal e intercepte todo (la app principal está atás)
        self.grab_set()

        self.al_iniciar_sesion = al_iniciar_sesion # Función de "App" a ejecutar

        # Conexión independiente o pasada por parámetro
        conexion = MongoClient("mongodb://localhost:27017/")
        self.db_usuarios = conexion['emprendetec']['usuarios']

        self.correo = StringVar()
        self.contrasena = StringVar()

        self._init_interfaz()

    def _init_interfaz(self):
        self.frame = CTkFrame(self)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        img1 = Image.open("static/images/logo2.png")
        img2 = Image.open("static/images/logo1.png")

        frame_imgs = CTkFrame(self.frame, fg_color="transparent")
        frame_imgs.pack()

        logo_1 = CTkImage(light_image=img1, size=(140, 50))
        label_1 = CTkLabel(frame_imgs, image=logo_1, text="")
        label_1.pack(side='left', padx=10)

        logo_2 = CTkImage(light_image=img2, size=(65, 50))
        label_2 = CTkLabel(frame_imgs, image=logo_2, text="")
        label_2.pack(side='right', padx=10, pady=(5, 0))

        CTkLabel(self.frame, text="Sistema de Control EmprendeTec", font=("Roboto", 20, "bold")).pack(pady=20)

        CTkLabel(self.frame, text="Correo").pack(pady=(0, 5), padx=10, fill="x")
        CTkEntry(self.frame, textvariable=self.correo, placeholder_text="Correo Electrónico").pack(pady=(0, 5), padx=10, fill="x")
        CTkLabel(self.frame, text="Contraseña").pack(pady=(0, 5), padx=10, fill="x")
        CTkEntry(self.frame, textvariable=self.contrasena, placeholder_text="Contraseña", show="*").pack(pady=(0, 5), padx=10, fill="x")

        CTkButton(self.frame, text="Iniciar Sesión", command=self.validar_login).pack(pady=(24, 0), padx=10, fill="x")

    def validar_login(self):
        correo = self.correo.get()
        contrasena = self.contrasena.get()

        if not correo or not contrasena:
            messagebox.showinfo("Atención", "Todos los campos son obligatorios")
            return

        # Buscar AL usuario solo por su correo
        user_data = self.db_usuarios.find_one({
               "correo": correo, 
               "esta_activo": True
        })

        # self.destroy() # Cerramos ventana de login
        # self.al_iniciar_sesion(None) 

        # # Si el usuario existe, comprobar si las contraseñas coinciden
        if user_data:
            # checkpw requiere datos en formato de bytes.
            match = bcrypt.checkpw(
                contrasena.encode('utf-8'), 
                user_data['contrasena']
            )

            if match: # Incio de Sesión Exitoso
                self.destroy() # Cerramos ventana de login
                self.al_iniciar_sesion(Usuario(user_data)) # Le regresamos el control al Main
            else:
                messagebox.showinfo("Error", "Credenciales incorrectas o usuario inactivo.")
        else:
            messagebox.showinfo("Error", "Credenciales incorrectas o usuario inactivo.")