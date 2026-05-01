from tkinter import messagebox
import customtkinter as ctk
from fpdf import FPDF
import os
from pymongo import MongoClient
from models.Alumno import Alumno

class PDFEmprendeTec(FPDF):
    def header(self):
        # Logo TecNM (Izquierda)
        self.image("static/images/logo2.png", x=5, y=4, w=45)
        # Logo ITV (Derecha)
        self.image("static/images/logo1.png", x=185, y=4, w=20)
        
        # Texto centrado
        self.set_font("helvetica", "B", 15)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, "Sistema de Control EmprendeTec", align="C")
        self.ln(15)

class GenPDF:
    def __init__(self):
        # Conectar a MongoDB para traer los detalles de los alumnos
        conexion = MongoClient('mongodb+srv://aaronsalasn_db_user:4lGNYrzHie9kCzfM@cluster0.vss7zgu.mongodb.net/')
        self.db_alumnos = conexion['emprendetec']['alumnos']

    def draw_pasillo_en_pdf(self, pdf, stands_totales, stands_ocupados, titulo, width, height, starts, count, cols_per_row, start_x, page_w):
        # Stands
        rows = (count + cols_per_row - 1) // cols_per_row
        stand_idx = starts
        
        for r in range(rows):
            cx = pdf.get_x()
            cy = pdf.get_y()
            for c in range(cols_per_row):
                if stand_idx >= starts + count:
                    break
                
                stand = stands_totales[stand_idx]
                
                # Check if occupied
                ocupado = next((s for s in stands_ocupados if s.id == stand.id), None)
                
                if ocupado:
                    negocio_nombre = ocupado.agenda[0].negocio.nombre
                    if len(negocio_nombre) > 15:
                        negocio_nombre = negocio_nombre[:13] + "..."
                    pdf.set_fill_color(220, 220, 220)
                    fill = True
                    texto = f"{stand.id}\n{negocio_nombre}"
                else:
                    pdf.set_fill_color(255, 255, 255)
                    fill = False
                    texto = f"{stand.id}\n(Libre)"

                pdf.rect(cx + c * width, cy, width, height, style='FD' if fill else 'D')
                
                pdf.set_font("helvetica", "B" if ocupado else "", 10)
                pdf.set_xy(cx + c * width, cy + (height - 8) / 2) # Center vertically approx
                pdf.multi_cell(width, 4, texto, border=0, align="C")
                
                stand_idx += 1
            pdf.set_xy(start_x, cy + height + 2)

    def pdf_logistica(self, stands_totales, stands_ocupados, fecha_texto):
        # 1. Preguntar al usuario dónde quiere guardar el archivo
        ruta_guardado = ctk.filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Guardar reporte como...",
            initialfile=f"Logistica_Stands_{fecha_texto.replace('/', '-')}.pdf"
        )

        if not ruta_guardado:
            return

        # Crear el PDF
        pdf = PDFEmprendeTec()
        pdf.add_page()
        
        # Titulo del Reporte
        pdf.set_font("helvetica", "B", 18)
        pdf.cell(0, 10, "Reporte Detallado de Logística - EmprendeTec", ln=True, align="C")
        
        pdf.set_font("helvetica", "I", 12)
        pdf.cell(0, 10, f"Fecha del Evento: {fecha_texto}", ln=True, align="C")
        pdf.ln(10)

        # -- CROQUIS DEL EVENTO --
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "Croquis del Evento", ln=True, align="C")
        pdf.ln(5)

        start_x = pdf.get_x()
        page_w = 190

        # Pasillo A: 8 stands, 4 per row
        if len(stands_totales) >= 8:
            # Titulo
            pdf.set_fill_color(180, 180, 180)
            pdf.set_font("helvetica", "", 12)
            pdf.cell(page_w, 10, "Pasillo A", ln=True, align="C", fill=True)
            pdf.ln(2)

            self.draw_pasillo_en_pdf(pdf, stands_totales, stands_ocupados, "PASILLO A", page_w / 4, 15, 0, 8, 4, start_x, page_w)
        
            # Titulo
            pdf.set_fill_color(180, 180, 180)
            pdf.set_font("helvetica", "", 12)
            pdf.cell(page_w, 10, "Pasillo B", ln=True, align="C", fill=True)
            pdf.ln(10)

        # Pasillo B: 6 stands, 6 per row
        if len(stands_totales) >= 14:
            self.draw_pasillo_en_pdf(pdf, stands_totales, stands_ocupados, "PASILLO B", page_w / 6, 15, 8, 6, 6, start_x, page_w)

        # Titulo
        pdf.set_fill_color(180, 180, 180)
        pdf.set_font("helvetica", "", 12)
        pdf.cell(page_w, 10, "Pasillo C", ln=True, align="C", fill=True)
        pdf.ln(2)

        # Pasillo C: 6 stands, 6 per row
        if len(stands_totales) >= 20:
            self.draw_pasillo_en_pdf(pdf, stands_totales, stands_ocupados, "PASILLO C", page_w / 6, 15, 14, 6, 6, start_x, page_w)

        pdf.add_page() # Siguiente página de detalles puros

        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "Detalles de Asignación por Stand", ln=True, align="C")
        pdf.ln(5)

        # Imprimir datos bloque por bloque
        for stand in stands_ocupados:
            negocio = stand.agenda[0].negocio
            requiere_luz = "Sí" if negocio.requiere_electricidad == 1 else "No"
            
            # Encabezado del Stand
            pdf.set_font("helvetica", "B", 13)
            pdf.set_fill_color(220, 220, 220)
            pdf.cell(0, 10, f"{stand.id} | {negocio.nombre}", ln=True, fill=True)
            
            # Información del Negocio
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 8, "Negocio:", ln=True)
            pdf.set_font("helvetica", "", 12)

            pdf.cell(10, 6, "", ln=False)
            pdf.cell(0, 8, f"Categoría: {str(negocio.categoria).upper()}", ln=True)
            
            self.print_boolean(pdf, "Ocupa Electricidad: ", "Sí" if negocio.requiere_electricidad == 1 else "No")
            
            # Consultar y mostrar los alumnos registrados
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 8, "Integrantes (Alumnos):", ln=True)
            
            pdf.set_font("helvetica", "", 11)
            if len(negocio.alumnos) > 0:
                for id_alumno in negocio.alumnos:
                    json_alumno = self.db_alumnos.find_one({"_id": id_alumno})
                    if json_alumno:
                        alumno = Alumno(json_alumno)
                        pdf.cell(10, 6, "", ln=False)
                        pdf.cell(0, 6, str(alumno), ln=True)
            else:
                pdf.cell(10, 6, "-", ln=False)
                pdf.cell(0, 6, "Sin integrantes registrados.", ln=True)
            
            # Ubicación del Stand
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 8, "Ubicación (Stand):", ln=True)
            
            pdf.set_font("helvetica", "", 12)
            pdf.cell(10, 6, "", ln=False)
            pdf.cell(0, 8, f"Zona: {stand.ubicacion.zona}", ln=True)
            
            pdf.cell(10, 6, "", ln=False)
            pdf.cell(0, 8, f"Pasillo: {stand.ubicacion.pasillo}", ln=True)
            
            pdf.cell(10, 6, "", ln=False)
            pdf.cell(0, 8, f"No. Mesa: {stand.ubicacion.numero_mesa}", ln=True)

            pdf.ln(5) # Separador entre stands

        # Guardar el PDF y abrirlo
        try:
            pdf.output(ruta_guardado)
            # Abrir el archivo automáticamente -> Exclusivo de Windows
            os.startfile(ruta_guardado)
        except Exception as e:
            messagebox.showinfo("Error", f"Error al guardar el archivo: {type(e)}, {e}")

    def pdf_alumnos(self, alumnos):
        ruta_guardado = ctk.filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Guardar reporte como...",
            initialfile="Reporte_Alumnos.pdf"
        )

        if not ruta_guardado:
            return

        pdf = PDFEmprendeTec()
        pdf.add_page()
        
        pdf.set_font("helvetica", "B", 18)
        pdf.cell(0, 10, "Reporte de Alumnos Registrados - EmprendeTec", ln=True, align="C")
        pdf.ln(5)

        for alumno in alumnos:
            pdf.set_font("helvetica", "B", 12)
            pdf.set_fill_color(220, 220, 220)
            pdf.cell(0, 10, f"{alumno.nombre} {alumno.primer_apellido} {alumno.segundo_apellido}", ln=True, fill=True)
            
            pdf.set_font("helvetica", "", 12)

            pdf.cell(10, 6, "", ln=False)
            pdf.cell(0, 8, f"No. Control: {alumno.id}", ln=True)

            pdf.cell(10, 6, "", ln=False)
            fecha_str = alumno.fecha_creacion.strftime("%d/%m/%Y")
            pdf.cell(0, 8, f"Fecha Registro: {fecha_str}", ln=True)
            
            self.print_boolean(pdf, "Activo: ", "Sí" if alumno.esta_activo else "No")
            
            pdf.ln(5)

        try:
            pdf.output(ruta_guardado)
            os.startfile(ruta_guardado)
        except Exception as e:
            messagebox.showinfo("Error", f"Error al guardar el archivo: {type(e)}, {e}")

    def pdf_negocios(self, negocios):
        ruta_guardado = ctk.filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Guardar reporte como...",
            initialfile="Reporte_Negocios.pdf"
        )

        if not ruta_guardado:
            return

        pdf = PDFEmprendeTec()
        pdf.add_page()
        
        pdf.set_font("helvetica", "B", 18)
        pdf.cell(0, 10, "Reporte de Negocios Registrados - EmprendeTec", ln=True, align="C")
        pdf.ln(5)

        for negocio in negocios:
            pdf.set_font("helvetica", "B", 13)
            pdf.set_fill_color(220, 220, 220)
            pdf.cell(0, 10, f"{negocio.nombre}", ln=True, fill=True)
            
            pdf.set_font("helvetica", "", 12)
            pdf.cell(10, 6, "", ln=False)
            pdf.cell(0, 8, f"Categoría: {str(negocio.categoria).upper()}", ln=True)
            
            self.print_boolean(pdf, "Ocupa Electricidad: ", "Sí" if negocio.requiere_electricidad == 1 else "No")

            pdf.cell(10, 6, "", ln=False)
            fecha_str2 = negocio.fecha_creacion.strftime("%d/%m/%Y")
            pdf.cell(0, 8, f"Fecha Registro: {fecha_str2}", ln=True)

            self.print_boolean(pdf, "Activo: ", "Sí" if negocio.esta_activo else "No")

            # Consultar y mostrar los alumnos registrados
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 8, "Integrantes (Alumnos):", ln=True)
            
            pdf.set_font("helvetica", "", 11)
            if len(negocio.alumnos) > 0:
                for id_alumno in negocio.alumnos:
                    json_alumno = self.db_alumnos.find_one({"_id": id_alumno})
                    if json_alumno:
                        alumno = Alumno(json_alumno)
                        pdf.cell(10, 6, "", ln=False)
                        pdf.cell(0, 6, str(alumno), ln=True)
            else:
                pdf.cell(10, 6, "-", ln=False)
                pdf.cell(0, 6, "Sin integrantes registrados.", ln=True)

            
            pdf.ln(5)

        try:
            pdf.output(ruta_guardado)
            os.startfile(ruta_guardado)
        except Exception as e:
            messagebox.showinfo("Error", f"Error al guardar el archivo: {type(e)}, {e}")

    def print_boolean(self, pdf, texto, valor):
        # Resaltamos si ocupa luz
        pdf.cell(10, 6, "", ln=False)
        pdf.cell(45, 6, texto, ln=False)
        pdf.set_font("helvetica", "B", 12)
        if valor == "Sí":
            pdf.set_text_color(0, 128, 0)
        else:
            pdf.set_text_color(128, 0, 0)
        
        pdf.cell(10, 6, "", ln=False)
        pdf.cell(0, 6, valor, ln=True)
        pdf.set_text_color(0, 0, 0) # Reset color
        pdf.set_font("helvetica", "", 12)