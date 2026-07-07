import subprocess
import os
import re

DOMINIOS_PERMITIDOS = [
    "centria.net", 
    "breca.com",
    "gmail.com",
    "outlook.com"
]


def obtener_correo_windows():
    # Configuración para ocultar ventanas de comandos en segundo plano
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    # Expresión regular para validar y limpiar formatos de correo electrónico
    regex_correo = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    # ==========================================
    # NIVEL 1: Entorno Corporativo Principal (Active Directory)
    # ==========================================
    try:
        comando_ad = 'powershell -Command "([adsisearcher]\'(samaccountname=$env:USERNAME)\').FindOne().Properties.userprincipalname"'
        resultado = subprocess.check_output(comando_ad, shell=True, startupinfo=startupinfo)
        lineas = resultado.decode('utf-8').strip().split('\n')
        
        # Iteramos las líneas recibidas y nos quedamos con la primera dirección válida
        for linea in lineas:
            correo_encontrado = re.search(regex_correo, linea)
            if correo_encontrado:
                return correo_encontrado.group(0).lower() # Retorna solo el correo principal en minúsculas
    except Exception:
        pass

    # ==========================================
    # NIVEL 2: Entorno Azure AD / Entra ID (Nube corporativa)
    # ==========================================
    try:
        comando_azure = 'powershell -Command "(Get-ItemProperty -Path \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Group Policy\\GroupMembership\' -ErrorAction SilentlyContinue).SearchDS"'
        resultado = subprocess.check_output(comando_azure, shell=True, startupinfo=startupinfo)
        lineas = resultado.decode('utf-8').strip().split('\n')
        
        for linea in lineas:
            correo_encontrado = re.search(regex_correo, linea)
            if correo_encontrado:
                return correo_encontrado.group(0).lower()
    except Exception:
        pass

    # ==========================================
    # NIVEL 3: Cuenta Microsoft Personal / Registro de Identidad
    # ==========================================
    try:
        # Consultamos las propiedades extendidas del usuario de identidad de Windows
        comando_registro = 'powershell -Command "(Get-ChildItem -Path \'HKCU:\\Software\\Microsoft\\IdentityCRL\\UserExtendedProperties\' -ErrorAction SilentlyContinue).PSChildName"'
        resultado = subprocess.check_output(comando_registro, shell=True, startupinfo=startupinfo)
        lineas = resultado.decode('utf-8').strip().split('\n')
        
        for linea in lineas:
            correo_encontrado = re.search(regex_correo, linea)
            if correo_encontrado:
                return correo_encontrado.group(0).lower()
    except Exception:
        pass

    # ==========================================
    # NIVEL 4: Fallback a Cuenta Local Tradicional (Sin Correo)
    # ==========================================
    try:
        usuario_local = os.environ.get('USERNAME')
        dominio_local = os.environ.get('USERDOMAIN')
        if usuario_local and dominio_local:
            # Si no hay correos válidos en los niveles anteriores, devolvemos el usuario de sesión clásico
            return f"{dominio_local}\\{usuario_local}".lower()
    except Exception:
        pass

    # Si se agotan absolutamente todas las opciones y no hay datos del sistema
    return None


def validar_acceso():
    correo = obtener_correo_windows()
    # correo = "jmariluz@centria.net"
    # Para pruebas locales, puedes descomentar la línea de abajo y forzar un correo:
    # correo = "usuario@centria.net"
    
    if not correo:
        return False, "No se detectó un usuario de red."
    if any(correo.endswith(f"@{dominio}") for dominio in DOMINIOS_PERMITIDOS):
        return True, f"{correo}"
    else:
        return False, f"Acceso denegado para: {correo}"