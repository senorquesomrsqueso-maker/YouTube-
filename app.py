import re
import time
from urllib.parse import urlparse, urlunparse
import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st

try:
    import yt_dlp  # type: ignore

    HAS_YTDLP = True
except ImportError:
    HAS_YTDLP = False

st.set_page_config(
    page_title="Auditor de Enlaces y Métricas de Facebook",
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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Upgrade-Insecure-Requests": "1",
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
        host = parsed.netloc.lower()
        is_fb = parsed.scheme in ("http", "https") and ("facebook.com" in host or "fb.watch" in host)
        if is_fb and url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def normalize_fb_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if "/watch" in parsed.path and "v=" in parsed.query:
        v_match = re.search(r"(?:^|&)v=([^&]+)", parsed.query)
        clean_query = f"v={v_match.group(1)}" if v_match else ""
    else:
        clean_query = ""
    clean = parsed._replace(query=clean_query, fragment="")
    return urlunparse(clean)


def parse_metric_number(text: str | None) -> int | None:
    if not text:
        return None
    s = str(text).strip().lower()
    s = re.sub(r"\s+", " ", s)

    match = re.search(r"(\d+(?:[.,]\d+)?)\s*(mil|k|m|millones|millón)?\b", s)
    if not match:
        return None

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
        return None


def extract_metrics_from_summary_text(text: str) -> dict[str, int | None]:
    """
    Rescata reproducciones, likes/reacciones y comentarios cuando vienen juntos
    en cadenas tipo: '2,2 mil reproducciones · 64 reacciones · 10 comentarios'
    """
    out: dict[str, int | None] = {
        "views": None,
        "likes": None,
        "comments": None,
    }
    if not text:
        return out

    m_views = re.search(
        r"(\d+(?:[.,]\d+)?\s*(?:mil|k|m|millones|millón)?)\s*(?:reproducciones|vistas|views)",
        text,
        flags=re.IGNORECASE,
    )
    if m_views:
        out["views"] = parse_metric_number(m_views.group(1))

    m_likes = re.search(
        r"(\d+(?:[.,]\d+)?\s*(?:mil|k|m|millones|millón)?)\s*(?:reacciones|me gusta|likes|reactions)",
        text,
        flags=re.IGNORECASE,
    )
    if m_likes:
        out["likes"] = parse_metric_number(m_likes.group(1))

    m_comments = re.search(
        r"(\d+(?:[.,]\d+)?\s*(?:mil|k|m|millones|millón)?)\s*(?:comentarios|comments)",
        text,
        flags=re.IGNORECASE,
    )
    if m_comments:
        out["comments"] = parse_metric_number(m_comments.group(1))

    return out


def looks_like_metrics_only(text: str) -> bool:
    t = text.strip().lower()
    metric_keywords = ("reproducciones", "vistas", "views", "reacciones", "me gusta", "likes", "comentarios", "comments")
    has_kw = any(k in t for k in metric_keywords)
    has_num = re.search(r"\d", t) is not None
    # Si la mayor parte del texto son números/palabras de métricas y no frases normales
    stripped_metrics = re.sub(
        r"\d+(?:[.,]\d+)?\s*(?:mil|k|m|millones|millón)?\s*(?:reproducciones|vistas|views|reacciones|me gusta|likes|comentarios|comments)?|[·•|,/-]",
        "",
        t,
        flags=re.IGNORECASE,
    ).strip()
    return has_kw and has_num and len(stripped_metrics) < 12


def sanitize_creator_and_rescue_metrics(
    creator: str | None,
    views: int | None,
    likes: int | None,
    comments: int | None,
) -> tuple[str | None, int | None, int | None, int | None]:
    if not creator:
        return None, views, likes, comments

    rescued = extract_metrics_from_summary_text(creator)
    if views is None and rescued["views"] is not None:
        views = rescued["views"]
    if likes is None and rescued["likes"] is not None:
        likes = rescued["likes"]
    if comments is None and rescued["comments"] is not None:
        comments = rescued["comments"]

    # Si el texto entero de creador era solo métricas (como "2,2 mil reproducciones · 64 reacciones"), limpiamos creador
    if looks_like_metrics_only(creator):
        return None, views, likes, comments

    # Si viene separado por '·' o '|', dejamos la parte que no sea métrica como posible creador
    for sep in ("·", "•", "|"):
        if sep in creator:
            partes = [p.strip() for p in creator.split(sep) if p.strip()]
            candidatos_nombre = [p for p in partes if not looks_like_metrics_only(p)]
            if candidatos_nombre:
                return candidatos_nombre[0], views, likes, comments
            return None, views, likes, comments

    return creator.strip(), views, likes, comments


def diagnose_html(html: str, final_url: str) -> str | None:
    lower = html.lower()
    if "login" in urlparse(final_url).path.lower() and "reel" not in urlparse(final_url).path.lower():
        return "Redirigido a login"
    if len(html) < 1500 and ("iniciar sesión" in lower or "log in" in lower):
        return "Pantalla de login / bloqueo"
    if "checkpoint" in lower:
        return "Checkpoint de seguridad FB"
    return None


def extract_from_html(url: str, html: str, final_url: str) -> dict:
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

    # Rescate desde meta descripción si trae resumen de métricas
    if desc_text:
        desc_metrics = extract_metrics_from_summary_text(desc_text)
        views = views if views is not None else desc_metrics["views"]
        likes = likes if likes is not None else desc_metrics["likes"]
        comments = comments if comments is not None else desc_metrics["comments"]

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
        r'(\d+(?:[.,]\d+)?\s*(?:mil|k|m|millones)?)\s*(?:reacciones|me gusta|likes)',
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

    if not title and desc_text and not looks_like_metrics_only(desc_text):
        title = desc_text[:140]

    creator, views, likes, comments = sanitize_creator_and_rescue_metrics(
        creator, views, likes, comments
    )

    extracted_map = {
        "Creador": creator,
        "Título": title,
        "Reproducciones": views,
        "Likes": likes,
        "Comentarios": comments,
    }

    diag = diagnose_html(html, final_url)
    faltantes = [k for k, v in extracted_map.items() if v in (None, "")]
    encontrados = len(CAMPOS_AUDITADOS) - len(faltantes)
    precision_pct = round((encontrados / len(CAMPOS_AUDITADOS)) * 100)

    if encontrados == 0:
        estado = "Error"
    elif len(faltantes) == 0:
        estado = "OK"
    else:
        estado = "Parcial"

    detalle_faltantes = list(faltantes)
    if diag and encontrados == 0:
        detalle_faltantes.insert(0, diag)

    return {
        "Enlace": url,
        "Creador": creator or "No detectado",
        "Título": title or "No detectado",
        "Reproducciones": views if views is not None else "No detectado",
        "Likes": likes if likes is not None else "No detectado",
        "Comentarios": comments if comments is not None else "No detectado",
        "Estado": estado,
        "Precisión (%)": precision_pct,
        "Campos faltantes": ", ".join(detalle_faltantes) if detalle_faltantes else "Ninguno",
    }


def extract_with_ytdlp(url: str, cookie_header: str) -> dict | None:
    if not HAS_YTDLP:
        return None
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    if cookie_header.strip():
        ydl_opts["http_headers"] = {"Cookie": cookie_header.strip()}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info:
            return None

        creator = info.get("uploader") or info.get("channel") or None
        title = info.get("title") or info.get("description") or None
        if isinstance(title, str):
            title = title[:140]
        views = info.get("view_count")
        likes = info.get("like_count")
        comments = info.get("comment_count")

        creator, views, likes, comments = sanitize_creator_and_rescue_metrics(
            creator, views, likes, comments
        )

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
            return None

        estado = "OK" if len(faltantes) == 0 else "Parcial"
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
    except Exception:
        return None


@st.cache_data(show_spinner=False, ttl=900)
def scrape_single_url(url: str, cookie_header: str, timeout_sec: int, use_ytdlp_fallback: bool) -> dict:
    headers = dict(HEADERS_BASE)
    if cookie_header.strip():
        headers["Cookie"] = cookie_header.strip()

    clean_url = normalize_fb_url(url)
    candidates = [clean_url]
    if "www.facebook.com" in clean_url:
        candidates.append(clean_url.replace("www.facebook.com", "m.facebook.com", 1))

    last_error = "Error desconocido"
    for target in candidates:
        try:
            resp = requests.get(target, headers=headers, timeout=timeout_sec, allow_redirects=True)
            resp.raise_for_status()
            result = extract_from_html(url, resp.text, resp.url)
            if result["Estado"] != "Error":
                return result
            last_error = f"{result['Campos faltantes']} ({target})"
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else "?"
            last_error = f"HTTPError {status_code} ({target})"
        except Exception as exc:
            last_error = f"{type(exc).__name__} ({target})"

    if use_ytdlp_fallback and HAS_YTDLP:
        yt_res = extract_with_ytdlp(clean_url, cookie_header)
        if yt_res is not None:
            return yt_res

    return {
        "Enlace": url,
        "Creador": "No detectado",
        "Título": "No detectado",
        "Reproducciones": "No detectado",
        "Likes": "No detectado",
        "Comentarios": "No detectado",
        "Estado": "Error",
        "Precisión (%)": 0,
        "Campos faltantes": last_error,
    }


st.title("📊 Auditor de Enlaces y Métricas de Facebook")
st.caption(
    "Pega uno o varios enlaces de videos/Reels de Facebook para extraer métricas y auditar qué campos se obtuvieron."
)

with st.sidebar:
    st.header("Configuración")
    delay_sec = st.slider("Pausa entre enlaces (seg)", min_value=0.5, max_value=5.0, value=1.5, step=0.5)
    timeout_sec = st.slider("Tiempo límite por enlace (seg)", min_value=5, max_value=30, value=12, step=1)
    use_ytdlp_fallback = st.checkbox(
        "Usar respaldo yt-dlp si falla HTTP",
        value=True,
        disabled=not HAS_YTDLP,
        help="Requiere tener yt-dlp en requirements.txt.",
    )
    if not HAS_YTDLP:
        st.caption("Tip: agrega `yt-dlp` a `requirements.txt` si quieres activar este respaldo.")
    cookie_header = st.text_area(
        "Cookie de sesión (opcional)",
        placeholder="Pega aquí la cabecera Cookie si lo necesitas...",
        height=90,
    )
    solo_fallidos = st.checkbox("Mostrar solo filas Parcial / Error", value=False)

raw_urls = st.text_area(
    "Enlaces de Facebook (uno por línea)",
    height=170,
    placeholder="https://www.facebook.com/reel/...\nhttps://www.facebook.com/watch/?v=...",
)

col_btn1, _ = st.columns([1, 4])
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
            rows.append(scrape_single_url(u, cookie_header, timeout_sec, use_ytdlp_fallback))
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
