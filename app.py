import streamlit as st
import pandas as pd
import yt_dlp
import io

# Configuración de la página
st.set_page_config(
    page_title="YouTube Multi-Scraper & Analytics", 
    page_icon="📺", 
    layout="wide"
)

st.title("📺 YouTube Scraper & Engagement Analyzer")
st.markdown(
    "Pega múltiples enlaces de YouTube (uno por línea) para extraer métricas de visualización, "
    "interacciones y calcular su engagement de forma automática."
)

# Text area para ingresar múltiples enlaces a la vez
links_input = st.text_area(
    "Enlaces de YouTube (pega varios enlaces, uno por línea):",
    height=150,
    placeholder="https://www.youtube.com/watch?v=...\nhttps://youtu.be/...\nhttps://www.youtube.com/watch?v=..."
)

# Botón para iniciar el proceso
if st.button("🚀 Iniciar Scraping y Análisis", type="primary"):
    if not links_input.strip():
        st.warning("⚠️ Por favor, ingresa al menos un enlace de YouTube.")
    else:
        # Limpiar y separar los enlaces por salto de línea
        urls = [url.strip() for url in links_input.split("\n") if url.strip()]
        
        data = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Configuración de yt-dlp para extraer metadatos sin descargar el video
        ydl_opts = {
            'extract_flat': False,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            total_urls = len(urls)
            for i, url in enumerate(urls):
                status_text.text(f"Procesando enlace {i+1} de {total_urls}: {url}")
                try:
                    info = ydl.extract_info(url, download=False)
                    
                    # Extracción de datos
                    fecha_raw = info.get('upload_date', '')
                    if fecha_raw and len(fecha_raw) == 8:
                        # Formatear fecha de YYYYMMDD a DD/MM/YYYY
                        fecha = f"{fecha_raw[6:8]}/{fecha_raw[4:6]}/{fecha_raw[0:4]}"
                    else:
                        fecha = "Desconocida"
                        
                    creador = info.get('uploader', 'Desconocido')
                    vistas = info.get('view_count', 0) or 0
                    likes = info.get('like_count', 0) or 0
                    comentarios = info.get('comment_count', 0) or 0
                    
                    # Nota sobre 'Saves': YouTube no hace pública la métrica de guardados/favoritos por privacidad.
                    # Se incluye la columna reflejando esta limitación de la plataforma.
                    saves = "No público (YouTube)"
                    
                    # Interacciones (Likes + Comentarios)
                    interacciones = likes + comentarios
                    
                    # Tasa de Engagement: (Interacciones / Vistas) * 100
                    engagement = (interacciones / vistas * 100) if vistas > 0 else 0.0
                    
                    data.append({
                        "Fecha": fecha,
                        "Creador": creador,
                        "Link": url,
                        "Vistas": vistas,
                        "Likes": likes,
                        "Comentarios": comentarios,
                        "Saves": saves,
                        "Interacciones": interacciones,
                        "Engagement (%)": round(engagement, 2)
                    })
                except Exception as e:
                    data.append({
                        "Fecha": "Error",
                        "Creador": "Error de carga",
                        "Link": url,
                        "Vistas": 0,
                        "Likes": 0,
                        "Comentarios": 0,
                        "Saves": "N/A",
                        "Interacciones": 0,
                        "Engagement (%)": 0.0
                    })
                
                # Actualizar barra de progreso
                progress_bar.progress((i + 1) / total_urls)
        
        status_text.text("¡Proceso de scraping completado con éxito! 🎉")
        
        # Crear DataFrame de Pandas
        df = pd.DataFrame(data)
        
        st.subheader("📊 Tabla de Resultados")
        st.dataframe(df, use_container_width=True)
        
        # Generar archivo Excel en memoria para descarga
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='YouTube Analytics')
        excel_data = output.getvalue()
        
        # Botón de descarga de Excel
        st.download_button(
            label="📥 Descargar reporte en Excel (.xlsx)",
            data=excel_data,
            file_name="youtube_scraping_reporte.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
