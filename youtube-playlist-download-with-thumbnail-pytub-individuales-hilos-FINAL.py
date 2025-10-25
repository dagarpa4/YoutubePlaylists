import yt_dlp
import easygui as ventana
import os
from PIL import Image
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
import ffmpeg
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Función para convertir imágenes WebP a JPEG
def convertToMp3(input_file, output_file):
    try:
        # Ejecuta el comando ffmpeg para convertir webm a mp3
        ffmpeg.input(input_file).output(output_file, acodec='libmp3lame', audio_bitrate='192k').run()
        print(f"Conversión exitosa: {output_file}")
    except ffmpeg.Error as e:
        print(f"Error durante convertToMp3: {e}")

# Función para convertir imágenes WebP a JPEG
def convertToJpeg(videoPathNoExt):
    # Obtener el nombre de la miniatura (debe tener el mismo nombre que el archivo MP3)
    thumbnailPath = ''
    
    # Verificar si la miniatura existe
    if os.path.exists(videoPathNoExt + '.webp'):
        thumbnailPath = (videoPathNoExt + '.webp')
    
    if os.path.exists(videoPathNoExt + '.jpg'):
        thumbnailPath = (videoPathNoExt + '.jpg')
        
    if os.path.exists(videoPathNoExt + '.jpeg'):
        thumbnailPath = (videoPathNoExt + '.jpeg')

    if os.path.exists(videoPathNoExt + '.png'):
        thumbnailPath = (videoPathNoExt + '.png')

    if os.path.exists(videoPathNoExt + '.bmp'):
        thumbnailPath = (videoPathNoExt + '.bmp')
    
    if os.path.exists(videoPathNoExt + '.gif'):
        thumbnailPath = (videoPathNoExt + '.gif')

    try:
        with Image.open(thumbnailPath) as img:
            output_path = (os.path.splitext(thumbnailPath)[0] + '.jpg') # Cambiar extensión a .jpg
            img.convert('RGB').save(output_path, format='JPEG')
        return output_path
    except FileNotFoundError as e:
        print(f"Error durante convertToJpeg: {e}")

# Función para agregar metadatos y portada
def addMetadata(mp3_file, image_path=None, title=None, artist=None, album=None):
    try:
        # Cargar el archivo MP3
        audio = MP3(mp3_file, ID3=ID3)

        # Asignar título y artista y álbum
        if title:
            audio.tags.add(TIT2(encoding=3, text=title))
        if artist:
            audio.tags.add(TPE1(encoding=3, text=artist))
        if album:
            audio.tags.add(TALB(encoding=3, text=album))

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
    except FileNotFoundError as e:
        print(f"Error durante addMetadata: {e}")

def downloadVideo(video_url, downloadFolder):
    try:
        # Configurar opciones de yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(downloadFolder, '%(id)s.%(ext)s'),
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
    except FileNotFoundError as e:
        print(f"Error durante downloadVideo: {e}")

def getVideoList(playlist_url):
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,  # No descarga, solo extrae URLs
            'force_generic_extractor': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            return info['entries']
    
    except FileNotFoundError as e:
        print(f"Error durante getVideoList: {e}")

    
def deleteExtraFilesGeneral(downloadFolder):
    # Eliminar todos los archivos que no sean .mp3 de la carpeta de descarga
    for file_name in os.listdir(downloadFolder):
        file_path = os.path.join(downloadFolder, file_name)
        if not file_path.endswith('.mp3'):
            os.remove(file_path)
            print(f"Eliminado: {file_path}")

def deleteExtraFiles(downloadFolder, file_path_to_remove, retries=5, delay=2):
    # Eliminar todos los archivos que no sean .mp3 de la carpeta de descarga relacionados con el video específico
    for i in range(retries):
        try:
            for file_name in os.listdir(downloadFolder):
                file_path = os.path.join(downloadFolder, file_name)
                if file_path.startswith(file_path_to_remove) and not file_path.endswith('.mp3'):
                    os.remove(file_path)
                    print(f"Eliminado: {file_path}")
        except PermissionError:
            print(f"⚠️ Archivo en uso, reintentando... ({i+1}/{retries})")
            time.sleep(delay)
        except FileNotFoundError:
            return  # ya se eliminó o no existe

def downloadVideoProcess(video, downloadFolder):
    # Descargar cada video individualmente y obtener su información
    videoInfoDic = downloadVideo(video['url'], downloadFolder)

    # Nombre del archivo de video descargado sin extensión
    videoPathNoExt = os.path.join(downloadFolder, videoInfoDic.get('id', ''))

    # Nombre del archivo de video descargado
    videoPath = videoPathNoExt + '.' + videoInfoDic.get('audio_ext', '')

    # Nombre que tendrá el archivo mp3
    mp3Path = unicodedata.normalize('NFKC', videoInfoDic.get('title', ''))
    mp3Path = re.sub(r'[<>:"/\\|?*]', '_', mp3Path)
    mp3Path = os.path.join(downloadFolder, mp3Path  + '.' + 'mp3')

    # Convertir el audio a MP3
    convertToMp3(videoPath, mp3Path)
        
    # Convertir la miniatura a JPEG
    jpegThumbnailPath = convertToJpeg(videoPathNoExt)
    
    # Extraer el título del video
    title = videoInfoDic.get('title', '')

    # Extraer el album del video
    album = videoInfoDic.get('album', '')
    
    # Extraer el uploader del video
    artist = videoInfoDic.get('uploader', '')

    # Agregar los metadatos (y portada) al MP3
    addMetadata(mp3Path, image_path=jpegThumbnailPath, title=title, artist=artist, album=album)

    # Opcional: Eliminar la miniatura WebP, la WebM y el JPG (si lo deseas)
    # os.remove(thumbnailPath)
    # if thumbnailPath != jpegThumbnailPath:
    #     os.remove(jpegThumbnailPath)
    # os.remove(videoPath)

    # Eliminar archivos .jpg y .webm que no sean mp3
    deleteExtraFiles(downloadFolder, videoPathNoExt)

if __name__ == "__main__":
    
    # Descomentar inicio
    mensaje="Url del video o de la playlist"
    titulo="Descargador de vídeos de David - YoutubeToMp3"
    lista=["URL: "]
    caja=ventana.multenterbox(mensaje,titulo,lista)
    
    mensaje="Video/os descargandose, mirar el progreso en el cmd (pantalla negra)"
    
    video_url = caja[0]
    # Descomentar fin
    
    # video_url = 'https://www.youtube.com/playlist?list=PLl1cp_5DYiK6IS0-M03rB7gXgZlGkSvHi'
    # El nombre base del directorio
    base_folder = './DownloadedFiles'
    i = 1
    downloadFolder = f"{base_folder}{i}"

    # Comprobamos si el directorio existe y buscamos uno disponible
    while os.path.isdir(downloadFolder):
        i += 1
        downloadFolder = f"{base_folder}{i}"
    
    # Descargar la playlist
    # info_dict = download_playlist(video_url, downloadFolder)

    num_hilos = os.cpu_count()
    print(f"Tu PC tiene {num_hilos} hilos lógicos de CPU.")

    inicio = time.time()

    videoList = getVideoList(video_url)

    futures = []
    with ThreadPoolExecutor(max_workers=min(8,num_hilos)) as executor:
        for video in videoList:
            if not video:
                continue
            futures.append(executor.submit(downloadVideoProcess, video, downloadFolder))

        for future in as_completed(futures):
                future.result()
                    
    # Eliminar archivos .jpg y .webm que no sean mp3
    deleteExtraFilesGeneral(downloadFolder)

    fin = time.time()

    print(f"⏱️ Tiempo total: {fin - inicio:.2f} segundos")

    # pip install yt-dlp easygui pillow mutagen ffmpeg-python
    # instalar ffmpeg en el sistema operativo y añadir a la variable PATH
    
    # Ejecutamos: 'pip install auto-py-to-exe' y después 'auto-py-to-exe' o 'python -m auto_py_to_exe'
    
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
