import yt_dlp
import easygui as ventana
import os
from PIL import Image
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
import yt_dlp

# Función para convertir imágenes WebP a JPEG
def convert_webp_to_jpeg(webp_path):
    with Image.open(webp_path) as img:
        output_path = webp_path.replace('.webp', '.jpg')  # Cambiar extensión a .jpg
        img.convert('RGB').save(output_path, format='JPEG')
    return output_path

# Función para agregar metadatos y portada
def add_metadata(mp3_file, image_path=None, title=None, artist=None, album=None):
    # Cargar el archivo MP3
    audio = MP3(mp3_file, ID3=ID3)

    # Asignar título y artista y álbum
    if title:
        audio.tags.add(TIT2(encoding=3, text=title))
    if artist:
        audio.tags.add(TPE1(encoding=3, text=artist))
    # if album:
    #     audio.tags.add(TALB(encoding=3, text=album))

    # Si se proporciona una imagen, la agregamos como portada
    if image_path:
        with open(image_path, 'rb') as img_file:
            image_data = img_file.read()

        # Añadir la imagen como portada
        audio.tags.add(
            APIC(
                encoding=3,  # UTF-8
                mime='image/jpeg',  # Asumimos que la imagen es JPEG
                type=3,  # Portada del álbum
                desc='Cover',
                data=image_data
            )
        )

    # Guardar los cambios en el archivo MP3
    audio.save()

def download_playlist(video_url, download_folder):
    # Configurar opciones de yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'quiet': False,  # Mostrar detalles del progreso
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': False,
        'writethumbnail': True,  # Descargar miniaturas
        'extractor-retries': 5,  # Número de reintentos si algo falla durante la descarga
        # 'sleep_interval': 1,  # Intervalo de tiempo entre cada intento de descarga (segundos)
        'max_downloads': 0,  # Descargar todos los videos disponibles (sin límite)
        'continue_dl': True,  # Continuar la descarga si fue interrumpida
        'restrict_filenames': False,  # Permite caracteres especiales en el nombre del archivo
        # 'no_warnings': True,  # No mostrar advertencias
        'ignoreerrors': True,  # Ignorar errores (si hay videos no disponibles o errores menores)
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        return info_dict
    
def delete_extra_files(download_folder):
    # Eliminar todos los archivos .jpg y .webm de la carpeta de descarga
    for file_name in os.listdir(download_folder):
        file_path = os.path.join(download_folder, file_name)
        if file_name.endswith('.jpg') or file_name.endswith('.webm'):
            os.remove(file_path)
            print(f"Eliminado: {file_path}")

if __name__ == "__main__":
    mensaje="Url del video o de la playlist"
    titulo="Descargador de vídeos de David - YoutubeToMp3"
    lista=["URL: "]
    caja=ventana.multenterbox(mensaje,titulo,lista)
    
    mensaje="Video/os descargandose, mirar el progreso en el cmd (pantalla negra)"
    
    video_url = caja[0]
    download_folder = './DownloadedFiles'
    
    # Descargar la playlist
    info_dict = download_playlist(video_url, download_folder)

    # Iterar sobre los archivos descargados y agregar metadatos
    for mp3_file in os.listdir(download_folder):
        if mp3_file.endswith('.mp3'):
            mp3_path = os.path.join(download_folder, mp3_file)

            # Obtener el nombre de la miniatura (debe tener el mismo nombre que el archivo MP3)
            thumbnail_path = os.path.join(download_folder, mp3_file.replace('.mp3', '.webp'))

            # Verificar si la miniatura existe
            if os.path.exists(thumbnail_path):
                # Convertir la miniatura WebP a JPEG
                jpeg_thumbnail_path = convert_webp_to_jpeg(thumbnail_path)
                
                # Intentar extraer el título del archivo MP3
                title = mp3_file.split('-')[1].split('.')[0].strip() if '-' in mp3_file else mp3_file.split('.')[0].strip()

                # Obtener información del video
                album = info_dict.get('title', '')
                
                # Extraer solo la primera parte del título hasta el primer guion
                artist = mp3_file.split('-')[0].strip()  # Obtener solo la parte antes del primer guion

                # Agregar los metadatos (y portada) al MP3
                add_metadata(mp3_path, image_path=jpeg_thumbnail_path, title=title, artist=artist, album=album)

                # Opcional: Eliminar la miniatura WebP original (si lo deseas)
                os.remove(thumbnail_path)
                
    # Eliminar archivos .jpg y .webm que no sean mp3
    delete_extra_files(download_folder)
    
    # Ejecutamos: 'pip install auto-py-to-exe' y después 'auto-py-to-exe'
