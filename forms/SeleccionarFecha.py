from customtkinter import CTkToplevel, CTkButton
from tkcalendar import Calendar

class SeleccionarFecha(CTkToplevel):
    def __init__(self, parent, objeto={}):
        super().__init__()

        self.title("Seleccionar Fecha")
        self.geometry("300x300")
        self.fecha_seleccionada = None

    def _init_interfaz(self):
        self.cal = Calendar(self, selectmode='day', date_pattern='dd/mm/yyyy')
        self.cal.pack(pady=20, padx=20, fill="both", expand=True)
        CTkButton(self, text="Seleccionar", command=self.seleccionar).pack(pady=(0, 20))

    def seleccionar(self):
        self.fecha_seleccionada = self.cal.get_date()
        self.destroy()

    def desplegar(self):
        self._init_interfaz()