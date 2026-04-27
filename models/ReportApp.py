from tkinter import messagebox
import customtkinter as ctk
from fpdf import FPDF
import os

class ReportApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x200")
        self.title("Generador de Reportes")

        # Botón en tu interfaz para generar el reporte
        self.btn_generar = ctk.CTkButton(
            self, 
            text="Generar Reporte PDF", 
            command=self.generar_reporte_pdf
        )
        self.btn_generar.pack(pady=50)

    def generar_reporte_pdf(self):
        # 1. Preguntar al usuario dónde quiere guardar el archivo
        ruta_guardado = ctk.filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Guardar reporte como..."
        )

        # Si el usuario cancela, no hacemos nada
        if not ruta_guardado:
            return

        # 2. Obtener tus datos de MongoDB (Mock de ejemplo)
        # Asumiendo que traes esto con pymongo: "coleccion.find({})"
        datos_ejemplo = [
            {"id": "1", "nombre": "Proyecto Alpha", "responsable": "Juan Perez"},
            {"id": "2", "nombre": "Innovación Web", "responsable": "Maria Lopez"},
            {"id": "3", "nombre": "EmprendeTec App", "responsable": "Carlos Slim"},
        ]

        # 3. Crear el documento PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Título del Reporte
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, "Reporte de Proyectos - EmprendeTec", ln=True, align="C")
        pdf.ln(10) # Salto de línea

        # Encabezados de la tabla
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(30, 10, "ID", border=1, align="C")
        pdf.cell(80, 10, "Nombre Proyecto", border=1, align="C")
        pdf.cell(70, 10, "Responsable", border=1, align="C")
        pdf.ln()

        # Filas con los datos
        pdf.set_font("helvetica", "", 12)
        for fila in datos_ejemplo:
            pdf.cell(30, 10, fila["id"], border=1, align="C")
            pdf.cell(80, 10, fila["nombre"], border=1, align="L")
            pdf.cell(70, 10, fila["responsable"], border=1, align="L")
            pdf.ln()

        try:
            pdf.output(ruta_guardado)
            # Abrir el archivo automáticamente -> Exclusivo de Windows
            os.startfile(ruta_guardado)
            
        except Exception as e:
            messagebox.showinfo("Error", f"Error al guardar el archivo: {type(e)}, {e}")

app = ReportApp()
app.mainloop()
