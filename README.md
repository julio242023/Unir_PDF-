# Unificador de PDFs (Centria)

Una herramienta de escritorio moderna y ligera diseñada para unificar múltiples formatos de documentos y archivos visuales en un único documento PDF optimizado y comprimido. Cuenta con validación de identidad e integración con el entorno de Windows.

---

## 🚀 Características Principales

- **Unificación Multiformato:** Combina de forma sencilla archivos `.pdf`, `.docx` (Microsoft Word), `.jpg`, `.jpeg` y `.png` en un solo documento final.
- **Optimización y Compresión Inteligente:**
  - Control de resolución de imágenes (Baja, Media o Alta).
  - Niveles de compresión ajustables para reducir el peso final del archivo.
- **Control de Peso Corporativo (Límite 3MB):** Alerta automáticamente si el archivo resultante supera los **3 MB** (límite corporativo habitual) y ofrece una opción de **compresión agresiva adicional** en un segundo paso.
- **Validación de Identidad Segura:** Verifica que el usuario activo de Windows pertenezca a dominios autorizados (`centria.net`, `breca.com`, `gmail.com`, `outlook.com`) mediante la consulta a:
  - Active Directory local (LDAP/SAM Account Name).
  - Microsoft Entra ID / Azure AD en la nube.
  - Cuentas de Microsoft Personales en el registro de Windows.
- **Interfaz Gráfica Moderna:** Desarrollada con `customtkinter` para ofrecer una estética limpia, profesional y adaptada a temas claros/oscuros.
- **Controles de Orden:** Permite ordenar los archivos agregados (subir/bajar) y eliminar elementos antes del proceso de unificación.

---

## 🛠️ Requisitos del Sistema

- **Sistema Operativo:** Windows.
- **Python:** Versión 3.8 o superior.
- **Microsoft Word:** Requerido para la conversión directa de archivos `.docx` a PDF (usa la biblioteca `docx2pdf` que interactúa con la API nativa de MS Word).

---

## 📦 Instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/julio242023/Unir_PDF-.git
   cd Unir_PDF-
   ```

2. **Crea y activa un entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv env
   # En Windows Powershell:
   .\env\Scripts\Activate.ps1
   # En CMD:
   .\env\Scripts\activate.bat
   ```

3. **Instala las dependencias del proyecto:**
   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Dependencias Utilizadas

El proyecto utiliza las siguientes librerías especificadas en [requirements.txt](file:///c:/Users/sky_c/Documents/Antigravity/Unir_PDF/requirements.txt):
- `customtkinter`: Para la interfaz visual moderna.
- `Pillow`: Para el procesamiento y reescalado de imágenes.
- `PyMuPDF` (fitz): Para la manipulación, unión y compresión eficiente de archivos PDF.
- `docx2pdf`: Para convertir documentos de Microsoft Word a PDF de forma nativa.
- `pyinstaller`: Para compilar la aplicación a un archivo ejecutable `.exe` independiente.

---

## 🖥️ Ejecución y Uso

Para iniciar la aplicación de forma local, simplemente ejecuta:

```bash
python main.py
```

### Pasos dentro de la aplicación:
1. **Cargar Documentos:** Haz clic en **➕ Agregar Archivos** para seleccionar los archivos PDF, DOCX o imágenes.
2. **Organizar:** Utiliza los botones `▲`, `▼` y `✕` a la derecha de la lista para ordenar o quitar elementos.
3. **Nombre del PDF:** Escribe el nombre deseado para el archivo final.
4. **Optimización:** Deja marcada la optimización si deseas aplicar la compresión y el escalado de imágenes personalizado.
5. **Unificar:** Haz clic en **Unificar y Comprimir**, selecciona dónde guardar el archivo, ¡y listo!

---

## 🔧 Generar Ejecutable (.exe)

Si deseas compilar la aplicación en un único archivo ejecutable `.exe` para su distribución en Windows, ejecuta el siguiente comando:

```bash
pyinstaller --noconsole --onefile main.py
```

El archivo compilado se generará dentro de la carpeta `dist/`.

---

## 📧 Soporte Técnico

Para cualquier duda, inconveniente o solicitud de soporte relacionado con el aplicativo, ponte en contacto con Soporte TI Corporativo:
- **Correo:** [jmariluz@centria.net](mailto:jmariluz@centria.net)