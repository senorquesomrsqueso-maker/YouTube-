import re
import time
from urllib.parse import urlparse
import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st

st.set_page_config(
    page_title="Auditor de Enlaces de Facebook",
    page_icon="📊",
    layout="wide",
)

HEADERS_BASE = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-419,es;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

CAMPOS_AUDITADOS = ["Creador", "Título", "Reproducciones", "Likes", "Comentarios"]


def parse_urls(raw_text: str) -> list[str]:
    seen = set()
    urls = []
    for line in raw_text.splitlines():
        url = line.strip()
        if not url:
            continue
        parsed = urlparse(url)
        if parsed.scheme in ("http", "https") and "facebook.com" in parsed.netloc.lower() or "fb.watch" in parsed.netloc.lower():
            if url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


def parse_metric_number(text: str | None) -> int | None:
    if not text:
        return None
    s = text.strip().lower()
    s = re.sub(r"\s+", " ", s)

    # Busca patrones como "12,4 mil", "1.5k", "2,3 m", "1.200"
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*(mil|k|m|millones|millón)?\b", s)
    if not match:
        return None

    num_str, suffix = match.groups()
    suffix = suffix or ""

    # Maneja separadores de miles y decimales de forma conservadora
    if suffix in ("mil", "k", "m", "millones", "millón"):
        val = float(num_str.replace(",", "."))
        if suffix in ("mil", "k"):
            return int(round(val * 1_000))
        return int(round(val * 1_000_000))

    # Sin sufijo: si tiene puntos o comas con 3 dígitos al final, suele ser separador de miles
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", num_str):
        return int(re.sub(r"[.,]", "", num_str))

    try:
        return int(round(float(num_str.replace(",", "."))))
    except ValueError:
        return None


def extract_from_html(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    creator = None
    title = None
    views = None
    likes = None
    comments = None

    # 1. Metaetiquetas OpenGraph (suelen ser las más estables en HTML estático)
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()

    og_desc = soup.find("meta", property="og:description")
    desc_text = og_desc["content"].strip() if og_desc and og_desc.get("content") else ""

    # A veces og:title incluye "Nombre | Video de Facebook" o "Nombre - Reel"
    if title and "|" in title:
        partes = [p.strip() for p in title.split("|")]
        if len(partes) >= 2 and "facebook" not in partes[0].lower():
            creator = partes[0]
            title = " | ".join(partes[1:]).replace("en Facebook", "").strip()

    # 2. Patrones JSON / texto embebido en el HTML
    patterns_views = [
        r'"video_view_count"\s*:\s*(\d+)',
        r'"play_count"\s*:\s*(\d+)',
        r'"view_count"\s*:\s*(\d+)',
        r'(\d+(?:[.,]\d+)?\s*(?:mil|k|m|millones)?)\s*(?:reproducciones|vistas|views)',
    ]
    for pat in patterns_views:
        m = re.search(pat, html, flags=re.IGNORECASE)
        if m:
            parsed = parse_metric_number(m.group(1))
            if parsed is not None:
                views = parsed
                break

    patterns_likes = [
        r'"reaction_count"\s*:\s*\{\s*"count"\s*:\s*(\d+)',
        r'"like_count"\s*:\s*(\d+)',
        r'(\d+(?:[.,]\d+)?\s*(?:mil|k|m|millones)?)\s*(?:me gusta|likes|reacciones)',
    ]
    for pat in patterns_likes:
        m = re.search(pat, html, flags=re.IGNORECASE)
        if m:
            parsed = parse_metric_number(m.group(1))
            if parsed is not None:
                likes = parsed
                break

    patterns_comments = [
        r'"comment_count"\s*:\s*\{\s*"total_count"\s*:\s*(\d+)',
        r'"comments_count"\s*:\s*(\d+)',
        r'(\d+(?:[.,]\d+)?\s*(?:mil|k|m|millones)?)\s*(?:comentarios|comments)',
    ]
    for pat in patterns_comments:
        m = re.search(pat, html, flags=re.IGNORECASE)
        if m:
            parsed = parse_metric_number(m.group(1))
            if parsed is not None:
                comments = parsed
                break

    if not creator:
        m_owner = re.search(r'"owner"\s*:\s*\{[^}]{0,200}?"name"\s*:\s*"([^"]+)"', html)
        if m_owner:
            creator = m_owner.group(1).encode("utf-8").decode("unicode_escape", errors="ignore").strip()

    if not title and desc_text:
        title = desc_text[:140]

    # Evaluación de calidad de extracción
    extracted_map = {
        "Creador": creator,
        "Título": title,
        "Reproducciones": views,
        "Likes": likes,
        "Comentarios": comments,
    }
    faltantes = [k for k, v in extracted_map.items() if v in (None, "")]
    encontrados = len(CAMPOS_AUDITADOS) - len(faltantes)
    precision_pct = round((encontrados / len(CAMPOS_AUDITADOS)) * 100)

    if encontrados == 0:
        estado = "Error"
    elif len(faltantes) == 0:
        estado = "OK"
    else:
        estado = "Parcial"

    return {
        "Enlace": url,
        "Creador": creator or "No detectado",
        "Título": title or "No detectado",
        "Reproducciones": views if views is not None else "No detectado",
        "Likes": likes if likes is not None else "No detectado",
        "Comentarios": comments if comments is not None else "No detectado",
        "Estado": estado,
        "Precisión (%)": precision_pct,
        "Campos faltantes": ", ".join(faltantes) if faltantes else "Ninguno",
    }


@st.cache_data(show_spinner=False, ttl=900)
def scrape_single_url(url: str, cookie_header: str, timeout_sec: int) -> dict:
    headers = dict(HEADERS_BASE)
    if cookie_header.strip():
        headers["Cookie"] = cookie_header.strip()

    try:
        resp = requests.get(url, headers=headers, timeout=timeout_sec, allow_redirects=True)
        resp.raise_for_status()
        return extract_from_html(url, resp.text)
    except Exception as exc:
        return {
            "Enlace": url,
            "Creador": "No detectado",
            "Título": "No detectado",
            "Reproducciones": "No detectado",
            "Likes": "No detectado",
            "Comentarios": "No detectado",
            "Estado": "Error",
            "Precisión (%)": 0,
            "Campos faltantes": f"Petición fallida ({type(exc).__name__})",
        }


st.title("📊 Auditor de Enlaces y Métricas de Facebook")
st.caption(
    "Pega uno o varios enlaces de videos/Reels de Facebook para extraer métricas y auditar qué campos se obtuvieron."
)

with st.sidebar:
    st.header("Configuración")
    delay_sec = st.slider("Pausa entre enlaces (seg)", min_value=0.5, max_value=5.0, value=1.5, step=0.5)
    timeout_sec = st.slider("Tiempo límite por enlace (seg)", min_value=5, max_value=30, value=12, step=1)
    cookie_header = st.text_area(
        "Cookie de sesión (opcional)",
        placeholder="Pega aquí la cabecera Cookie si lo necesitas...",
        height=90,
        help="Útil si ciertos enlaces requieren contexto de sesión; úsala con precaución.",
    )
    solo_fallidos = st.checkbox("Mostrar solo filas Parcial / Error", value=False)

raw_urls = st.text_area(
    "Enlaces de Facebook (uno por línea)",
    height=170,
    placeholder="https://www.facebook.com/reel/...\nhttps://www.facebook.com/watch/?v=...",
)

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    run_btn = st.button("Extraer y auditar", type="primary", use_container_width=True)

if run_btn:
    urls = parse_urls(raw_urls)
    if not urls:
        st.warning("Ingresa al menos un enlace válido de Facebook.")
    else:
        rows = []
        progress = st.progress(0, text="Iniciando extracción...")
        for idx, u in enumerate(urls, start=1):
            progress.progress(idx / len(urls), text=f"Procesando {idx} de {len(urls)}: {u}")
            rows.append(scrape_single_url(u, cookie_header, timeout_sec))
            if idx < len(urls):
                time.sleep(delay_sec)
        progress.empty()
        st.session_state["audit_df"] = pd.DataFrame(rows)

if "audit_df" in st.session_state and not st.session_state["audit_df"].empty:
    df = st.session_state["audit_df"].copy()

    total = len(df)
    ok_count = (df["Estado"] == "OK").sum()
    parcial_count = (df["Estado"] == "Parcial").sum()
    error_count = (df["Estado"] == "Error").sum()
    avg_prec = round(df["Precisión (%)"].mean(), 1)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total enlaces", total)
    m2.metric("OK (100%)", ok_count)
    m3.metric("Parcial", parcial_count)
    m4.metric("Error", error_count)
    m5.metric("Precisión promedio", f"{avg_prec}%")

    view_df = df[df["Estado"].isin(["Parcial", "Error"])] if solo_fallidos else df

    st.subheader("Tabla de auditoría")
    st.dataframe(view_df, use_container_width=True, hide_index=True)

    csv_data = view_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Descargar tabla en CSV",
        data=csv_data,
        file_name="auditoria_facebook.csv",
        mime="text/csv",
    )

    with st.expander("Lista vertical de enlaces (fácil de copiar)"):
        st.code("\n".join(view_df["Enlace"].tolist()), language="text")
