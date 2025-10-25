import yt_dlp
import easygui as ventana
import os
from PIL import Image
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
import ffmpeg

# Función para convertir imágenes WebP a JPEG
def convertir_a_mp3(input_file, output_file):
    try:
        # Ejecuta el comando ffmpeg para convertir webm a mp3
        ffmpeg.input(input_file).output(output_file, acodec='libmp3lame', audio_bitrate='192k').run()
        print(f"Conversión exitosa: {output_file}")
    except ffmpeg.Error as e:
        print(f"Error durante la conversión: {e}")

# Función para convertir imágenes WebP a JPEG
def convert_to_jpeg(webp_path):
    try:
        with Image.open(webp_path) as img:
            output_path = (os.path.splitext(webp_path)[0] + '.jpg') # Cambiar extensión a .jpg
            img.convert('RGB').save(output_path, format='JPEG')
        return output_path
    except FileNotFoundError as e:
        print(f"Error durante la conversión: {e}")

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
        # 'postprocessors': [{
        #     'key': 'FFmpegExtractAudio',
        #     'preferredcodec': 'mp3',
        #     'preferredquality': '192',
        # }],
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
        if not file_name.endswith('.mp3'):
            os.remove(file_path)
            print(f"Eliminado: {file_path}")

if __name__ == "__main__":
    
    mensaje="Url del video o de la playlist"
    titulo="Descargador de vídeos de David - YoutubeToMp3"
    lista=["URL: "]
    caja=ventana.multenterbox(mensaje,titulo,lista)
    
    mensaje="Video/os descargandose, mirar el progreso en el cmd (pantalla negra)"
    
    video_url = caja[0]
    
    # El nombre base del directorio
    base_folder = './DownloadedFiles'
    i = 1
    download_folder = f"{base_folder}{i}"

    # Comprobamos si el directorio existe y buscamos uno disponible
    while os.path.isdir(download_folder):
        i += 1
        download_folder = f"{base_folder}{i}"
    
    # Descargar la playlist
    info_dict = download_playlist(video_url, download_folder)
    
    for video_file in os.listdir(download_folder):
        if video_file.endswith('.webm') or video_file.endswith('.m4a'):
            video_path = os.path.join(download_folder, video_file)
            mp3_path = (os.path.splitext(video_path)[0] + '.mp3')
            
            # Llama a la función con el archivo .webm de entrada y el archivo .mp3 de salida
            convertir_a_mp3(video_path, mp3_path)
            
            # Obtener el nombre de la miniatura (debe tener el mismo nombre que el archivo MP3)
            thumbnail_path = ''
            
            # Verificar si la miniatura existe
            if os.path.exists(mp3_path.split('.mp3')[0] + '.webp'):
                thumbnail_path = (mp3_path.split('.mp3')[0] + '.webp')
            
            if os.path.exists(mp3_path.split('.mp3')[0] + '.jpg'):
                thumbnail_path = (mp3_path.split('.mp3')[0] + '.jpg')
                
            if os.path.exists(mp3_path.split('.mp3')[0] + '.png'):
                thumbnail_path = (mp3_path.split('.mp3')[0] + '.png')
                
            # Convertir la miniatura WebP a JPEG
            jpeg_thumbnail_path = convert_to_jpeg(thumbnail_path)
            
            # Intentar extraer el título del archivo MP3
            title = os.path.splitext(video_file)[0].split('-')[1] if '-' in video_file else os.path.splitext(video_file)[0]

            # Obtener información del video
            album = info_dict.get('title', '') if info_dict.get('title', '') else title
            
            # Extraer solo la primera parte del título hasta el primer guion
            artist = video_file.split('-')[0].strip()  # Obtener solo la parte antes del primer guion

            # Agregar los metadatos (y portada) al MP3
            add_metadata(mp3_path, image_path=jpeg_thumbnail_path, title=title, artist=artist, album=album)

            # Opcional: Eliminar la miniatura WebP, la WebM y el JPG (si lo deseas)
            # os.remove(thumbnail_path)
            # if thumbnail_path != jpeg_thumbnail_path:
            #     os.remove(jpeg_thumbnail_path)
            # os.remove(video_path)
                
    # Eliminar archivos .jpg y .webm que no sean mp3
    delete_extra_files(download_folder)
    
    # Ejecutamos: 'pip install auto-py-to-exe' y después 'auto-py-to-exe'
    
    # Resumen completo de las extensiones posibles:
    # 1. Miniaturas
    # .jpg
    # .webp
    # .png
    # 2. Audio
    # .webm
    # .m4a
    # .mp3
    # .ogg (raro)
    # .flac (raro)
    # 3. Video
    # .webm
    # .mp4
    # .mov (raro)
    # .avi (raro)
    # .flv (raro)
    # .mkv (raro)
