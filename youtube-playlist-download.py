# import yt_dlp

# def descargar_video(url, ruta_descarga='.'):
#     try:
#         # Configuración de opciones para yt-dlp
#         opciones = {
#             'format': 'bestaudio/best',  # Descargar la mejor calidad de audio
#             'outtmpl': f'{ruta_descarga}/%(title)s.%(ext)s',  # Formato de nombre de archivo
#             'quiet': False  # Para mostrar detalles del progreso
#             # 'postprocessors': [{  # Postprocesador para convertir a .mp3
#             #     'key': 'FFmpegAudio',
#             #     'preferredcodec': 'mp3',
#             #     'preferredquality': '192',
#             # }],
#         }

#         # Crear un objeto de descarga de yt-dlp
#         with yt_dlp.YoutubeDL(opciones) as ydl:
#             # Descargar el video o la lista de reproducción
#             ydl.download([url])
#             print("Descarga completada")
#     except Exception as e:
#         print(f"Error: {e}")

# if __name__ == "__main__":
#     url = input("Introduce la URL de la canción o playlist de YouTube: ")
#     ruta = input("Introduce la ruta donde guardar los archivos (deja vacío para la ruta predeterminada): ")
#     if not ruta:
#         ruta = '.'  # Si no se proporciona ruta, usa la carpeta actual.
#     descargar_video(url, ruta)

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
