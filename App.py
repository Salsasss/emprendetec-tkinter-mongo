from customtkinter import CTk, CTkTabview, CTkFrame, CTkLabel, CTkButton, CTkOptionMenu, StringVar, CTkImage, CTkToplevel
from tkcalendar import Calendar
from datetime import datetime
from pymongo import MongoClient

from PIL import Image

from TableFrame import TableFrame

from models.Alumno import Alumno
from models.Negocio import Negocio
from models.Stand import Stand

from forms.FormAlumno import FormAlumno
from forms.FormNegocio import FormNegocio
from forms.SetStand import SetStand
from forms.SeleccionarFecha import SeleccionarFecha

class App(CTk):
    def __init__(self): # DONE
        super().__init__()
        self.title("EmprendeTec")
        self.geometry('800x600')
        self.resizable(True, True)
        
        conexion = MongoClient("mongodb://localhost:27017/")
        db = conexion['emprendetec'] # Cluster
        
        # Collections
        self.db_alumnos = db['alumnos']
        self.db_negocios = db['negocios']
        self.db_stands = db['stands']
        
        # StringVar
        self.fecha_agenda = StringVar()
        self.fecha_para_mongo = datetime(2023, 1, 1)
    
    def _init_header(self):
        cont_header = CTkFrame(self, height=20, fg_color="transparent")
        cont_header.pack(side='top', fill='x')
        
        img1 = Image.open("static/images/logo2.png")
        img2 = Image.open("static/images/logo1.png")

        logo_1 = CTkImage(light_image=img1, size=(140, 50))
        label_1 = CTkLabel(cont_header, image=logo_1, text="")
        label_1.pack(side='left', padx=10, pady=(5, 0))

        title_label = CTkLabel(cont_header, text="Sistema de Control EmprendeTec", font=("Roboto", 24, "bold"))
        title_label.place(relx=0.5, rely=0.5, anchor='center')
        
        logo_2 = CTkImage(light_image=img2, size=(60, 50))
        label_2 = CTkLabel(cont_header, image=logo_2, text="")
        label_2.pack(side='right', padx=10, pady=(5, 0))
        
    def _init_tabs(self): # DONE
        self.tabview = CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)

        self.tabview.add("Stands")
        self.tabview.add("Negocios")
        self.tabview.add("Alumnos")
        
    def _init_tablas(self): # DONE
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
    
    def _recargar_tabla_alumnos(self): # DONE
        json_ultimo = self.db_alumnos.find(
            {},
            {"fecha_creacion": 0},
            sort=[("fecha_creacion", -1)],
            limit=1
        )[0]
        alumno = Alumno(json_ultimo)
        self.tabla_alumnos.insertar_fila(alumno, Alumno.campos, self.db_alumnos)
        
    def _recargar_tabla_negocios(self): # DONE
        json_ultimo = self.db_negocios.find(
            {},
            {"_id": 0, "alumnos": 0},
            sort=[("fecha_creacion", -1)],
            limit=1
        )[0]
        negocio = Negocio(json_ultimo)
        self.tabla_negocios.insertar_fila(negocio, Negocio.campos, self.db_negocios)
    
    def _init_botones_stands(self): # DONE
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
    
    def _init_botones_stands_acciones(self):
        jsons_stands_ocupados = self.db_stands.find(
            {"agenda.fecha": self.fecha_para_mongo}, 
             # Parte 2: La Proyección (¿Qué partes del documento devolver?)
             {
                 "_id": 1,           # Queremos el ID del stand
                 "agenda": {
                     "$elemMatch": {"fecha": self.fecha_para_mongo} # ¡Aquí está la magia!
                 }
             }
        )
        
        stands_ocupados = [Stand(json) for json in jsons_stands_ocupados]
            
        # Habilitando todos los botones
        for key, value in self.botones_stands.items():
            if value.cget('state') == 'disabled':
                value.configure(fg_color='green')
                value.configure(state='enabled')
                value.configure(text=f'{key}')
        
        # Deshabilitando los ocupados
        for stand in stands_ocupados:
            ocupado = self.botones_stands[stand.id]
            ocupado.configure(fg_color='red')
            ocupado.configure(state='disabled')
            ocupado.configure(text=f'{stand.id} \n {stand.agenda[0].negocio.nombre}')
    
    def _init_botones(self): # DONE
        CTkButton(self.tabview.tab("Alumnos"), text="Nuevo Alumno", command=lambda: self.tabla_alumnos.abrir_form(FormAlumno, self._recargar_tabla_alumnos)).pack()
        CTkButton(self.tabview.tab("Negocios"), text="Nuevo Negocio", command=lambda: self.tabla_negocios.abrir_form(FormNegocio, self._recargar_tabla_negocios)).pack()

        # Select de Fecha
        fechas_evento = self.db_stands.distinct("agenda.fecha") # Trae todas las fechas del evento usando distinct
        self.fechas_texto = [fecha.strftime("%d/%m/%Y") for fecha in fechas_evento]

        cont_fecha = CTkFrame(self.tabview.tab("Stands"))
        cont_fecha.pack()

        CTkLabel(cont_fecha, text="Fecha del Evento:").pack(side='left', padx=10)
        self.option_menu = CTkOptionMenu(cont_fecha, variable=self.fecha_agenda, values=self.fechas_texto, command=self.fecha_seleccionada)
        self.option_menu.pack(side='left')
        CTkButton(cont_fecha, text="+", width=20, command=self._agregar_fecha).pack(side='left', expand=True, fill='y', padx=10)
    
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
      
    def abrir_stand(self, stand): # DONE
        ventana_form = SetStand(self, stand, self.fecha_para_mongo, self._init_botones_stands_acciones)
        ventana_form.grab_set()
        ventana_form.desplegar()

    def fecha_seleccionada(self, fecha_elegida): # DONE
        self.fecha_para_mongo = datetime.strptime(fecha_elegida, "%d/%m/%Y")
        self._init_botones_stands_acciones()
        
    def desplegar(self): # DONE
        self._init_header()
        self._init_tabs() # DONE
        self._init_botones_stands()
        self._init_botones()
        self._init_botones_stands_acciones()
        self._init_tablas() # DONE
        self.mainloop() # DONE

appMongo = App()
appMongo.desplegar()