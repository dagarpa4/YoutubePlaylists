import yt_dlp
import easygui as ventana
import os
from streamlink import Streamlink
from pytube import YouTube
import subprocess
from PIL import Image
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
import ffmpeg
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Eliminar todos los archivos que no sean .mp3 de la carpeta de descarga relacionados con el video específico
def retryFunction(func, retries=5, delay=2):
    for i in range(retries):
        try:
            return func()
        except:
            print(f"⚠️ Archivo en uso, reintentando... ({i+1}/{retries})")
            time.sleep(delay)
    
    time.sleep(delay) # Pequeña pausa para asegurar

# Función para agregar metadatos y portada
def addMetadata(mp3_file, image_path=None, title=None, artist=None, album=None):
    try:
        # Cargar el archivo MP3
        if not os.path.exists(mp3_file):
            print(f"Archivo no encontrado: {mp3_file} ------------------------------------------------------------------------------------------------------------")
            return
        
        audio = MP3(mp3_file, ID3=ID3)
        
        # Inicializar tags si no existen
        if audio.tags is None:
                audio.add_tags()

        # Asignar título y artista y álbum
        if title:
            audio.tags.add(TIT2(encoding=3, text=title))
        if artist:
            audio.tags.add(TPE1(encoding=3, text=artist))
        if album:
            audio.tags.add(TALB(encoding=3, text=album))

        # Asignar imagen
        if image_path:
            with open(image_path, 'rb') as img_file:
                image_data = img_file.read()

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
        

# Función para convertir imágenes WebP a JPEG
def convertToMp3(input_file, output_file):
    try:
      # Convertir a MP3 con ffmpeg
      subprocess.run([
          "ffmpeg",
          "-y",
          "-i", input_file,
          "-vn", # sin video
          "-acodec", "libmp3lame",
          "-ab", "192k",
          "-ar", "44100",
          output_file
      ], check=True)
      print(f"Conversión exitosa: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error durante convertToMp3: {e}")
        
def renameMp3(input_file, output_file):
    try:
        os.rename(input_file, output_file)
        print(f"Archivo renombrado a: {output_file}")
    except FileNotFoundError as e:
        print(f"Error durante renameMp3: {e}")
    except FileExistsError as e:
        print(f"Error durante renameMp3: {e}")
        
        
def downloadThumbnail(video_id, output_file):
    try:
    #   subprocess.run([
    #       "wget",
    #       "-L",
    #       f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
    #       "-o",
    #       output_file
    #   ], check=True)
      
      subprocess.run([
          "yt-dlp",
          "--skip-download",
          "--write-thumbnail",
          "--convert-thumbnails", "jpg",
          "-o", output_file.replace(".jpg", ""),
          f"https://www.youtube.com/watch?v={video_id}"
      ], check=True)
      
    except subprocess.CalledProcessError as e:
        print(f"Error durante downloadThumbnail: {e}")


def downloadVideo(video_url, output_file):
    try:
      subprocess.run([
          "streamlink",
          video_url,
          "best",
          "-o",
          output_file
      ], check=True)
    
    except subprocess.CalledProcessError as e:
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

    
# Eliminar todos los archivos que no sean .mp3 de la carpeta de descarga
def deleteExtraFilesGeneral(downloadFolder):
    for file_name in os.listdir(downloadFolder):
        file_path = os.path.join(downloadFolder, file_name)
        if not file_path.endswith('.mp3'):
            os.remove(file_path)
            print(f"Eliminado: {file_path}")


# Eliminar todos los archivos que no sean .mp3 de la carpeta de descarga relacionados con el video específico
def deleteExtraFiles(downloadFolder, file_path_to_remove, retries=5, delay=2):
    for i in range(retries):
        try:
            for file_name in os.listdir(downloadFolder):
                file_path = os.path.join(downloadFolder, file_name)
                if file_path.startswith(file_path_to_remove.replace('.mp3', '')) and not file_path.endswith('.mp3'):
                    os.remove(file_path)
                    print(f"Eliminado: {file_path}")
        except PermissionError:
            print(f"⚠️ Archivo en uso, reintentando... ({i+1}/{retries})")
            time.sleep(delay)
        except FileNotFoundError:
            return  # ya se eliminó o no existe

# Descargar cada video individualmente y obtener su información
def downloadVideoProcess(video, downloadFolder):
    # videoId = video.get('id', '')
    # title = re.sub(r'[<>:"/\\|?*]', '_', unicodedata.normalize('NFKC', video.get('title', '')))
    # album = video.get('album', '')
    # artist = video.get('uploader', '')
    # output_file_video = os.path.join(downloadFolder, videoId + '.mp4')
    # output_file_audio = os.path.join(downloadFolder, videoId + '.mp3')
    # output_file_image = os.path.join(downloadFolder, videoId + '.jpg')
    # output_file_audio_final = os.path.join(downloadFolder, title + '.mp3')
    
    subprocess.run([
        "yt-dlp",
        "-f", "bestaudio",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--embed-thumbnail",
        "--add-metadata",
        "--parse-metadata", "%(uploader)s:%(artist)s",
        "--parse-metadata", "%(playlist_title)s:%(album)s",
        "--parse-metadata", "%(upload_date>%Y)s:%(date)s",
        "-o", os.path.join(downloadFolder, '%(title)s.%(ext)s'),
        "--ignore-errors",
        "--no-overwrites",
        "--continue",
        video["url"]
    ], check=True)

    # retryFunction(lambda: downloadVideo(video['url'], output_file_video))
    
    # retryFunction(lambda: convertToMp3(output_file_video, output_file_audio))

    # retryFunction(lambda: downloadThumbnail(videoId, output_file_image))

    # retryFunction(lambda: addMetadata(output_file_audio, image_path=output_file_image, title=title, artist=artist, album=album))
    
    # retryFunction(lambda: renameMp3(output_file_audio, output_file_audio_final))

    # retryFunction(lambda: deleteExtraFiles(downloadFolder, output_file_audio))

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
    # deleteExtraFilesGeneral(downloadFolder)

    fin = time.time()

    print(f"⏱️ Tiempo total: {fin - inicio:.2f} segundos")

    # pip install yt-dlp easygui pillow mutagen ffmpeg-python streamlink
    # instalar ffmpeg en el sistema operativo y añadir a la variable PATH
    
    # Ejecutamos: 'pip install auto-py-to-exe' y después 'auto-py-to-exe' o 'python -m auto_py_to_exe'
    
    # pip install -U yt-dlp

    # {
    #     '_type': 'url',
    #     'ie_key': 'Youtube',
    #     'id': 'nk8COybCLuU',
    #     'url': 'https://www.youtube.com/watch?v=nk8COybCLuU',
    #     'title': 'Made in Abyss OST - Pathway (Goodbye My Friend) [メイドインアビス OST]',
    #     'description': None,
    #     'duration': 178,
    #     'channel_id': 'UCdOsR0daJqjpFU2PyIdiQDw',
    #     'channel': 'Pandora Heaven',
    #     'channel_url': 'https://www.youtube.com/channel/UCdOsR0daJqjpFU2PyIdiQDw',
    #     'uploader': 'Pandora Heaven',
    #     'uploader_id': '@pandoraheaven',
    #     'uploader_url': 'https://www.youtube.com/@pandoraheaven',
    #     'thumbnails': [{...}, {...}, {...}, {...}],
    #     'timestamp': None,
    #     'release_timestamp': None,
    #     'availability': None,
    #     'view_count': 5100000,
    #     'live_status': None,
    #     'channel_is_verified': None,
    #     '__x_forwarded_for_ip': None
    # }
