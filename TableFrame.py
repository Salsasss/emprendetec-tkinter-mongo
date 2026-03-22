from customtkinter import CTkScrollableFrame, CTkLabel, CTkFrame, CTkButton
from tkinter import messagebox
from pymongo import MongoClient

from models.Alumno import Alumno
from models.Negocio import Negocio

from forms.FormAlumno import FormAlumno
from forms.FormNegocio import FormNegocio

class TableFrame(CTkScrollableFrame):
    def __init__(self, parent, columnas, **kwargs):
        super().__init__(parent, **kwargs)

        conexion = MongoClient("mongodb://localhost:27017/")
        db = conexion['emprendetec'] # Cluster
        
        # Collections
        self.db_alumnos = db['alumnos']
        self.db_negocios = db['negocios']
    
        self.columnas = columnas

        # Configurar columnas
        for i in range(len(columnas)):
            self.grid_columnconfigure(i, weight=1)

        # Crear encabezados
        for i, text in enumerate(columnas):
            header = CTkLabel(
                self,
                text=text,
                font=("Arial", 14, "bold"),
                fg_color="#2b2b2b",
                text_color="white",
                height=30
            )
            header.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)

    def insertar_fila(self, objeto, campos, coleccion):
        # contador de filas (empieza en 1 porque 0 es el header)
        if not hasattr(self, "fila_actual"):
            self.fila_actual = 1

        fila_widgets = []

        for i, campo in enumerate(campos):
            valor = getattr(objeto, campo) # Obtenemos el valor del objeto

            cell = CTkLabel(self, text=str(valor), fg_color="#3a3a3a", height=28)
            cell.grid(row=self.fila_actual, column=i, sticky="nsew", padx=1, pady=1)

            fila_widgets.append(cell)
            
        cell = self.insertar_botones_accion(objeto.id, objeto.esta_activo, coleccion)
        fila_widgets.append(cell)
    
        self.fila_actual += 1
        
    def insertar_botones_accion(self, id, esta_activo, coleccion):
        btn_frame = CTkFrame(self, fg_color="#3a3a3a")
        btn_frame.grid(row=self.fila_actual, column=(len(self.columnas)-1), padx=1, pady=1, sticky="nsew")
        
        # Frame interno para centrar
        cont = CTkFrame(btn_frame, fg_color="transparent")
        cont.pack(expand=True, anchor="center")
        
        CTkButton(cont, text="Editar", width=40, height=20, fg_color="#3b8ed0", command=lambda id=id, coleccion=coleccion: self.editar(id, coleccion)).pack(side="left", padx=2)
        if esta_activo: # Desactivar
            CTkButton(cont, text="X", width=30, height=20, fg_color="#943126", command=lambda id=id, valor=False, coleccion=coleccion: self.cambiar_activo(id, valor, coleccion)).pack(side="left", padx=2)
        else: # Activar
            CTkButton(cont, text="A", width=30, height=20, fg_color="#269428", command=lambda id=id, valor=True, coleccion=coleccion: self.cambiar_activo(id, valor, coleccion)).pack(side="left", padx=2)
        return btn_frame
    
    def recargar_tabla(self, coleccion):
        # Primero vaciamos la tabla
        self.limpiar_tabla()
        
        if coleccion == self.db_alumnos:
            jsons_alumnos = coleccion.find(
                {},
                {"created_at": 0}
            )
            alumnos = [Alumno(json) for json in jsons_alumnos]
            
            self._llenar_tabla(alumnos, Alumno.campos, coleccion)
        elif coleccion == self.db_negocios:
            jsons_negocios = self.db_negocios.find(
                {},
                {"_id": 1, "nombre": 1, "categoria": 1, "requiere_electricidad": 1, "esta_activo": 1, }
            )
            negocios = [Negocio(json) for json in jsons_negocios]
            
            self._llenar_tabla(negocios, Negocio.campos, coleccion)
    
    def editar(self, id, coleccion):
        json_encontrado = coleccion.find_one(
            {'_id': id}
        )
        
        if coleccion == self.db_alumnos:
            self.abrir_form(
                FormAlumno,
                lambda: self.recargar_tabla(coleccion=self.db_alumnos),
                objeto=Alumno(json_encontrado)
            )
        elif coleccion == self.db_negocios:
            self.abrir_form(
                FormNegocio,
                lambda: self.recargar_tabla(coleccion=self.db_negocios),
                objeto=Negocio(json_encontrado)
            )
    
    def cambiar_activo(self, id, valor, coleccion):
        respuesta = messagebox.askyesno(
            title="Confirmación", 
            message = "¿Seguro de Activar?" if valor else "¿Seguro de Desactivar?"
        )
        
        if respuesta:
            # Cambiar esta_activo
            coleccion.update_one({'_id': id}, {'$set': {'esta_activo': valor}})
            
            self.recargar_tabla(coleccion)
    
    def abrir_form(self, ClaseFormulario, metodo_on_close, objeto=None): # DONE
        ventana_form = ClaseFormulario(self, on_close=metodo_on_close, objeto=objeto)
        ventana_form.grab_set()
        ventana_form.desplegar()
    
    def _llenar_tabla(self, objetos, campos, coleccion):
        for objeto in objetos:
            self.insertar_fila(objeto, campos, coleccion)
    
    def limpiar_tabla(self):
        for widget in self.winfo_children():
            info = widget.grid_info()
            # conservar header (row 0)
            if int(info["row"]) > 0:
                widget.destroy()

        # reiniciar contador de filas
        self.fila_actual = 1