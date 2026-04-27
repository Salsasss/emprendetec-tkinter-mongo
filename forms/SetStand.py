from tkinter import messagebox
from customtkinter import CTkToplevel, CTkLabel, CTkFont, CTkButton, CTkOptionMenu, CTkFrame
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from datetime import datetime

from models.Negocio import Negocio

class SetStand(CTkToplevel):
    def __init__(self, parent, stand, fecha, on_close=None, objeto={}):
        super().__init__()
        self.title("Asignar Stand")
        self.resizable(False, False)
        self.on_close = on_close
        
        conexion = MongoClient("mongodb://localhost:27017/")
        db = conexion['emprendetec'] # Cluster
        
        # Collections
        self.db_negocios = db['negocios']
        self.db_stands = db['stands']

        # Objeto para la opción de Editar
        self.negocio = None
        self.stand = stand
        self.fecha = fecha

        # Consultamos directamente a la base de datos para ver si tiene negocio asignado
        stand_db = self.db_stands.find_one(
            {"_id": self.stand.id, "agenda.fecha": self.fecha},
            {"agenda": {"$elemMatch": {"fecha": self.fecha}}}
        )
        
        if stand_db and "agenda" in stand_db and len(stand_db["agenda"]) > 0:
            id_negocio = stand_db["agenda"][0].get("id_negocio")
            if id_negocio:
                negocio_db = self.db_negocios.find_one({"_id": id_negocio})
                if negocio_db:
                    self.negocio = Negocio(negocio_db)

    def _consultar_negocios(self):
        # 1. Obtener todos los negocios ya asignados en esta fecha
        stands_ocupados = self.db_stands.find(
            {"agenda.fecha": self.fecha},
            {"agenda": 1}
        )
        # Obtener los IDs de los negocios ya asignados en esta fecha
        negocios_asignados = []
        for stand_json in stands_ocupados:
            for item in stand_json.get("agenda", []):
                if item.get("fecha") == self.fecha and item.get("id_negocio"):
                    # Comparamos como string para evitar TypeErrors y aseguramos que exista self.negocio
                    if self.negocio and str(self.negocio.id) == str(item.get("id_negocio")):
                        continue
                    
                    negocios_asignados.append(item.get("id_negocio"))
        
        # 2. Consultar negocios activos excluyendo los IDs ya asignados
        query = {"esta_activo": True, "_id": {"$nin": negocios_asignados}}
        
        if self.negocio:
            query = {
                "$or": [
                    {"esta_activo": True, "_id": {"$nin": negocios_asignados}},
                    {"_id": self.negocio.id}
                ]
            }

        jsons_negocios = self.db_negocios.find(
            query,
            {"_id": 1, "nombre": 1}
        )
        negocios = [Negocio(json) for json in jsons_negocios]
        
        self.map_negocios = {}
        valores = []

        for negocio in negocios:
            texto = negocio.nombre
            self.map_negocios[texto] = negocio.id
            valores.append(texto)
        
        self.negocio_option.configure(values=valores)

    def _init_interfaz(self):
        CTkLabel(self, text=f'{self.stand.id}', font=CTkFont(size=20)).pack(pady=10)

        # CTkLabel(self, text=f'Fecha: {self.stand.ubicacion.fecha}').pack(pady=10)

        CTkLabel(self, text=f'Ubicación', width=120, anchor='center').pack(pady=(0, 5))
        CTkLabel(self, text=f'Zona: {self.stand.ubicacion.zona}', width=120, anchor='w').pack(pady=(0, 5))
        CTkLabel(self, text=f'Pasillo: {self.stand.ubicacion.pasillo}', width=120, anchor='w').pack(pady=(0, 5))
        CTkLabel(self, text=f'No. Mesa: {self.stand.ubicacion.numero_mesa}', width=120, anchor='w').pack(pady=(0, 5))

        frame = CTkFrame(self, fg_color='transparent')
        frame.pack(pady=5)

        CTkLabel(frame, text="Negocio:").pack(side='left', padx=(0, 10))
        self.negocio_option = CTkOptionMenu(frame)    
        self._consultar_negocios()

        if self.negocio:
            self.negocio_option.set(self.negocio.nombre)
        else:
            self.negocio_option.set("Selecciona un Negocio")

        self.negocio_option.pack(side='left')
        estado_btn = "normal" if self.negocio else "disabled"
        CTkButton(frame, text="x", width=20, command=self._desasignar, fg_color="#a30000", state=estado_btn).pack(side='left', expand=True, fill='y', padx=5)

        CTkButton(self, text="Asignar", command=self._asignar).pack(pady=10)

    def _asignar(self):
        value_combo = self.negocio_option.get()
        id_negocio = self.map_negocios.get(value_combo)

        if not id_negocio:
            messagebox.showinfo("Error", "Seleccione un Negocio.")
            return

        try: # Si se logró asignar el Negocio
            # Primero removemos la asignación anterior para esta misma fecha (limpia la agenda si ya estaba ocupada esa fecha)
            self.db_stands.update_one({'_id': self.stand.id}, {'$pull': {"agenda": {"fecha": self.fecha}}})
            
            # Luego insertamos la nueva asignación actualizada
            self.db_stands.update_one({'_id': self.stand.id}, {'$push': {"agenda": {"fecha": self.fecha, "id_negocio": id_negocio, "ocupado": True}}})
            self._cerrar()
        except PyMongoError as e:
            messagebox.showinfo("Error", f"Error de MongoDB: {type(e)}, {e}")

    def _desasignar(self):
        try:
            self.db_stands.update_one(
                {'_id': self.stand.id},
                {'$pull': {"agenda": {"fecha": self.fecha}}}
            )
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