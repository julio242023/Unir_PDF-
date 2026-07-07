import os
import tempfile
from PIL import Image
import fitz  # PyMuPDF
from docx2pdf import convert

class GestorArchivos:
    @staticmethod
    def unificar_y_comprimir(lista_archivos, ruta_salida, callback_estado, aplicar_opt, nivel_res, nivel_comp):
        try:
            doc_final = fitz.open()
            archivos_temporales = []

            # Mapeo de resoluciones según el slider (0: Baja, 1: Media, 2: Alta)
            resoluciones = {0: (800, 600), 1: (1280, 720), 2: (1920, 1080)}
            calidad_img = {0: 60, 1: 80, 2: 95}
            
            res_max = resoluciones.get(int(nivel_res), (1280, 720)) if aplicar_opt else None
            calidad = calidad_img.get(int(nivel_res), 95) if aplicar_opt else 100

            for i, archivo in enumerate(lista_archivos):
                callback_estado(f"Procesando {i+1}/{len(lista_archivos)}: {os.path.basename(archivo)}")
                ext = archivo.lower().split('.')[-1]
                
                if ext == "pdf":
                    doc_temp = fitz.open(archivo)
                    doc_final.insert_pdf(doc_temp)
                    doc_temp.close()
                    
                elif ext in ["jpg", "jpeg", "png"]:
                    temp_img_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
                    archivos_temporales.append(temp_img_pdf)
                    
                    img = Image.open(archivo).convert("RGB")
                    if aplicar_opt:
                        img.thumbnail(res_max, Image.Resampling.LANCZOS)
                        img.save(temp_img_pdf, "PDF", resolution=90.0, quality=calidad, save_all=True)
                    else:
                        img.save(temp_img_pdf, "PDF", save_all=True)
                    
                    doc_temp = fitz.open(temp_img_pdf)
                    doc_final.insert_pdf(doc_temp)
                    doc_temp.close()
                    
                elif ext == "docx":
                    temp_docx_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
                    archivos_temporales.append(temp_docx_pdf)
                    try:
                        # docx2pdf requiere MS Word
                        convert(archivo, temp_docx_pdf)
                    except Exception as e:
                        raise Exception(f"No se pudo convertir el archivo Word. Asegúrate de tener Microsoft Word instalado y cerrado.\nArchivo: {os.path.basename(archivo)}\nError interno: {str(e)}")
                    
                    doc_temp = fitz.open(temp_docx_pdf)
                    doc_final.insert_pdf(doc_temp)
                    doc_temp.close()

            callback_estado("Generando PDF final...")
            
            # Opciones de compresión PyMuPDF según el slider (0: Alta compresión, 1: Media, 2: Baja compresión)
            if aplicar_opt:
                if int(nivel_comp) == 0:
                    doc_final.save(ruta_salida, garbage=4, deflate=True, clean=True)
                elif int(nivel_comp) == 1:
                    doc_final.save(ruta_salida, garbage=3, deflate=True)
                else:
                    doc_final.save(ruta_salida, garbage=1, deflate=False)
            else:
                doc_final.save(ruta_salida)
                
            doc_final.close()

            # Limpieza de temporales
            for temp_file in archivos_temporales:
                try:
                    os.remove(temp_file)
                except:
                    pass

            return True, "Proceso finalizado."
        except Exception as e:
            return False, str(e)
            
    @staticmethod
    def aplicar_compresion_agresiva(ruta_archivo, callback_estado):
        try:
            callback_estado("Aplicando compresión agresiva...")
            doc = fitz.open(ruta_archivo)
            temp_path = ruta_archivo.replace(".pdf", "_temp.pdf")
            doc.save(temp_path, garbage=4, deflate=True, clean=True, linear=True)
            doc.close()
            os.replace(temp_path, ruta_archivo)
            return True
        except Exception as e:
            return False