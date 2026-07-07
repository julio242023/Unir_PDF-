import os
import threading
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from auth import validar_acceso
from gestor_archivos import GestorArchivos

class GestorUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Unificador de PDFs")
        # Altura perfectamente calibrada para evitar recortes por escalado de Windows
        self.geometry("450x640") 
        self.resizable(False, False)
        
        self.archivos_cargados = []
        self.acceso_concedido, self.mensaje = validar_acceso()
        
        if not self.acceso_concedido:
            messagebox.showerror("Acceso Denegado", self.mensaje)

        self.construir_ui()

    def construir_ui(self):
        # --- DETECTAR MODO PARA EL LISTBOX NATIVO ---
        es_oscuro = self._get_appearance_mode() == "dark"
        lb_bg = "#2a2a2a" if es_oscuro else "#ffffff"
        lb_fg = "#e8eaed" if es_oscuro else "#202124"
        lb_border = "#3c4043" if es_oscuro else "#dadce0"

        # --- PIE DE PÁGINA ---
        self.lbl_footer = ctk.CTkLabel(self, text="© Centria", font=("Segoe UI", 10), text_color=("#b0b0b0", "#70757a"))
        self.lbl_footer.pack(side="bottom", pady=4)

        # --- BOTÓN DE AYUDA ---
        self.btn_help = ctk.CTkButton(
            self, text="❓", width=22, height=22, corner_radius=11, 
            fg_color="transparent", text_color=("#888888", "#b0b0b0"), hover_color=("#e4e6e9", "#3c4043"),
            font=("Segoe UI", 12), command=self.mostrar_ayuda
        )
        self.btn_help.place(relx=0.96, y=10, anchor="ne") 

        # --- HEADER (IDENTIDAD SEGURA) ---
        self.frame_header = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_header.pack(pady=(12, 2))

        icono = "      🛡️" if self.acceso_concedido else "🚫"
        titulo = "Identidad Segura" if self.acceso_concedido else "Acceso Restringido"
        
        # Formato original con el checkmark verde de éxito restaurado
        texto_usuario = f"✅ {self.mensaje}" if self.acceso_concedido else f"❌ {self.mensaje}"
        color_usuario = "#34a853" if self.acceso_concedido else "#ea4335"

        self.lbl_icono = ctk.CTkLabel(self.frame_header, text=icono, font=("Segoe UI", 28))
        self.lbl_icono.pack(anchor="center")
        
        self.lbl_titulo = ctk.CTkLabel(self.frame_header, text=titulo, font=("Segoe UI", 15, "bold"), text_color=("#202124", "#e8eaed"))
        self.lbl_titulo.pack(pady=(1, 1), anchor="center")
        
        self.lbl_usuario = ctk.CTkLabel(self.frame_header, text=texto_usuario, font=("Segoe UI", 11, "bold"), text_color=color_usuario)
        self.lbl_usuario.pack(anchor="center")

        # Línea divisoria de identidad recuperada e integrada
        self.separador = ctk.CTkFrame(self, height=2, width=350, fg_color="#e0e0e0")
        self.separador.pack(pady=10)

        estado_botones = "normal" if self.acceso_concedido else "disabled"

# --- SECCIÓN 1: CONTROL DE DOCUMENTOS ---
        self.lbl_paso1 = ctk.CTkLabel(self, text="1. Cagar Documentos", font=("Segoe UI", 10, "bold"), text_color=("#5f6368", "#9aa0a6"))
        self.lbl_paso1.pack(anchor="center")
        
        self.btn_cargar = ctk.CTkButton(
            self, text="➕ Agregar Archivos", command=self.cargar_archivos, 
            fg_color=("#ffffff", "#2d2d2d"), text_color=("#1a73e8", "#8ab4f8"), 
            hover_color=("#f8f9fa", "#3c4043"), border_width=1, border_color=lb_border,
            width=180, height=28, font=("Segoe UI", 11, "bold"),
            state=estado_botones
        )
        self.btn_cargar.pack(pady=4, anchor="center")

        # Contenedor de Lista (Compactado y protegido contra expansiones erráticas)
        self.frame_lista = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_lista.pack(pady=2, padx=35, fill="x", anchor="center")

        # 1. AQUÍ DEFINES EL ALTO MANUAL (height=75 hace el cuadro pequeño y chato)
        self.frame_listbox_scroll = ctk.CTkFrame(self.frame_lista, fg_color="transparent", height=95)
        self.frame_listbox_scroll.pack(side="left", fill="x", expand=True)
        self.frame_listbox_scroll.pack_propagate(False) # <-- OBLIGA a respetar los 75px de alto

        self.listbox = tk.Listbox(
            self.frame_listbox_scroll, height=4, font=("Segoe UI", 10), 
            bg=lb_bg, fg=lb_fg,
            selectbackground="#1a73e8", selectforeground="white",
            relief="flat", borderwidth=1, highlightthickness=1, highlightcolor=lb_border, bd=0
        )
        
        self.scrollbar = ctk.CTkScrollbar(self.frame_listbox_scroll, width=12, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.scrollbar.set)
        
        # Empaquetado correcto para que llene el ancho sin crecer hacia abajo
        self.listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y", expand=False)
        # Botones de Control Laterales
        self.frame_controles = ctk.CTkFrame(self.frame_lista, fg_color="transparent")
        self.frame_controles.pack(side="right", padx=(6, 0))

        self.btn_subir = ctk.CTkButton(self.frame_controles, text="▲", width=28, height=22, fg_color=("#f1f3f4", "#3c4043"), text_color=("#3c4043", "#e8eaed"), hover_color=("#e8eaed", "#4f5357"), font=("Segoe UI", 9), state=estado_botones, command=self.mover_arriba)
        self.btn_subir.pack(pady=1)
        self.btn_bajar = ctk.CTkButton(self.frame_controles, text="▼", width=28, height=22, fg_color=("#f1f3f4", "#3c4043"), text_color=("#3c4043", "#e8eaed"), hover_color=("#e8eaed", "#4f5357"), font=("Segoe UI", 9), state=estado_botones, command=self.mover_abajo)
        self.btn_bajar.pack(pady=1)
        self.btn_eliminar = ctk.CTkButton(self.frame_controles, text="✕", width=28, height=22, fg_color=("#fce8e6", "#5c2523"), text_color=("#c5221f", "#f28b82"), hover_color=("#fad2cf", "#752d2a"), font=("Segoe UI", 9, "bold"), state=estado_botones, command=self.eliminar_seleccion)
        self.btn_eliminar.pack(pady=1)

        # --- CAMPO: NOMBRE DEL ARCHIVO ---
        self.frame_nombre = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_nombre.pack(pady=4, padx=35, fill="x", anchor="center")
        
        self.lbl_nombre = ctk.CTkLabel(self.frame_nombre, text="Nombre del PDF:", font=("Segoe UI", 11, "bold"), text_color=("#5f6368", "#9aa0a6"))
        self.lbl_nombre.pack(side="left", padx=(0, 8))
        
        self.entry_nombre = ctk.CTkEntry(
            self.frame_nombre, placeholder_text="ej. Documento_Final", 
            height=26, fg_color=("#ffffff", "#2d2d2d"), border_color=lb_border, text_color=("#202124", "#e8eaed"), font=("Segoe UI", 11),
            state=estado_botones
        )
        self.entry_nombre.pack(side="right", fill="x", expand=True)

        self.separador2 = ctk.CTkFrame(self, height=1, width=380, fg_color=("#f1f3f4", "#3c4043"))
        self.separador2.pack(pady=5)

        # --- SECCIÓN 2: CONFIGURACIÓN DE SALIDA ---
        self.lbl_paso2 = ctk.CTkLabel(self, text="2. Ajustes de Optimización", font=("Segoe UI", 10, "bold"), text_color=("#5f6368", "#9aa0a6"))
        self.lbl_paso2.pack(anchor="center")

        self.chk_optimizar_var = ctk.BooleanVar(value=True)
        self.slider_res_var = ctk.IntVar(value=1)  
        self.slider_comp_var = ctk.IntVar(value=2) 

        self.chk_optimizar = ctk.CTkCheckBox(
            self, text="Activar compresión y escalado inteligente", 
            variable=self.chk_optimizar_var, command=self.toggle_sliders, 
            text_color=("#202124", "#e8eaed"), font=("Segoe UI", 11), state=estado_botones,
            checkbox_width=16, checkbox_height=16
        )
        self.chk_optimizar.pack(pady=4, anchor="center")

        self.frame_sliders = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_sliders.pack(fill="x", padx=45, anchor="center")

        # Slider Resolución
        self.lbl_res = ctk.CTkLabel(self.frame_sliders, text="Resolución Imágenes: Media (Recomendada)", font=("Segoe UI", 11), text_color=("#5f6368", "#9aa0a6"))
        self.lbl_res.pack(anchor="w")
        self.slider_res = ctk.CTkSlider(self.frame_sliders, from_=0, to=2, number_of_steps=2, height=14, variable=self.slider_res_var, command=self.actualizar_labels, state=estado_botones)
        self.slider_res.pack(fill="x", pady=(1, 5))

        # Slider Compresión
        self.lbl_comp = ctk.CTkLabel(self.frame_sliders, text="Compresión PDF: Baja (Mejor calidad)", font=("Segoe UI", 11), text_color=("#5f6368", "#9aa0a6"))
        self.lbl_comp.pack(anchor="w")
        self.slider_comp = ctk.CTkSlider(self.frame_sliders, from_=0, to=2, number_of_steps=2, height=14, variable=self.slider_comp_var, command=self.actualizar_labels, state=estado_botones)
        self.slider_comp.pack(fill="x", pady=(1, 2))
        
        self.actualizar_labels(None)

        # --- SECCIÓN 3: ACCIÓN PRINCIPAL (BLOQUEADO DE FORMA SEGURA EN SU SITIO) ---
        self.btn_procesar = ctk.CTkButton(
            self, text="Unificar y Comprimir", command=self.iniciar_proceso, 
            fg_color=("#1a73e8", "#1a73e8"), hover_color=("#1557b0", "#1557b0"), 
            font=("Segoe UI", 12, "bold"), width=200, height=34, corner_radius=6,
            state=estado_botones
        )
        self.btn_procesar.pack(pady=(10, 2), anchor="center")

        self.lbl_estado = ctk.CTkLabel(self, text="Listo para estructurar." if self.acceso_concedido else "Acceso restringido por políticas.", font=("Segoe UI", 11), text_color=("#70757a", "#9aa0a6") if self.acceso_concedido else "#c5221f")
        self.lbl_estado.pack(anchor="center")

    def toggle_sliders(self):
        if self.chk_optimizar_var.get() and self.acceso_concedido:
            self.slider_res.configure(state="normal", progress_color=("#1a73e8", "#1a73e8"), button_color=("#1a73e8", "#1a73e8"))
            self.slider_comp.configure(state="normal", progress_color=("#1a73e8", "#1a73e8"), button_color=("#1a73e8", "#1a73e8"))
            self.lbl_res.configure(text_color=("#5f6368", "#9aa0a6"))
            self.lbl_comp.configure(text_color=("#5f6368", "#9aa0a6"))
        else:
            color_opaco_prog = ("#e0e0e0", "#404040")
            color_opaco_btn = ("#cccccc", "#555555")
            self.slider_res.configure(state="disabled", progress_color=color_opaco_prog, button_color=color_opaco_btn)
            self.slider_comp.configure(state="disabled", progress_color=color_opaco_prog, button_color=color_opaco_btn)
            self.lbl_res.configure(text_color=("#c0c0c0", "#555555"))
            self.lbl_comp.configure(text_color=("#c0c0c0", "#555555"))

    def actualizar_labels(self, _):
        textos_res = {0: "Baja", 1: "Media (Recomendada)", 2: "Alta"}
        textos_comp = {0: "Alta (Menor peso)", 1: "Media (Recomendada)", 2: "Baja (Peso Standar)"}
        
        self.lbl_res.configure(text=f"Resolución Imágenes: {textos_res[self.slider_res_var.get()]}")
        self.lbl_comp.configure(text=f"Compresión PDF: {textos_comp[self.slider_comp_var.get()]}")

    def mostrar_ayuda(self):
        messagebox.showinfo("Soporte Técnico", "Soporte TI Corporativo:\njmariluz@centria.net")

    def cargar_archivos(self):
        rutas = filedialog.askopenfilenames(
            title="Seleccionar archivos", 
            filetypes=[("Formatos admitidos", "*.pdf *.docx *.jpg *.png"), ("PDF", "*.pdf"), ("Word", "*.docx"), ("Imágenes", "*.jpg *.png")]
        )
        for r in rutas:
            self.archivos_cargados.append(r)
            self.listbox.insert(tk.END, os.path.basename(r))

    def mover_arriba(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == 0: return
        idx = sel[0]
        texto = self.listbox.get(idx)
        self.listbox.delete(idx)
        self.listbox.insert(idx - 1, texto)
        self.listbox.selection_set(idx - 1)
        self.archivos_cargados.insert(idx - 1, self.archivos_cargados.pop(idx))

    def mover_abajo(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == self.listbox.size() - 1: return
        idx = sel[0]
        texto = self.listbox.get(idx)
        self.listbox.delete(idx)
        self.listbox.insert(idx + 1, texto)
        self.listbox.selection_set(idx + 1)
        self.archivos_cargados.insert(idx + 1, self.archivos_cargados.pop(idx))

    def eliminar_seleccion(self):
        sel = self.listbox.curselection()
        if not sel: return
        self.listbox.delete(sel[0])
        self.archivos_cargados.pop(sel[0])

    def actualizar_estado(self, mensaje):
        self.lbl_estado.configure(text=mensaje, text_color="#1a73e8")

    def iniciar_proceso(self):
        if not self.archivos_cargados:
            messagebox.showwarning("Atención", "Carga al menos un archivo para procesar.")
            return

        nombre_sugerido = self.entry_nombre.get().strip()
        if not nombre_sugerido:
            nombre_sugerido = "Documento_Unificado"

        ruta_salida = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            initialfile=nombre_sugerido,
            filetypes=[("PDF", "*.pdf")], 
            title="Guardar PDF unificado..."
        )
        if not ruta_salida: return

        self.btn_procesar.configure(state="disabled", text="Procesando...")
        threading.Thread(target=self.ejecutar_unificacion, args=(ruta_salida,), daemon=True).start()

    def ejecutar_unificacion(self, ruta_salida):
        aplicar_opt = self.chk_optimizar_var.get()
        level_res = self.slider_res_var.get()
        level_comp = self.slider_comp_var.get()

        exito, msj = GestorArchivos.unificar_y_comprimir(self.archivos_cargados, ruta_salida, self.actualizar_estado, aplicar_opt, level_res, level_comp)
        
        if exito:
            peso_bytes = os.path.getsize(ruta_salida)
            if peso_bytes > 3145728:
                peso_mb = round(peso_bytes / 1048576, 2)
                respuesta = messagebox.askyesno(
                    "Advertencia de Tamaño", 
                    f"El archivo final pesa {peso_mb}MB (mayor al límite establecido de 3MB).\n\n¿Deseas intentar forzar una compresión agresiva extra?"
                )
                if respuesta:
                    GestorArchivos.aplicar_compresion_agresiva(ruta_salida, self.actualizar_estado)
                    nuevo_peso_mb = round(os.path.getsize(ruta_salida) / 1048576, 2)
                    messagebox.showinfo("Éxito", f"Compresión extra completada.\nNuevo peso: {nuevo_peso_mb}MB\nGuardado en: {ruta_salida}")
                else:
                    messagebox.showinfo("Éxito", f"PDF generado sin alteraciones extras.\nGuardado en: {ruta_salida}")
            else:
                self.lbl_estado.configure(text="✅ ¡PDF generado con éxito!", text_color="#34a853")
                messagebox.showinfo("Éxito", f"El archivo ha sido guardado en:\n{ruta_salida}")
            
            self.listbox.delete(0, tk.END)
            self.archivos_cargados.clear()
            self.entry_nombre.delete(0, tk.END)
        else:
            self.lbl_estado.configure(text="❌ Ocurrió un error.", text_color="#ea4335")
            messagebox.showerror("Error de Procesamiento", msj)
            
        self.btn_procesar.configure(state="normal", text="Unificar y Comprimir")