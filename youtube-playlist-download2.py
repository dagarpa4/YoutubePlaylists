import yt_dlp

def descargar_audio(url, ruta_descarga='.'):
    try:
        opciones = {
            'format': 'bestaudio/best',  # Descargar la mejor calidad de audio
            'extractaudio': True,  # Extraer solo el audio
            'audioformat': 'mp3',  # Convertir a mp3
            'outtmpl': f'{ruta_descarga}/%(title)s.%(ext)s',  # Formato de nombre de archivo
            'quiet': False,  # Mostrar detalles del progreso
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            # Opciones adicionales para obtener toda la información disponible:
            # 'writeinfojson': True,  # Escribir archivo JSON con información del video
            # 'writethumbnail': True,  # Descargar miniaturas del video
            # 'writedescription': True,  # Descargar la descripción del video
            # 'writeannotations': True,  # Descargar las anotaciones del video
            # 'writesubtitles': True,  # Descargar subtítulos (si están disponibles)
            # 'writeautosub': True,  # Descargar subtítulos automáticos si están disponibles
            'subtitleslangs': ['en'],  # Idiomas de los subtítulos (si los hay)
            'writemetadata': True,  # Descargar metadatos del video (por ejemplo, tags, categorías)
            # 'writeallthumbnails': True,  # Descargar todas las miniaturas disponibles
            'writeurl': True,  # Descargar la URL directa del video
            # 'writethumbnail': True,  # Descargar miniaturas
            # 'writeplaylist': True,  # Escribir información de la lista de reproducción
            'writeinfo': True,  # Escribir información adicional del video
            'writeid3': True,  # Escribir etiquetas ID3 al archivo de audio
            'merge_output_format': 'mp3',  # Forzar la conversión a MP3 si no está en ese formato
            'extractor-retries': 5,  # Número de reintentos si algo falla durante la descarga
            'sleep_interval': 1,  # Intervalo de tiempo entre cada intento de descarga (segundos)
            'max_downloads': 0,  # Descargar todos los videos disponibles (sin límite)
            'continue_dl': True,  # Continuar la descarga si fue interrumpida
            'restrict_filenames': False,  # Permite caracteres especiales en el nombre del archivo
            # 'no_warnings': True,  # No mostrar advertencias
            'ignoreerrors': True,  # Ignorar errores (si hay videos no disponibles o errores menores)
        }
        
        # Crear un objeto de descarga
        with yt_dlp.YoutubeDL(opciones) as ydl:
            ydl.download([url])
        print("Descarga completada con éxito.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    url = input("Introduce la URL del video de YouTube: ")
    ruta = input("Introduce la ruta donde guardar los archivos (deja vacío para la ruta predeterminada): ")
    if not ruta:
        ruta = '.'  # Si no se proporciona ruta, usa la carpeta actual.
    descargar_audio(url, ruta)
