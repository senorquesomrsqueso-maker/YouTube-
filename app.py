import streamlit as st
import yt_dlp
import pandas as pd
import re
import time
import requests
import json
import datetime
import math
import os
import traceback
import urllib.parse
import random
import google.generativeai as genai
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup

# ==============================================================================
# 1. CONFIGURACIÓN ESTRUCTURAL Y NÚCLEO IA DE ALTO RENDIMIENTO
# ==============================================================================

# Credenciales de Acceso - Protocolo BS LATAM
DRIVE_API_KEY = "AIzaSyBjETNqerBHpqCBQBH7B1bZl55eYWrtMQk" 
GEMINI_API_KEY = "AIzaSyA8HsM0vSCopd1s05nOryhbNIGU26dvxG4"

# Configuración Inicial del Dashboard
st.set_page_config(
    page_title="BS LATAM - AUDIT ELITE SUPREMACÍA V33.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialización de Inteligencia Artificial Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Marcador de tiempo
    fecha_actual_global = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Configuración de generación
    generation_config = {
        "temperature": 0.85,
        "top_p": 0.95,
        "top_k": 45,
        "max_output_tokens": 4096,
    }
    
    # Instrucción Maestra del Sistema - Identidad Corporativa
    system_instruction_core = (
        f"Eres el Consultor Senior y Partner Estratégico de BS LATAM. "
        f"HOY ES: {fecha_actual_global}. "
        "Tu misión es asistir al usuario en TODO: auditoría de métricas, programación, "
        "redacción de reportes, matemáticas complejas y análisis de mercado. "
        "Eres una IA de PROPÓSITO GENERAL. "
        "Mantén siempre un tono profesional, con autoridad técnica. "
        "Estilo visual: Cyberpunk Industrial / Corporativo de Élite. "
        "NUNCA uses frases robóticas ni disculpas innecesarias."
    )

    # Configuramos el modelo sin forzar rutas largas
    model_name_target = 'gemini-1.5-flash' 
    
    # Inicializamos el modelo vinculando la instrucción que acabamos de crear
    model_ia = genai.GenerativeModel(
        model_name=model_name_target,
        generation_config=generation_config,
        system_instruction=system_instruction_core
    )
    
    st.sidebar.success("Núcleo Neuronal: ONLINE")

except Exception as e_ia_init:
    st.error(f"FALLA CRÍTICA EN NÚCLEO NEURAL: {e_ia_init}")

# ==============================================================================
# 2. CAPA DE DISEÑO VISUAL "ELITE SUPREMACÍA" (CSS EXTENDIDO)
# ==============================================================================

st.markdown("""
    <style>
    /* Estética General Dark Industrial */
    .main { 
        background-color: #0b0d11; 
        color: #e6edf3; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    }

    .stApp { 
        background-color: #0b0d11; 
    }
    
    /* BLOQUE DE TÍTULO PRINCIPAL EXTENDIDO */
    .title-box { 
        border-left: 20px solid #E30613; 
        padding: 50px 70px; 
        margin: 40px 0 70px 0; 
        background: linear-gradient(90deg, #161b22 0%, rgba(11,13,17,0) 100%);
        border-radius: 0 40px 40px 0;
        box-shadow: 20px 0 50px rgba(0,0,0,0.7);
    }

    .m-title { 
        font-size: 60px; 
        font-weight: 900; 
        color: #ffffff; 
        text-transform: uppercase; 
        letter-spacing: 12px; 
        margin: 0; 
        line-height: 1.1; 
        text-shadow: 5px 5px 10px rgba(0,0,0,1);
    }

    .s-title { 
        font-size: 26px; 
        color: #8b949e; 
        font-family: 'Courier New', monospace; 
        margin-top: 25px; 
        letter-spacing: 5px; 
        font-weight: bold;
    }

    /* ESTILO DE LOS ENCABEZADOS DE MÓDULO */
    .module-header {
        font-size: 32px; 
        font-weight: 700; 
        color: #ffffff;
        margin-top: 40px; 
        margin-bottom: 25px;
        display: flex; 
        align-items: center; 
        gap: 15px;
        border-bottom: 1px solid #30363d; 
        padding-bottom: 15px;
    }

    .sub-header {
        font-size: 20px; 
        font-weight: 600; 
        color: #E30613;
        margin-top: 20px; 
        text-transform: uppercase; 
        letter-spacing: 2px;
    }

    /* ESTILO BS LATAM SIDEBAR */
    .bs-latam-sidebar {
        color: #ffffff; 
        font-weight: 950; 
        font-size: 45px; 
        text-align: center;
        text-transform: uppercase; 
        letter-spacing: 7px;
        text-shadow: 0px 0px 30px #0055ff, 4px 4px 0px #000000;
        margin-bottom: 45px; 
        padding: 25px; 
        border-bottom: 4px solid #E30613;
    }

    /* BOTONERÍA ÉLITE */
    .stButton>button { 
        background: linear-gradient(135deg, #E30613 0%, #9e040d 100%) !important;
        color: #ffffff !important; 
        font-weight: 900 !important; 
        text-transform: uppercase; 
        border-radius: 30px; 
        height: 70px; 
        width: 100%; 
        font-size: 22px !important;
        border: none; 
        box-shadow: 0 10px 20px rgba(227,6,19,0.35);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    .stButton>button:hover {
        transform: scale(1.02) translateY(-4px);
        box-shadow: 0 15px 35px rgba(227,6,19,0.55);
        border: 2px solid #ffffff;
    }
    
    /* INPUTS Y TEXT AREAS MASIVAS */
    .stTextArea textarea, .stTextInput input, .stNumberInput input { 
        background-color: #161b22 !important; 
        color: #e6edf3 !important; 
        border: 2px solid #30363d !important; 
        border-radius: 15px;
        font-size: 16px; 
        padding: 15px;
    }

    .stTextArea textarea:focus, .stTextInput input:focus { 
        border-color: #E30613 !important; 
    }

    /* TABLAS Y DATAFRAMES */
    [data-testid="stDataFrame"] {
        border: 2px solid #30363d; 
        border-radius: 20px; 
        overflow: hidden;
        background-color: #161b22;
    }
    
    /* BLOQUES DE CÓDIGO (Optimización para copiado) */
    .stCodeBlock {
        border: 1px solid #E30613;
        border-radius: 10px;
    }

    /* CONTENEDORES DE ERROR PERSONALIZADOS */
    .error-card {
        background-color: #2d0000;
        border: 1px solid #ff4b4b;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }

    /* MÉTRICAS FLOTANTES */
    .metric-value {
        color: #E30613; 
        font-size: 38px; 
        font-weight: 900;
    }

    /* ESTILO RESUMEN TÁCTICO */
    .tactical-summary {
        background: linear-gradient(135deg, #161b22 0%, #0b0d11 100%);
        border: 1px solid #30363d;
        border-left: 5px solid #E30613;
        padding: 20px;
        border-radius: 10px;
        color: #e6edf3;
        font-family: 'Courier New', monospace;
    }

    .tactical-item { 
        margin-bottom: 8px; 
        display: flex; 
        justify-content: space-between; 
    }

    .tactical-label { 
        color: #8b949e; 
        text-transform: uppercase; 
        font-size: 14px; 
    }

    .tactical-value { 
        color: #ffffff; 
        font-weight: bold; 
        border-bottom: 1px solid #E30613; 
    }
    </style>
    
    <div class="title-box">
        <p class="m-title">AUDIT-ELITE SUPREMACÍA V33.0</p>
        <p class="s-title">SISTEMA INTEGRAL BS LATAM • FB / YT / TK / VISION-IA</p>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. GESTIÓN DE MEMORIA, VARIABLES DE ESTADO Y LOGS
# ==============================================================================

if 'db_final' not in st.session_state: 
    st.session_state.db_final = pd.DataFrame()

if 'db_fallidos' not in st.session_state: 
    st.session_state.db_fallidos = pd.DataFrame()

if 'db_drive_vision' not in st.session_state: 
    st.session_state.db_drive_vision = pd.DataFrame()

if 'chat_log' not in st.session_state:
    st.session_state.chat_log = [
        {"role": "assistant", "content": f"SISTEMA OPERATIVO V33.0 LISTO. Integración Anti-Bloqueos y Motor Facebook activados."}
    ]

# ==============================================================================
# 4. FUNCIONES CORE - LÓGICA DE PROCESAMIENTO MULTI-PLATAFORMA Y MOTOR FACEBOOK
# ==============================================================================

def limpiar_url_táctica(url):
    """Limpia parámetros de rastreo agresivos para evitar fallos de scraping en FB, YT y TK."""
    url = url.strip().replace('"', '').replace("'", "")
    url_l = url.lower()
    
    if "web.facebook.com" in url_l:
        url = re.sub(r"web\.facebook\.com", "www.facebook.com", url, flags=re.IGNORECASE)
    
    if "youtube.com/shorts/" in url_l or "youtu.be/" in url_l:
        url = url.split('?')[0]
    elif "tiktok.com" in url_l:
        url = url.split('?')[0]
    elif "facebook.com" in url_l or "fb.watch" in url_l or "fb.com" in url_l:
        parsed = urllib.parse.urlparse(url)
        if "/watch" in parsed.path.lower() and "v=" in parsed.query.lower():
            v_match = re.search(r"(?:^|&)v=([^&]+)", parsed.query, flags=re.IGNORECASE)
            clean_query = f"v={v_match.group(1)}" if v_match else ""
        else:
            clean_query = ""
        url = urllib.parse.urlunparse(parsed._replace(query=clean_query, fragment=""))
    else:
        parametros_basura = ['?si=', '&pp=', '?mibextid=', '?is_from_webapp=']
        for param in parametros_basura:
            if param in url:
                url = url.split(param)[0]
            
    return url

def obtener_tipo_video(url, info_dict):
    """Determina la categoría exacta del contenido, incluyendo soporte para TikTok Photos/Carousels."""
    url_l = url.lower()
    if "facebook.com" in url_l or "fb.watch" in url_l or "fb.com" in url_l:
        return "Facebook Video"
    
    if "tiktok.com" in url_l or "tiktok" in url_l:
        if "/photo/" in url_l:
            return "TikTok Photo Carousel"
        return "TikTok Video"
    
    if "youtube.com" in url_l or "youtu.be" in url_l or "youtube" in url_l:
        duration = info_dict.get('duration', 0) if info_dict else 0
        if "/shorts/" in url_l or (duration and duration <= 65):
            return "YouTube Shorts"
        return "YouTube Video"
    
    return "Contenido Externo"

def navegar_ia_en_enlace(url):
    """Permite que el sistema 'entre' en un enlace y extraiga texto para la IA."""
    try:
        header_request = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        r = requests.get(url, headers=header_request, timeout=12)
        if r.status_code == 200:
            s = BeautifulSoup(r.text, 'html.parser')
            for tag in s(["script", "style", "header", "footer", "nav"]):
                tag.decompose()
            return s.get_text(separator=' ')[:5000]
        return "Error: No se pudo acceder al sitio."
    except Exception as e:
        return f"Error de conexión: {str(e)}"

def analizar_imagen_con_ia(image_file):
    """Usa Gemini Vision para leer métricas, maneja Ks/Ms y muestra reportes en pantalla."""
    try:
        if 'model_ia' not in globals():
            st.error("🚨 NÚCLEO IA OFFLINE: El modelo no cargó.")
            return 0
            
        img = Image.open(image_file)
        prompt_vision = "Analiza esta imagen. Dime ÚNICAMENTE el número total de vistas (views). Si ves una 'K' o 'M', inclúyela (ejemplo: 5.9K, 1.2M). No agregues texto adicional, solo el número."
        
        response = model_ia.generate_content([prompt_vision, img])
        texto_ia = response.text.strip().lower()
        
        st.warning(f"👁️ Lectura Cruda de la IA: '{texto_ia}'") 
        
        texto_limpio = texto_ia.replace(',', '.') 
        numeros = re.findall(r'[0-9.]+', texto_limpio)
        
        if not numeros:
            return 0 
            
        valor_base = float(numeros[0])
        
        if 'k' in texto_limpio:
            return int(valor_base * 1000)
        elif 'm' in texto_limpio:
            return int(valor_base * 1000000)
        else:
            return int(valor_base)
            
    except Exception as e_vision:
        st.error(f"❌ FALLO EN LECTURA ÓPTICA (VISION): {str(e_vision)}")
        return 0

def analizar_imagen_drive_con_ia(url_drive):
    """Módulo Vision Avanzado: Descarga capturas desde Google Drive público y extrae vistas con IA."""
    try:
        file_id = re.findall(r'[-\w]{25,}', url_drive)
        if not file_id: 
            return 0, "ID de Drive no encontrado en la URL"
        
        url_download = f"https://drive.google.com/uc?export=download&id={file_id[0]}"
        response = requests.get(url_download, timeout=15)
        
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            prompt_vision = (
                "Actúa como un validador experto en auditoría visual de BS LATAM. "
                "Analiza esta captura de pantalla de métricas de redes sociales. "
                "Localiza y extrae únicamente el número total de VISTAS (Views o Reproducciones). "
                "Responde de forma estricta el número entero puro, sin letras, espacios, ni caracteres adicionales."
            )
            res = model_ia.generate_content([prompt_vision, img])
            texto_limpio = re.sub(r'[^0-9]', '', res.text)
            return int(texto_limpio) if texto_limpio else 0, "Éxito"
        else:
            return 0, f"Error de descarga: Código HTTP {response.status_code}. Asegúrate de que el enlace sea público."
    except Exception as e:
        return 0, str(e)

def convertir_k_m(valor_str):
    """Convierte strings de métricas ('2,2 mil', '6.1K', '1.2M', '12.345') a enteros reales."""
    if valor_str is None:
        return 0
    if isinstance(valor_str, (int, float)):
        return int(valor_str)
    s = str(valor_str).strip().lower()
    if not s:
        return 0
    s = re.sub(r"\s+", " ", s)

    match = re.search(r"(\d+(?:[.,]\d+)?)\s*(mil|k|m|millones|millón)?\b", s)
    if not match:
        return 0

    num_str, suffix = match.groups()
    suffix = suffix or ""

    if suffix in ("mil", "k", "m", "millones", "millón"):
        val = float(num_str.replace(",", "."))
        if suffix in ("mil", "k"):
            return int(round(val * 1_000))
        return int(round(val * 1_000_000))

    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", num_str):
        return int(re.sub(r"[.,]", "", num_str))

    try:
        return int(round(float(num_str.replace(",", "."))))
    except ValueError:
        return 0

# ==============================================================================
# MOTOR DEDICADO DE FACEBOOK (RESCATE DE MÉTRICAS, CREADOR, TÍTULO Y FALLBACK)
# ==============================================================================

def rescatar_metricas_texto_fb(texto):
    """
    Rescata reproducciones/vistas, likes/reacciones y comentarios desde cadenas tipo:
    '2,2 mil reproducciones · 64 reacciones · 10 comentarios'
    """
    out = {"views": None, "likes": None, "comments": None}
    if not texto:
        return out

    m_views = re.search(
        r"(\d+(?:[.,]\d+)?\s*(?:mil|k|m|millones|millón)?)\s*(?:reproducciones|vistas|views|plays)",
        texto,
        flags=re.IGNORECASE,
    )
    if m_views:
        out["views"] = convertir_k_m(m_views.group(1))

    m_likes = re.search(
        r"(\d+(?:[.,]\d+)?\s*(?:mil|k|m|millones|millón)?)\s*(?:reacciones|me gusta|likes|reactions)",
        texto,
        flags=re.IGNORECASE,
    )
    if m_likes:
        out["likes"] = convertir_k_m(m_likes.group(1))

    m_comments = re.search(
        r"(\d+(?:[.,]\d+)?\s*(?:mil|k|m|millones|millón)?)\s*(?:comentarios|comments)",
        texto,
        flags=re.IGNORECASE,
    )
    if m_comments:
        out["comments"] = convertir_k_m(m_comments.group(1))

    return out

def es_solo_metricas_fb(texto):
    """Detecta si una cadena es un resumen de métricas en vez del nombre de un creador o título real."""
    if not texto:
        return False
    t = str(texto).strip().lower()
    keywords = (
        "reproducciones", "vistas", "views", "plays",
        "reacciones", "me gusta", "likes", "reactions",
        "comentarios", "comments"
    )
    has_kw = any(k in t for k in keywords)
    has_num = re.search(r"\d", t) is not None
    stripped = re.sub(
        r"\d+(?:[.,]\d+)?\s*(?:mil|k|m|millones|millón)?\s*(?:reproducciones|vistas|views|plays|reacciones|me gusta|likes|reactions|comentarios|comments)?|[·•|,/-]",
        "",
        t,
        flags=re.IGNORECASE,
    ).strip()
    return has_kw and has_num and len(stripped) < 14

def normalizar_campos_fb(creator, title, views, likes, comments):
    """
    Limpia campos de Facebook y reubica métricas que hayan caído en 'creator' o 'title'
    hacia sus columnas correspondientes ('Vistas', 'Likes', 'Comments').
    """
    for fuente in (creator, title):
        if fuente:
            rescatado = rescatar_metricas_texto_fb(fuente)
            if (views is None or views == 0) and rescatado["views"] is not None:
                views = rescatado["views"]
            if (likes is None or likes == 0) and rescatado["likes"] is not None:
                likes = rescatado["likes"]
            if (comments is None or comments == 0) and rescatado["comments"] is not None:
                comments = rescatado["comments"]

    creador_limpio = creator.strip() if isinstance(creator, str) and creator.strip() else None
    if creador_limpio:
        if es_solo_metricas_fb(creador_limpio):
            creador_limpio = None
        else:
            for sep in ("·", "•", "|"):
                if sep in creador_limpio:
                    partes = [p.strip() for p in creador_limpio.split(sep) if p.strip()]
                    candidatos = [p for p in partes if not es_solo_metricas_fb(p)]
                    creador_limpio = candidatos[0] if candidatos else None
                    break

    titulo_limpio = title.strip() if isinstance(title, str) and title.strip() else None
    if titulo_limpio and es_solo_metricas_fb(titulo_limpio):
        titulo_limpio = None

    return (
        creador_limpio or "N/A",
        titulo_limpio or "N/A",
        int(views or 0),
        int(likes or 0),
        int(comments or 0),
    )

def diagnosticar_bloqueo_fb(html, final_url):
    """Detecta si Facebook redirigió a login, checkpoint o bloqueo de página."""
    lower = (html or "").lower()
    path = urllib.parse.urlparse(final_url or "").path.lower()
    if "login" in path and "reel" not in path and "watch" not in path:
        return "Redirigido a login"
    if len(html or "") < 1500 and ("iniciar sesión" in lower or "log in" in lower):
        return "Pantalla de login / bloqueo"
    if "checkpoint" in lower:
        return "Checkpoint de seguridad FB"
    return None

def extraer_fb_desde_html(url, html, final_url):
    """Extrae creador, título, vistas, likes y comentarios desde HTML/JSON de Facebook."""
    soup = BeautifulSoup(html, "html.parser")
    creator = None
    title = None
    views = None
    likes = None
    comments = None

    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()

    og_desc = soup.find("meta", property="og:description")
    desc_text = og_desc["content"].strip() if og_desc and og_desc.get("content") else ""

    if title and "|" in title:
        partes = [p.strip() for p in title.split("|")]
        if len(partes) >= 2 and "facebook" not in partes[0].lower():
            creator = partes[0]
            title = " | ".join(partes[1:]).replace("en Facebook", "").strip()

    if desc_text:
        d_res = rescatar_metricas_texto_fb(desc_text)
        views = d_res["views"]
        likes = d_res["likes"]
        comments = d_res["comments"]

    patrones_vistas = [
        r'"video_view_count"\s*:\s*(\d+)',
        r'"play_count"\s*:\s*(\d+)',
        r'"view_count"\s*:\s*(\d+)',
        r'(\d+(?:[.,]\d+)?\s*(?:mil|k|m|millones|millón)?)\s*(?:reproducciones|vistas|views)',
    ]
    for pat in patrones_vistas:
        m = re.search(pat, html, flags=re.IGNORECASE)
        if m:
            val = convertir_k_m(m.group(1))
            if val > 0:
                views = val
                break

    patrones_likes = [
        r'"reaction_count"\s*:\s*\{\s*"count"\s*:\s*(\d+)',
        r'"like_count"\s*:\s*(\d+)',
        r'(\d+(?:[.,]\d+)?\s*(?:mil|k|m|millones|millón)?)\s*(?:reacciones|me gusta|likes)',
    ]
    for pat in patrones_likes:
        m = re.search(pat, html, flags=re.IGNORECASE)
        if m:
            val = convertir_k_m(m.group(1))
            if val > 0:
                likes = val
                break

    patrones_comments = [
        r'"comment_count"\s*:\s*\{\s*"total_count"\s*:\s*(\d+)',
        r'"comments_count"\s*:\s*(\d+)',
        r'(\d+(?:[.,]\d+)?\s*(?:mil|k|m|millones|millón)?)\s*(?:comentarios|comments)',
    ]
    for pat in patrones_comments:
        m = re.search(pat, html, flags=re.IGNORECASE)
        if m:
            val = convertir_k_m(m.group(1))
            if val > 0:
                comments = val
                break

    if not creator:
        m_owner = re.search(r'"owner"\s*:\s*\{[^}]{0,200}?"name"\s*:\s*"([^"]+)"', html)
        if m_owner:
            creator = m_owner.group(1).encode("utf-8").decode("unicode_escape", errors="ignore").strip()

    if not title and desc_text and not es_solo_metricas_fb(desc_text):
        title = desc_text[:140]

    creator_f, title_f, views_f, likes_f, comments_f = normalizar_campos_fb(
        creator, title, views, likes, comments
    )

    diag = diagnosticar_bloqueo_fb(html, final_url)
    tiene_algo = any([
        creator_f != "N/A",
        title_f != "N/A",
        views_f > 0,
        likes_f > 0,
        comments_f > 0,
    ])
    if not tiene_algo:
        return None, diag or "Sin datos legibles en HTML de Facebook"

    return {
        "Fecha": "N/A",
        "Plataforma": "FACEBOOK",
        "Tipo": "Facebook Video (Motor FB)",
        "Creador": creator_f,
        "Título": title_f[:65],
        "Vistas": views_f,
        "Likes": likes_f,
        "Comments": comments_f,
        "Saves": 0,
        "Link": url,
    }, None

def motor_facebook_rescate(url, headers):
    """Intenta extraer datos de Facebook probando URL limpia y respaldo móvil."""
    candidatos = [url]
    if "www.facebook.com" in url:
        candidatos.append(url.replace("www.facebook.com", "m.facebook.com", 1))

    ultimo_error = "Fallo desconocido en Facebook"
    for target in candidatos:
        try:
            resp = requests.get(target, headers=headers, timeout=12, allow_redirects=True)
            resp.raise_for_status()
            data, err = extraer_fb_desde_html(url, resp.text, resp.url)
            if data:
                return data, None
            ultimo_error = f"{err} ({target})"
        except requests.HTTPError as exc:
            code = exc.response.status_code if exc.response is not None else "?"
            ultimo_error = f"HTTPError {code} ({target})"
        except Exception as exc:
            ultimo_error = f"{type(exc).__name__} ({target})"

    return None, ultimo_error

# ==============================================================================
# SISTEMA DE RESCATE: EXTRACCIÓN HTML DIRECTA PARA BYPASS YOUTUBE/TIKTOK/FB
# ==============================================================================
def extraccion_html_emergencia(url):
    """Fallback directo mediante Web Scraping cuando la API yt-dlp es bloqueada."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'es-419,es;q=0.9,pt-BR;q=0.8,ar;q=0.7,en;q=0.6',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    tipo = obtener_tipo_video(url, {})
    plataforma = tipo.split(' ')[0].upper()

    if plataforma == "FACEBOOK":
        return motor_facebook_rescate(url, headers)

    try:
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code != 200:
            return None, f"Servidor rechazó conexión (HTTP {res.status_code})"
            
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')
        
        t_tag = soup.find("meta", property="og:title")
        titulo = t_tag["content"] if t_tag else soup.title.string if soup.title else "Título no recuperable"
        
        vistas = 0
        if "youtube" in url.lower() or "youtu.be" in url.lower():
            v_match = re.search(r'"viewCount":"(\d+)"', html)
            if v_match: vistas = int(v_match.group(1))
        elif "tiktok" in url.lower():
            v_match = re.search(r'"playCount":(\d+)', html)
            if v_match: vistas = int(v_match.group(1))
            
        return {
            "Fecha": "N/A", "Plataforma": plataforma, "Tipo": tipo + " (Rescate HTML)",
            "Creador": "Extraído por HTML", "Título": str(titulo)[:65],
            "Vistas": vistas, "Likes": 0, "Comments": 0, "Saves": 0, "Link": url
        }, None
    except Exception as e:
        return None, str(e)

def motor_auditor_universal_v32(urls):
    """Core de scraping masivo con blindaje anti-bloqueos regional y motor Facebook avanzado."""
    resultados = []
    fallidos = []
    
    p_bar = st.progress(0)
    status_text = st.empty()
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
    ]

    for i, raw_url in enumerate(urls):
        url = limpiar_url_táctica(raw_url)
        status_text.markdown(f"🔍 **AUDITANDO (#{i+1}):** `{url[:50]}...`")
        
        ydl_opts = {
            'quiet': True,
            'ignoreerrors': True,
            'skip_download': True,
            'no_warnings': True,
            'extract_flat': False,
            'socket_timeout': 15,
            'retries': 3,
            'nocheckcertificate': True, 
            'geo_bypass': True,
            'extractor_args': {'youtube': {'player_client': ['web', 'mweb']}},
            'http_headers': {
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
            }
        }
        
        exito_extraccion = False
        registro_parcial_fb = None

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info:
                    titulo_raw = str(info.get('title') or info.get('description') or 'N/A')
                    creador_raw = str(info.get('uploader') or info.get('channel') or 'N/A')
                    vistas = int(info.get('view_count') or 0)
                    likes = int(info.get('like_count') or 0)
                    comments = int(info.get('comment_count') or 0)
                    saves = int(info.get('repost_count') or 0)
                    tipo = obtener_tipo_video(url, info)
                    plataforma = tipo.split(' ')[0].upper()

                    if plataforma == 'FACEBOOK':
                        match_fb = re.search(r"([\d.,]+\s*(?:mil|KMkm)?)\s*views.*?([\d.,]+\s*(?:mil|KMkm)?)\s*reactions\s*\|\s*(.*)", titulo_raw, re.IGNORECASE)
                        if match_fb:
                            vistas = convertir_k_m(match_fb.group(1))
                            likes = convertir_k_m(match_fb.group(2))
                            titulo_raw = match_fb.group(3).strip()
                        else:
                            match_fb_views = re.search(r"([\d.,]+\s*(?:mil|KMkm)?)\s*views\s*\|\s*(.*)", titulo_raw, re.IGNORECASE)
                            if match_fb_views:
                                vistas = convertir_k_m(match_fb_views.group(1))
                                titulo_raw = match_fb_views.group(2).strip()

                        creador_raw, titulo_raw, vistas, likes, comments = normalizar_campos_fb(
                            creador_raw, titulo_raw, vistas, likes, comments
                        )

                    raw_date = info.get('upload_date', 'N/A')
                    if raw_date and raw_date != 'N/A' and len(str(raw_date)) == 8:
                        raw_date_s = str(raw_date)
                        fecha_formateada = f"{raw_date_s[6:8]}/{raw_date_s[4:6]}/{raw_date_s[2:4]}"
                    else:
                        fecha_formateada = str(raw_date)

                    registro = {
                        "ID": i + 1,
                        "Fecha": fecha_formateada,
                        "Plataforma": plataforma,
                        "Tipo": tipo,
                        "Creador": creador_raw,
                        "Título": titulo_raw[:65],
                        "Vistas": vistas,
                        "Likes": likes,
                        "Comments": comments,
                        "Saves": saves,
                        "Link": url
                    }

                    if plataforma == 'FACEBOOK' and (vistas == 0 or creador_raw == 'N/A' or likes == 0):
                        registro_parcial_fb = registro
                    else:
                        resultados.append(registro)
                        exito_extraccion = True
        except Exception:
            pass
        
        if not exito_extraccion:
            status_text.markdown(f"⚠️ **Refinando extracción / rescate HTML para:** `{url[:40]}...`")
            data_html, error_html = extraccion_html_emergencia(url)
            
            if data_html and registro_parcial_fb:
                if data_html["Vistas"] == 0 and registro_parcial_fb["Vistas"] > 0:
                    data_html["Vistas"] = registro_parcial_fb["Vistas"]
                if data_html["Likes"] == 0 and registro_parcial_fb["Likes"] > 0:
                    data_html["Likes"] = registro_parcial_fb["Likes"]
                if data_html["Comments"] == 0 and registro_parcial_fb["Comments"] > 0:
                    data_html["Comments"] = registro_parcial_fb["Comments"]
                if data_html["Creador"] == "N/A" and registro_parcial_fb["Creador"] != "N/A":
                    data_html["Creador"] = registro_parcial_fb["Creador"]
                if data_html["Título"] == "N/A" and registro_parcial_fb["Título"] != "N/A":
                    data_html["Título"] = registro_parcial_fb["Título"]
                if registro_parcial_fb["Fecha"] != "N/A":
                    data_html["Fecha"] = registro_parcial_fb["Fecha"]
                data_html["Tipo"] = "Facebook Video (Híbrido)"

            if data_html:
                data_html["ID"] = i + 1
                resultados.append(data_html)
            elif registro_parcial_fb:
                resultados.append(registro_parcial_fb)
            else:
                fallidos.append({"ID": i + 1, "Link": raw_url, "Error": f"Bloqueo Bot y Fallo HTML: {error_html}"[:55]})

        p_bar.progress((i + 1) / len(urls))
    
    p_bar.empty()
    status_text.empty()
    return pd.DataFrame(resultados), pd.DataFrame(fallidos)

def motor_busqueda_temporal(urls_canales, f_start, f_end, min_views):
    """MOTOR REPARADO: Se eliminan pausas innecesarias y se blindan las cabeceras para máxima velocidad."""
    resultados = []
    d_start = int(f_start.strftime('%Y%m%d'))
    d_end = int(f_end.strftime('%Y%m%d'))
    
    p_bar = st.progress(0)
    status = st.empty()
    
    ydl_opts_search = {
        'quiet': True,
        'ignoreerrors': True,
        'extract_flat': True,
        'playlistend': 50,
        'socket_timeout': 15,
        'retries': 3,
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        }
    }
    
    for i, url in enumerate(urls_canales):
        url = url.strip()
        if not url: continue
        
        url_lower = url.lower()
        if "facebook.com" in url_lower and "/videos" not in url_lower and "watch" not in url_lower:
            if not url.endswith("/"):
                url += "/"
            url += "videos/"
        elif "youtube.com" in url_lower and "@" in url_lower and "/videos" not in url_lower and "/shorts" not in url_lower:
            if not url.endswith("/"):
                url += "/"
            url += "videos"

        status.markdown(f"🛰️ **ESCANEO RADAR:** Analizando feed de `{url[:40]}...`")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts_search) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info and 'entries' in info:
                    videos = info['entries']
                    for vid in videos:
                        if not vid: continue
                        
                        v_date_str = vid.get('upload_date')
                        if not v_date_str and vid.get('timestamp'):
                            v_date_str = datetime.datetime.fromtimestamp(vid.get('timestamp')).strftime('%Y%m%d')
                        
                        v_views = vid.get('view_count')
                        
                        if v_date_str and v_views is not None:
                            v_date_int = int(v_date_str)
                            
                            if d_start <= v_date_int <= d_end:
                                if int(v_views) >= min_views:
                                    
                                    f_radar = f"{v_date_str[6:8]}/{v_date_str[4:6]}/{v_date_str[2:4]}" if len(str(v_date_str)) == 8 else str(v_date_str)

                                    resultados.append({
                                        "Fecha": f_radar,
                                        "Canal/Fuente": info.get('title', 'N/A'),
                                        "Título Video": vid.get('title', 'N/A')[:60],
                                        "Vistas": int(v_views),
                                        "Likes": int(vid.get('like_count') or 0),
                                        "Comments": int(vid.get('comment_count') or 0),
                                        "Saves": int(vid.get('repost_count') or 0),
                                        "Link": vid.get('url') or vid.get('webpage_url') or url
                                    })
                else:
                    print(f"No se pudieron extraer entradas de: {url}")
        except Exception as e:
            print(f"Error en canal {url}: {e}")
            
        p_bar.progress((i + 1) / len(urls_canales))

    p_bar.empty()
    status.empty()
    return pd.DataFrame(resultados)

# ==============================================================================
# 5. SIDEBAR - CONTROL DE MISIONES
# ==============================================================================

with st.sidebar:
    st.markdown('<p class="bs-latam-sidebar">BS LATAM</p>', unsafe_allow_html=True)
    
    modulo = st.radio(
        "MÓDULOS OPERATIVOS", 
        ["🚀 EXTRACTOR ELITE", "📂 DRIVE AUDITOR (VISION)", "🤖 PARTNER IA", "🛰️ SEARCH PRO", "✅ VERIFICADOR ENLACES"],
        index=0
    )
    
    st.divider()
    
    if st.button("🚨 REINICIO DE CACHÉ"):
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    st.caption(f"VERSIÓN: 33.0-ELITE")
    st.caption(f"ÚLTIMO SYNC: {datetime.datetime.now().strftime('%H:%M:%S')}")

# ==============================================================================
# 6. MÓDULO 1: EXTRACTOR ELITE (MODO MULTI-PLATAFORMA)
# ==============================================================================

if modulo == "🚀 EXTRACTOR ELITE":
    st.markdown('<div class="module-header">📥 Extractor de Métricas Masivas</div>', unsafe_allow_html=True)
    
    texto_entrada = st.text_area(
        "Pega los enlaces (uno por línea o separados por espacios):", 
        height=250, 
        placeholder="www.tiktok.com/... \nhttps://web.facebook.com/reel/..."
    )
    
    c_btn1, c_btn2 = st.columns([1, 4])
    with c_btn1:
        ejecutar = st.button("🔥 EJECUTAR AUDITORÍA")
    
    if ejecutar:
        raw_words = texto_entrada.replace(',', ' ').replace('\n', ' ').split()
        urls_detectadas = []
        for word in raw_words:
            word = word.strip('"\'()[]')
            wl = word.lower()
            
            if any(domain in wl for domain in ['tiktok', 'fb.watch', 'facebook', 'fb.com', 'youtube', 'youtu.be']):
                if not word.startswith('http'):
                    word = 'https://' + word
                urls_detectadas.append(word)
        
        if urls_detectadas:
            res, fails = motor_auditor_universal_v32(urls_detectadas)
            st.session_state.db_final = res
            st.session_state.db_fallidos = fails
            
            if not res.empty:
                st.success(f"PROCESO FINALIZADO: {len(res)} registros extraídos con éxito.")
            if not fails.empty:
                st.warning(f"AVISO: {len(fails)} enlaces presentaron anomalías.")
        else:
            st.error("ERROR: No se detectaron URLs válidas en el campo de texto. Asegúrate de pegar links de FB, TK o YT.")

    # --- ZONA DE VISUALIZACIÓN DE RESULTADOS ---
    
    if not st.session_state.db_fallidos.empty:
        with st.expander("⚠️ VER ENLACES NO PROCESADOS / ERRORES"):
            st.markdown('<div class="error-card">', unsafe_allow_html=True)
            st.dataframe(st.session_state.db_fallidos, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

    if not st.session_state.db_final.empty:
        df = st.session_state.db_final.copy()
        
        # --- NÚCLEO MATEMÁTICO: APLICACIÓN DEL FACTOR X3 A YT LARGOS ---
        df['Vistas_Calc'] = df.apply(
            lambda row: int(row['Vistas'] * 3) if row['Tipo'] == 'YouTube Video' else int(row['Vistas']), 
            axis=1
        )
        
        st.divider()
        st.markdown('<div class="sub-header">📊 DATOS EXTRAÍDOS (MULTI-PLATAFORMA)</div>', unsafe_allow_html=True)
        st.dataframe(df.drop(columns=['Vistas_Calc']), use_container_width=True, hide_index=True)

        csv_export = df.drop(columns=['Vistas_Calc']).to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="💾 DESCARGAR HOJA DE CÁLCULO (CSV)",
            data=csv_export,
            file_name=f"Reporte_BS_LATAM_{datetime.datetime.now().strftime('%d_%m_%y_%H%M')}.csv",
            mime="text/csv",
        )

        st.markdown('<div class="module-header">📋 CENTRO DE COPIADO Y FÓRMULAS</div>', unsafe_allow_html=True)
        
        df_yt_v = df[df['Tipo'] == 'YouTube Video']
        df_shorts = df[df['Tipo'] == 'YouTube Shorts']
        df_fb = df[df['Plataforma'] == 'FACEBOOK']
        df_tk = df[df['Plataforma'] == 'TIKTOK']

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"**TOTAL VISTAS (PONDERADO)**\n## {df['Vistas_Calc'].sum():,}")
        with m2:
            st.markdown(f"**YT LARGOS (x3 APLICADO)**\n## {df_yt_v['Vistas_Calc'].sum():,}")
        with m3:
            st.markdown(f"**FACEBOOK**\n## {df_fb['Vistas'].sum():,}")
        with m4:
            st.markdown(f"**TIKTOK**\n## {df_tk['Vistas'].sum():,}")

        st.divider()
        st.markdown("### 📥 Bloques de Texto para Copiar")
        
        col_copy1, col_copy2 = st.columns(2)
        
        with col_copy1:
            st.markdown("**1. FÓRMULA YT LARGOS (X+Y+Z) [YA MULTIPLICADO X3]**")
            f_yt_largos = "+".join(df_yt_v['Vistas_Calc'].astype(str).tolist())
            st.code(f_yt_largos if f_yt_largos else "0", language="text")
            
            st.markdown("**2. FÓRMULA FACEBOOK (X+Y+Z)**")
            f_fb_str = "+".join(df_fb['Vistas'].astype(str).tolist())
            st.code(f_fb_str if f_fb_str else "0", language="text")
            
            st.markdown("**3. FÓRMULA YT SHORTS (X+Y+Z)**")
            f_shorts_str = "+".join(df_shorts['Vistas'].astype(str).tolist())
            st.code(f_shorts_str if f_shorts_str else "0", language="text")

            st.markdown("**4. VISTAS TOTALES DE TODO (SUMA GLOBAL PONDERADA)**")
            f_total_todo = "+".join(df['Vistas_Calc'].astype(str).tolist())
            st.code(f_total_todo if f_total_todo else "0", language="text")

        with col_copy2:
            st.markdown("**5. FÓRMULA TIKTOK (X+Y+Z)**")
            f_tk_str = "+".join(df_tk['Vistas'].astype(str).tolist())
            st.code(f_tk_str if f_tk_str else "0", language="text")

            st.markdown("**6. FÓRMULA TOTAL GENERAL**")
            st.code(f_total_todo if f_total_todo else "0", language="text")
            
            st.divider()
            st.markdown("### 🚀 CÁLCULO ESTELAR (YT + RESTO)")
            
            val_yt_long_x3 = df_yt_v['Vistas_Calc'].sum()
            val_resto = df[df['Tipo'] != 'YouTube Video']['Vistas_Calc'].sum()
            val_booster = val_yt_long_x3 + val_resto
            
            st.markdown(f"""
            <div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #E30613;">
                <span style="color:#8b949e;">LÓGICA:</span> (YT Largos x3: <b>{val_yt_long_x3:,}</b>) + Resto Global: <b>{val_resto:,}</b>
                <br>
                <span style="color:#ffffff; font-size:24px; font-weight:bold;">RESULTADO FINAL: {val_booster:,}</span>
            </div>
            """, unsafe_allow_html=True)
            st.code(f"{val_booster}", language="text")

            st.markdown("**7. RESUMEN TÁCTICO DE OPERACIÓN**")
            st.markdown(f"""
                <div class="tactical-summary">
                    <div class="tactical-item"><span class="tactical-label">Protocolo:</span><span class="tactical-value">BS LATAM AUDIT ELITE</span></div>
                    <div class="tactical-item"><span class="tactical-label">Exitosos:</span><span class="tactical-value">{len(df)}</span></div>
                    <div class="tactical-item"><span class="tactical-label">YouTube Largos (x3):</span><span class="tactical-value">{val_yt_long_x3:,}</span></div>
                    <div class="tactical-item"><span class="tactical-label">YouTube Shorts (x1):</span><span class="tactical-value">{df_shorts['Vistas'].sum():,}</span></div>
                    <div class="tactical-item"><span class="tactical-label">Facebook:</span><span class="tactical-value">{df_fb['Vistas'].sum():,}</span></div>
                    <div class="tactical-item"><span class="tactical-label">TikTok:</span><span class="tactical-value">{df_tk['Vistas'].sum():,}</span></div>
                    <div style="border-top: 1px dashed #E30613; margin-top: 10px; padding-top: 10px;" class="tactical-item">
                        <span class="tactical-label" style="color:#E30613;">Acumulado Ponderado:</span>
                        <span class="tactical-value" style="font-size: 18px;">{df['Vistas_Calc'].sum():,}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# 7. MÓDULO 2: DRIVE AUDITOR (VISION IA + NAVEGACIÓN INTEGRADAS)
# ==============================================================================

elif modulo == "📂 DRIVE AUDITOR (VISION)":
    st.markdown('<div class="module-header">👁️ Auditor Visual y de Enlaces</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sub-header">🔗 Auditoría Automatizada de Capturas por Enlace de Google Drive</div>', unsafe_allow_html=True)
    entrada_enlaces_drive = st.text_area(
        "Pega aquí los enlaces de Google Drive (La IA descargará el contenido y procesará la métrica mediante visión artificial):", 
        height=150, 
        placeholder="Pega múltiples enlaces de Drive públicos aquí (uno por línea o separados por espacios)..."
    )
    
    st.divider()
    
    st.markdown('<div class="sub-header">📸 Auditoría por Evidencia Visual Local (OCR)</div>', unsafe_allow_html=True)
    up_files = st.file_uploader("Arrastra las evidencias locales aquí:", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True)
    
    if st.button("🧠 INICIAR AUDITORÍA PROFUNDA"):
        v_results_final = []
        
        raw_urls = entrada_enlaces_drive.replace(',', ' ').replace('\n', ' ').split()
        urls_drive = []
        for u in raw_urls:
            u = u.strip('"\'()[]')
            if "." in u:  
                if not u.startswith('http'):
                    u = 'https://' + u
                urls_drive.append(u)
        
        if urls_drive:
            for u in urls_drive:
                if "drive.google.com" in u.lower():
                    with st.spinner(f"IA Descargando y escaneando captura de Drive..."):
                        vistas_drive, status_drive = analizar_imagen_drive_con_ia(u)
                        v_results_final.append({
                            "Fecha": "Drive Vision IA", 
                            "Plataforma": "DRIVE", 
                            "Tipo": "Captura Automática", 
                            "Creador": "N/A", 
                            "Título": f"Asset Drive Visual", 
                            "Vistas": vistas_drive, 
                            "Link": u
                        })
                else:
                    with st.spinner(f"IA Navegando en {u[:30]}..."):
                        texto_web = navegar_ia_en_enlace(u)
                        prompt_ia_link = f"Analiza este texto extraído de una web y busca el número de VISTAS o REPRODUCCIONES. Solo responde el número: {texto_web}"
                        res_ia_link = model_ia.generate_content(prompt_ia_link)
                        vistas_final = re.sub(r'[^0-9]', '', res_ia_link.text)
                        
                        v_results_final.append({
                            "Fecha": "Enlace IA", "Plataforma": "LINK", "Tipo": "Scraping IA", 
                            "Creador": "N/A", "Título": u[:50], 
                            "Vistas": int(vistas_final) if vistas_final else 0, "Link": u
                        })

        if up_files:
            v_bar = st.progress(0)
            for idx, f in enumerate(up_files):
                v_img = analizar_imagen_con_ia(f)
                v_results_final.append({
                    "Fecha": "OCR IA", "Plataforma": "VISION", "Tipo": "Captura Local", 
                    "Creador": "N/A", "Título": f.name, "Vistas": v_img, "Link": "Archivo Local"
                })
                v_bar.progress((idx + 1) / len(up_files))
        
        st.session_state.db_drive_vision = pd.DataFrame(v_results_final)
        st.success("Análisis Profundo Completado.")

    if not st.session_state.db_drive_vision.empty:
        st.markdown('<div class="sub-header">📊 DATA CONSOLIDADA DRIVE/VISION</div>', unsafe_allow_html=True)
        st.dataframe(st.session_state.db_drive_vision, use_container_width=True, hide_index=True)
        f_ia = "+".join(st.session_state.db_drive_vision['Vistas'].astype(str).tolist())
        st.markdown("**FÓRMULA DE SUMA DRIVE/VISION**")
        st.code(f_ia, language="text")

# ==============================================================================
# 8. MÓDULO 3: PARTNER IA (CON VALIDACIÓN DE CONEXIÓN)
# ==============================================================================

elif modulo == "🤖 PARTNER IA":
    st.markdown('<div class="module-header">🤖 Partner IA - Consultor Estratégico</div>', unsafe_allow_html=True)
    
    for msg in st.session_state.chat_log:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if p_user := st.chat_input("Instrucción técnica..."):
        st.session_state.chat_log.append({"role": "user", "content": p_user})
        with st.chat_message("user"): 
            st.markdown(p_user)
        
        with st.chat_message("assistant"):
            try:
                if not GEMINI_API_KEY or GEMINI_API_KEY == "TU_LLAVE_AQUI":
                    st.error("ERROR: API KEY no configurada. Verifica tus Secretos.")
                else:
                    ventana = st.session_state.chat_log[-6:]
                    gemini_history = []
                    for msg in ventana[:-1]: 
                        if "SISTEMA OPERATIVO" in msg["content"]: continue
                        rol = "user" if msg["role"] == "user" else "model"
                        gemini_history.append({"role": rol, "parts": [msg["content"]]})
                    
                    chat = model_ia.start_chat(history=gemini_history)
                    response = chat.send_message(p_user)
                    
                    if response and response.text:
                        texto_ia = response.text
                        st.markdown(texto_ia)
                        st.session_state.chat_log.append({"role": "assistant", "content": texto_ia})
                    else:
                        st.warning("La IA respondió vacío. Reintenta.")
            
            except Exception as e_chat:
                st.error(f"FALLO DE CONEXIÓN CON GEMINI: {str(e_chat)}")
                st.info("💡 Tip: Verifica que tu API Key sea válida en los 'Secrets' de Streamlit.")

# ==============================================================================
# 9. MÓDULO 4: SEARCH PRO (SISTEMA RADAR TEMPORAL)
# ==============================================================================

elif modulo == "🛰️ SEARCH PRO":
    st.markdown('<div class="module-header">🚀 Radar de Canales (Motor Temporal)</div>', unsafe_allow_html=True)
    st.markdown("Pega los enlaces de canales o perfiles de **TikTok, YouTube o Facebook**. El sistema buscará videos dentro de las fechas indicadas.")
    
    area_search = st.text_area("Canales a rastrear (uno por línea o separados por espacios):", height=150, placeholder="https://youtube.com/@CanalX\nhttps://facebook.com/PaginaY\nhttps://tiktok.com/@UserZ")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    f_inicio = col_s1.date_input("Desde:", value=datetime.date(2026, 2, 1))
    f_fin = col_s2.date_input("Hasta:", value=datetime.date(2026, 2, 28))
    v_umbral = col_s3.number_input("Vistas Mínimas (Filtro):", value=1000)

    if st.button("🚀 ACTIVAR BARRIDO TEMPORAL"):
        raw_perfiles = area_search.replace(',', ' ').replace('\n', ' ').split()
        perfiles = []
        for p in raw_perfiles:
            p = p.strip('"\'()[]')
            if "." in p:
                if not p.startswith('http'):
                    p = 'https://' + p
                perfiles.append(p)
        
        if perfiles:
            with st.status("📡 Escaneando feeds de contenido...", expanded=True) as status:
                st.write(f"Iniciando extracción profunda en {len(perfiles)} canales...")
                st.write("Aplicando protocolos multiplataforma (FB / YT / TK)...")
                
                res_search = motor_busqueda_temporal(perfiles, f_inicio, f_fin, v_umbral)
                
                status.update(label="✅ Escaneo Completado", state="complete", expanded=False)
            
            if not res_search.empty:
                st.markdown('<div class="sub-header">📊 VIDEOS DETECTADOS (FILTRADOS)</div>', unsafe_allow_html=True)
                st.dataframe(res_search, use_container_width=True, hide_index=True)
                
                st.markdown('<div class="tactical-summary">', unsafe_allow_html=True)
                total_radar = res_search['Vistas'].sum()
                st.markdown(f"**VISTAS TOTALES ENCONTRADAS:** {total_radar:,}")
                st.markdown(f"**TOTAL VIDEOS:** {len(res_search)}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("**FÓRMULA TOTAL COPIABLE:**")
                f_search_total = "+".join(res_search['Vistas'].astype(str).tolist())
                st.code(f_search_total if f_search_total else "0", language="text")
            else:
                st.warning("No se encontraron videos que cumplan con los filtros. Si el perfil tiene videos, prueba bajando el umbral de vistas a 0 o revisa que el link sea público.")
        else:
            st.error("Error: Debe ingresar al menos un canal para el radar.")

# ==============================================================================
# 10. MÓDULO 5: VERIFICADOR DE ENLACES (ESTADO DE RED OPTIMIZADO)
# ==============================================================================

elif modulo == "✅ VERIFICADOR ENLACES":
    st.markdown('<div class="module-header">✅ Verificador de Enlaces (Scraping Directo)</div>', unsafe_allow_html=True)
    st.markdown("Verifica rápidamente la existencia real del enlace conectándose directamente al código HTML, saltando restricciones de bots.")
    
    texto_verificar = st.text_area("Pega los enlaces masivos para validar disponibilidad:", height=250, placeholder="https://youtube.com/... \nhttps://tiktok.com/...")
    
    if st.button("🔍 VERIFICAR ESTADO EN VIVO"):
        raw_words = texto_verificar.replace(',', ' ').replace('\n', ' ').split()
        urls_verif = [w.strip('"\'()[]') for w in raw_words if any(d in w.lower() for d in ['tiktok', 'facebook', 'youtube', 'youtu.be', 'fb.com'])]
        urls_verif = ['https://' + w if not w.startswith('http') else w for w in urls_verif]
                
        if urls_verif:
            res_verif = []
            bar = st.progress(0)
            stat = st.empty()
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept-Language': 'es-419,es;q=0.9,pt-BR;q=0.8,ar;q=0.7,en;q=0.6'
            }
            
            for i, url in enumerate(urls_verif):
                stat.markdown(f"🔍 Evaluando servidor para: `{url[:60]}...`")
                url_cl = limpiar_url_táctica(url)
                
                estado = "🔴 DESCONOCIDO"
                titulo = "N/A"
                
                try:
                    res = requests.get(url_cl, headers=headers, timeout=10)
                    html = res.text
                    
                    if res.status_code == 200:
                        soup = BeautifulSoup(html, 'html.parser')
                        if "youtube" in url_cl.lower() or "youtu.be" in url_cl.lower():
                            if "Video unavailable" in html or "Video no disponible" in html or 'playabilityStatus":{"status":"ERROR"' in html:
                                estado = "❌ ROTO / PRIVADO / CAÍDO"
                                titulo = "Video no disponible en plataforma"
                            else:
                                estado = "✅ ACTIVO Y FUNCIONAL"
                                t_tag = soup.find("meta", property="og:title")
                                titulo = t_tag["content"] if t_tag else "YouTube Media (Activo)"
                        elif "tiktok" in url_cl.lower():
                            if "video-not-found" in html or "Video currently unavailable" in html:
                                estado = "❌ ROTO / PRIVADO / CAÍDO"
                                titulo = "TikTok Eliminado"
                            else:
                                estado = "✅ ACTIVO Y FUNCIONAL"
                                t_tag = soup.find("title")
                                titulo = t_tag.text if t_tag else "TikTok Media (Activo)"
                        else:
                            estado = "✅ ACTIVO Y FUNCIONAL"
                            t_tag = soup.find("title")
                            titulo = t_tag.text if t_tag else "Contenido Activo"
                    else:
                        estado = f"❌ CAÍDO (HTTP {res.status_code})"
                        titulo = "Conexión rechazada"
                except Exception as e:
                    estado = "❌ ROTO / PRIVADO / CAÍDO"
                    titulo = "Error de conexión"
                
                res_verif.append({"URL Original": url, "Estado del Servidor": estado, "Detalle/Título": titulo})
                bar.progress((i + 1) / len(urls_verif))
                
            bar.empty()
            stat.empty()
            
            df_verif = pd.DataFrame(res_verif)
            st.markdown('<div class="sub-header">📊 RESULTADOS DE VERIFICACIÓN DE RED</div>', unsafe_allow_html=True)
            st.dataframe(df_verif, use_container_width=True, hide_index=True)
            
            activos = len(df_verif[df_verif['Estado del Servidor'] == '✅ ACTIVO Y FUNCIONAL'])
            rotos = len(df_verif) - activos
            
            c_v1, c_v2 = st.columns(2)
            c_v1.success(f"**✅ ENLACES FUNCIONALES:** {activos}")
            c_v2.error(f"**❌ ENLACES CAÍDOS/PRIVADOS:** {rotos}")
            
        else:
            st.error("No se detectaron enlaces válidos en la entrada de texto.")

# ==============================================================================
# PIE DE PÁGINA Y METADATOS
# ==============================================================================

st.markdown("---")
st.caption(f"BS LATAM Tools • {fecha_actual_global} • Blood Strike")
