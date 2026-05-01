from forms import FormLogin
from customtkinter import CTk, CTkTabview, CTkFrame, CTkLabel, CTkButton, CTkOptionMenu, StringVar, CTkImage
from tkinter import messagebox
from datetime import datetime
from pymongo import MongoClient
import bcrypt

from PIL import Image

from models.TableFrame import TableFrame

from models.Usuario import Usuario
from models.Alumno import Alumno
from models.Negocio import Negocio
from models.Stand import Stand
from models.GenPDF import GenPDF

from forms.FormLogin import FormLogin
from forms.FormAlumno import FormAlumno
from forms.FormNegocio import FormNegocio
from forms.FormUsuario import FormUsuario
from forms.FormStand import FormStand
from forms.SeleccionarFecha import SeleccionarFecha

class App(CTk):
    def __init__(self):
        super().__init__()
        self.title("EmprendeTec")
        self.geometry('800x650')
        self.resizable(True, True)
        
        conexion = MongoClient('mongodb+srv://aaronsalasn_db_user:4lGNYrzHie9kCzfM@cluster0.vss7zgu.mongodb.net/')
        db = conexion['emprendetec'] # Cluster
        
        # Collections
        self.db_usuarios = db['usuarios']
        self.db_alumnos = db['alumnos']
        self.db_negocios = db['negocios']
        self.db_stands = db['stands']
        
        # StringVar
        self.fecha_agenda = StringVar()
        self.fecha_para_mongo = datetime(2023, 1, 1)

        # Ocultar la app (hasta no iniciar sesión)
        self.withdraw()
    
    def _init_header(self):
        cont_header = CTkFrame(self, height=20, fg_color="transparent")
        cont_header.pack(side='top', fill='x')
        
        img1 = Image.open("static/images/logo2.png")
        img2 = Image.open("static/images/logo1.png")

        logo_1 = CTkImage(light_image=img1, size=(140,  50))
        label_1 = CTkLabel(cont_header, image=logo_1, text="")
        label_1.pack(side='left', padx=10, pady=(5, 0))

        title_label = CTkLabel(cont_header, text="Sistema de Control EmprendeTec", font=("Roboto", 24, "bold"))
        title_label.place(relx=0.5, rely=0.5, anchor='center')
        
        logo_2 = CTkImage(light_image=img2, size=(65, 50))
        label_2 = CTkLabel(cont_header, image=logo_2, text="")
        label_2.pack(side='right', padx=10, pady=(5, 0))
        
    def _init_tabs(self):
        self.tabview = CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)

        self.tabview.add("Stands")
        self.tabview.add("Negocios")
        self.tabview.add("Alumnos")
        
        if self.usuario_actual.rol == Usuario.roles['admin']:
            self.tabview.add("Usuarios")
            
    def _init_tablas(self):
        # Tabla Alumnos
        self.tabla_alumnos = TableFrame(self.tabview.tab("Alumnos"), Alumno.columnas)
        self.tabla_alumnos.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        
        jsons_alumnos = self.db_alumnos.find(
            {},
            {"fecha_creacion": 0}
        )
        alumnos = [Alumno(json) for json in jsons_alumnos]
        
        self.tabla_alumnos._llenar_tabla(alumnos, Alumno.campos, self.db_alumnos)
        
        # Tabla Negocios
        self.tabla_negocios = TableFrame(self.tabview.tab("Negocios"), Negocio.columnas)
        self.tabla_negocios.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        
        jsons_negocios = self.db_negocios.find(
             {},
             {"_id": 1, "nombre": 1, "categoria": 1, "requiere_electricidad": 1, "esta_activo": 1, }
        )
        
        negocios = [Negocio(json) for json in jsons_negocios]
        
        self.tabla_negocios._llenar_tabla(negocios, Negocio.campos, self.db_negocios)
        
        # Tabla Usuarios
        if self.usuario_actual.esta_activo and self.usuario_actual.rol == Usuario.roles['staff']: # Solo continuar si el usuario es Admin
            return
        
        self.tabla_usuarios = TableFrame(self.tabview.tab("Usuarios"), Usuario.columnas)
        self.tabla_usuarios.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        
        jsons_usuarios = self.db_usuarios.find(
            {}
        )
        
        usuarios = [Usuario(json) for json in jsons_usuarios]
        
        self.tabla_usuarios._llenar_tabla(usuarios, Usuario.campos, self.db_usuarios)
    
    def _recargar_tabla_alumnos(self):
        json_ultimo = self.db_alumnos.find(
            {},
            {"fecha_creacion": 0},
            sort=[("fecha_creacion", -1)],
            limit=1
        )[0]
        alumno = Alumno(json_ultimo)
        self.tabla_alumnos.insertar_fila(alumno, Alumno.campos, self.db_alumnos)
        
    def _recargar_tabla_negocios(self):
        json_ultimo = self.db_negocios.find(
            {},
            {"alumnos": 0},
            sort=[("fecha_creacion", -1)],
            limit=1
        )[0]

        negocio = Negocio(json_ultimo)
        self.tabla_negocios.insertar_fila(negocio, Negocio.campos, self.db_negocios)
        
    def _recargar_tabla_usuario(self):
        json_ultimo = self.db_usuarios.find(
            {},
            sort=[("fecha_creacion", -1)],
            limit=1
        )[0]

        usuario = Usuario(json_ultimo)
        self.tabla_usuarios.insertar_fila(usuario, Usuario.campos, self.db_usuarios)    
    
    def _init_botones_stands(self):
        self.cont_stands = CTkFrame(self.tabview.tab("Stands"))
        self.cont_stands.pack(fill='both', expand=True)

        CTkLabel(self.cont_stands, text="PASILLO A", height=35, bg_color="gray").grid(row=0, column=1, columnspan=4, pady=5, sticky="we")
        
        jsons_stands = self.db_stands.find(
            {},
        )
        self.stands = [Stand(json) for json in jsons_stands]
        
        self.botones_stands = {}

        j=0
        
        for i in range(6):
           self.cont_stands.columnconfigure(i, weight=1)
        
        for i in range(1, 3):
            for o in range(1, 5):
                btn = CTkButton(self.cont_stands, width=400, height=60, text=self.stands[j].id, command=lambda stand=self.stands[j]: self.abrir_stand(stand), fg_color='green')
                btn.grid(row=i, column=o, padx=5, pady=5, sticky="we")
                self.botones_stands[self.stands[j].id] = btn
                j += 1

        CTkLabel(self.cont_stands, text="PASILLO B", height=35, bg_color="gray").grid(row=3, column=1, columnspan=4, pady=5, sticky="we")
        
        for o in range(6):
            btn = CTkButton(self.cont_stands, width=400, height=60, text=self.stands[j].id, command=lambda stand=self.stands[j]: self.abrir_stand(stand), fg_color='green')
            btn.grid(row=4, column=o, padx=5, pady=(30, 0), sticky="we")
            self.botones_stands[self.stands[j].id] = btn
            j += 1

        CTkLabel(self.cont_stands, text="PASILLO C", height=35, bg_color="gray").grid(row=5, column=0, columnspan=6, pady=10, sticky="we")
        
        for o in range(6):
            btn = CTkButton(self.cont_stands, width=400, height=60, text=self.stands[j].id, command=lambda stand=self.stands[j]: self.abrir_stand(stand), fg_color='green')
            btn.grid(row=6, column=o, padx=5, sticky="we")
            self.botones_stands[self.stands[j].id] = btn
            j += 1
    
    def _consultar_stands_ocupados(self):
        jsons_stands_ocupados = self.db_stands.find(
            {"agenda.fecha": self.fecha_para_mongo}, 
             # Parte 2: La Proyección (¿Qué partes del documento devolver?)
             {
                 "_id": 1,           # Queremos el ID del stand
                 "agenda": {
                     "$elemMatch": {"fecha": self.fecha_para_mongo} # ¡Aquí está la magia!
                 },
                 "ubicacion": 1
             }
        )
        
        self.stands_ocupados = [Stand(json) for json in jsons_stands_ocupados]
    
    def _init_botones_stands_acciones(self):
        self._consultar_stands_ocupados()

        if len(self.stands_ocupados) == 0:
            self.btn_pdf.configure(state='disabled')
        else:
            self.btn_pdf.configure(state='normal')

        # Habilitando todos los botones
        for key, value in self.botones_stands.items():
            if value.cget('fg_color') == '#a30000':
                value.configure(fg_color='green')
                value.configure(text=f'{key}')
        
        # Deshabilitando los ocupados
        for stand in self.stands_ocupados:
            ocupado = self.botones_stands[stand.id]
            ocupado.configure(fg_color='#a30000')
            ocupado.configure(text=f'{stand.id} \n {stand.agenda[0].negocio.nombre}')
    
    def _init_botones(self):
        cont_botones_alumnos = CTkFrame(self.tabview.tab("Alumnos"), fg_color="transparent")
        cont_botones_alumnos.pack(pady=5)
        CTkButton(cont_botones_alumnos, text="Nuevo Alumno", command=lambda: self.tabla_alumnos.abrir_form(FormAlumno, self._recargar_tabla_alumnos)).pack(side='left', padx=5)
        CTkButton(cont_botones_alumnos, text="Exportar Alumnos (PDF)", command=self.generar_pdf_alumnos).pack(side='left', padx=5)

        cont_botones_negocios = CTkFrame(self.tabview.tab("Negocios"), fg_color="transparent")
        cont_botones_negocios.pack(pady=5)
        CTkButton(cont_botones_negocios, text="Nuevo Negocio", command=lambda: self.tabla_negocios.abrir_form(FormNegocio, self._recargar_tabla_negocios)).pack(side='left', padx=5)
        CTkButton(cont_botones_negocios, text="Exportar Negocios (PDF)", command=self.generar_pdf_negocios).pack(side='left', padx=5)

        if self.usuario_actual.esta_activo and self.usuario_actual.rol == Usuario.roles['admin']: # Solo si el usuario es rol Admin
            cont_botones_usuarios = CTkFrame(self.tabview.tab("Usuarios"), fg_color="transparent")
            cont_botones_usuarios.pack(pady=5)
            CTkButton(cont_botones_usuarios, text="Nuevo Usuario", command=lambda: self.tabla_usuarios.abrir_form(FormUsuario, self._recargar_tabla_usuario)).pack(side='left', padx=5)
            # CTkButton(cont_botones_usuarios, text="Exportar Usuarios (PDF)", command=self.generar_pdf_negocios).pack(side='left', padx=5)


        # Select de Fecha
        fechas_evento = self.db_stands.distinct("agenda.fecha") # Trae todas las fechas del evento usando distinct
        self.fechas_texto = [fecha.strftime("%d/%m/%Y") for fecha in fechas_evento]

        cont_fecha = CTkFrame(self.tabview.tab("Stands"))
        cont_fecha.pack()

        CTkLabel(cont_fecha, text="Fecha del Evento:").pack(side='left', padx=5)
        self.option_menu = CTkOptionMenu(cont_fecha, variable=self.fecha_agenda, values=self.fechas_texto, command=self.fecha_seleccionada)
        self.option_menu.pack(side='left', padx=(0, 5))
        CTkButton(cont_fecha, text="+", width=20, command=self._agregar_fecha).pack(side='left', expand=True, fill='y', padx=(0, 5))
        CTkButton(cont_fecha, text="x", width=20, command=self._eliminar_fecha, fg_color="#a30000").pack(side='left', expand=True, fill='y', padx=(0, 5))
        
        self.btn_pdf = CTkButton(cont_fecha, text="Exportar Logística de hoy (PDF)", command=self.generar_pdf_logistica)
        self.btn_pdf.pack(side='left', expand=True, fill='y')

        # Si hay fechas del evento
        if len(self.fechas_texto) > 0:
            self.fecha_agenda.set(self.fechas_texto[0])
            self.fecha_seleccionada(self.fechas_texto[0])
        else:
            self.btn_pdf.configure(state='disabled')

    def _agregar_fecha(self):
        ventana_fecha = SeleccionarFecha(self)
        ventana_fecha.grab_set()
        ventana_fecha.desplegar()
        self.wait_window(ventana_fecha)
        
        if ventana_fecha.fecha_seleccionada:
            fecha = ventana_fecha.fecha_seleccionada
            if fecha not in self.fechas_texto:
                self.fechas_texto.append(fecha)
                self.option_menu.configure(values=self.fechas_texto)
            self.fecha_agenda.set(fecha)
            self.fecha_seleccionada(fecha)
    
    def _eliminar_fecha(self):
        respuesta = messagebox.askyesno(
            title="Confirmación",
            message = "¿Está seguro de eliminar la fecha?"
        )
        
        if respuesta:
            try:
                # 1. Quitar todas las agendas de esa fecha particular
                self.db_stands.update_many(
                    {"agenda.fecha": self.fecha_para_mongo},
                    {"$pull": {"agenda": {"fecha": self.fecha_para_mongo}}}
                )
                
                # 2. Actualizar combo y variables de la UI
                fecha_texto = self.fecha_agenda.get()
                if fecha_texto in self.fechas_texto:
                    self.fechas_texto.remove(fecha_texto)
                
                self.option_menu.configure(values=self.fechas_texto)
                
                # 3. Limpiar o enfocar la otra fecha
                if len(self.fechas_texto) > 0:
                    self.fecha_agenda.set(self.fechas_texto[0])
                    self.fecha_seleccionada(self.fechas_texto[0])
                else:
                    self.fecha_agenda.set("")
                    self.btn_pdf.configure(state='disabled')
                    for key, value in self.botones_stands.items():
                        value.configure(fg_color='green')
                        value.configure(state='enabled')
                        value.configure(text=f'{key}')
            except Exception as e:
                messagebox.showinfo("Error", f"Ocurrió un error: {e}")

    def abrir_stand(self, stand):
        ventana_form = FormStand(self, stand, self.fecha_para_mongo, self._init_botones_stands_acciones)
        ventana_form.grab_set()
        ventana_form.desplegar()
    
    def fecha_seleccionada(self, fecha_elegida):
        self.fecha_para_mongo = datetime.strptime(fecha_elegida, "%d/%m/%Y")
        self._init_botones_stands_acciones()

    def generar_pdf_logistica(self):
        self._consultar_stands_ocupados()
        if len(self.stands_ocupados) > 0:
            generador = GenPDF()
            generador.pdf_logistica(self.stands, self.stands_ocupados, self.fecha_agenda.get())
        else:
            messagebox.showinfo("Atención", "No hay stands ocupados en esta fecha para generar un reporte.")

    def generar_pdf_alumnos(self):
        jsons_alumnos = self.db_alumnos.find()

        alumnos = [Alumno(json) for json in jsons_alumnos]
        if len(alumnos) > 0:
            generador = GenPDF()
            generador.pdf_alumnos(alumnos)
        else:
            messagebox.showinfo("Atención", "No hay alumnos registrados para generar el reporte.")

    def generar_pdf_negocios(self):
        jsons_negocios = self.db_negocios.find(
            {},
            {
                "_id": 0,
            }
        )
        negocios = [Negocio(json) for json in jsons_negocios]
        
        if len(negocios) > 0:
            generador = GenPDF()
            generador.pdf_negocios(negocios)
        else:
            messagebox.showinfo("Atención", "No hay negocios registrados para generar el reporte.")

    def init(self, usuario):
        self.usuario_actual = usuario # Guardamos quién es, por si queremos usar sus roles

        self._init_header()
        self._init_tabs()
        self._init_botones_stands()
        self._init_botones()
        self._init_botones_stands_acciones()
        self._init_tablas()
        self._init_footer()

        self.deiconify() # ¡Magia! Muestra la pantalla principal que estaba oculta
    
    def _init_footer(self):
        # 1. Función cuando el mouse se pone encima
        def al_entrar_mouse(event):
            label_1.configure(text_color="red")

        # 2. Función cuando el mouse se quita
        def al_salir_mouse(event):
            # Aquí regresas el color a la normalidad. 
            # Puedes poner "white", "black", o ["black", "white"] si usas modo claro/oscuro
            label_1.configure(text_color=["black", "white"])

        cont_footer = CTkFrame(self, height=20, fg_color="transparent")
        cont_footer.pack(side='bottom', fill='x')
        
        label_1 = CTkLabel(cont_footer, text="Cerrar Sesión")
        label_1.pack(side='left', padx=20, pady=5)

        label_2 = CTkLabel(cont_footer, text=f"¡Bienvenido, {self.usuario_actual.nombre}!")
        label_2.pack(side='right', padx=20, pady=5)

        # 3. Conectamos los eventos a la etiqueta
        label_1.bind("<Enter>", al_entrar_mouse)
        label_1.bind("<Leave>", al_salir_mouse)
        label_1.bind("<Button-1>", self.cerrar_sesion)

    def cerrar_sesion(self, event=None):
        self.withdraw()
        
        for widget in self.winfo_children():
            widget.destroy()
            
        self.usuario_actual = None
        
        FormLogin(self, self.init)

    def desplegar(self):
        FormLogin(self, self.init)
        self.mainloop()

    def _aux_registrar(self):
        password_hasheada = bcrypt.hashpw("1234".encode('utf-8'), bcrypt.gensalt())
        nuevo_usuario = {
            "nombre": "Aarón2",
            "correo": "aaronsalasnn@gmail.com",
            "contrasena": password_hasheada,
            "rol": "admin",
            "fecha_creacion": datetime.now(),
            "esta_activo": True
        }

        self.db_usuarios.insert_one(nuevo_usuario)

        print("GOL")

appMongo = App()
appMongo.desplegar()