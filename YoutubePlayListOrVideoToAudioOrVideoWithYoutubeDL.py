'''
YouTube Video Downloader
Author: Ayushi Rawat
'''

#import the package
from pytube import YouTube
from pytube import Playlist
from datetime import datetime
import os
import shutil
#from __future__ import unicode_literals
import youtube_dl


#Funciones auxiliares:

#def arreglarNombre(text):
#    for ch in ['\\','\/',':','*','?','\"','<','>','|']:
#        if ch in text:
#            text = text.replace(ch,".")
#    return text


def CreateFolder():
    try:
        dir = "./DownloadedFiles"
    
        os.mkdir(dir) 
        print("Directory '% s' is built!" % dir) 
    except:
        pass


def DownloadMP3(videoURL):
    """
    Dado un video de Youtube, me descarga el vídeo como MP3 y me retorna el nombre del archivo MP3
    """

    print('Executing...')

    try:
        video_info = youtube_dl.YoutubeDL().extract_info(
            url = videoURL,download=False
        )
        filename = f"DownloadedFiles\{video_info['title']}.mp3"
        options={
            'format':'bestaudio/best',
            'keepvideo':False,
            'outtmpl':filename,
        }

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([video_info['webpage_url']])
    except:
        print('Some error in downloading: ', videoURL)

    return videoURL


def DownloadMP4(videoURL, high_resol = False):
    """
    Dado un video de Youtube, me descarga el vídeo como MP4 y me retorna el nombre del archivo MP4 y sus fps
    """

    print('Executing...')

    try:
        video_info = youtube_dl.YoutubeDL().extract_info(
            url = videoURL,download=False
        )
        filename = f"DownloadedFiles\{video_info['title']}.mp4"
        options={
            'format':'bestvideo+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
            'merge-output-format' : 'mp4',
            'keepvideo':False,
            'outtmpl':filename,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
        }

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([video_info['webpage_url']])
    except:
        print('Some error in downloading: ', videoURL)

    return videoURL


#High resolution aún en fase de pruebas
def DownloadMP4HighResolution():
    
    def combine_audio(vidname, audname, outname, fps=25):
        import moviepy.editor as mpe
        my_clip = mpe.VideoFileClip(vidname)
        audio_background = mpe.AudioFileClip(audname)
        final_clip = my_clip.set_audio(audio_background)
        final_clip.write_videofile(outname,fps=fps)

    audname = DownloadMP3(video_url)
    vidname, fps = DownloadMP4(video_url, True)
    outname = vidname + "HD"
    combine_audio(vidname, audname, outname, fps)
    os.remove(audname)


#Descarga de un video individual
def SingleDownload(video_url, finish = False):
    list = SelectDownload()
    if (list != []):
        try:
            list[0](video_url)
        except:
            print("\n")
            print("Invalid Youtube link, please reexecute the program")

        finish = True

    return finish


#Seleccionar descarga de MP3 o MP4
def SelectDownload():
    list = []
    #Si lo quiero en MP4
    if (MP3Mp4BoolString == 'n'):
        list.append(DownloadMP4)
    #Si lo quiero en MP3
    elif (MP3Mp4BoolString == 'y'):
        list.append(DownloadMP3)
    #En otro caso
    else:
        print("Unexpected MP3 or MP4 response, reexecute the program")

    return list


#Descarga de toda la playlist
def PlayListDownload(video_url, finish = False):
    p = Playlist(video_url)
    
    list = SelectDownload()
    if (list != []):
        try:
            for url in p.video_urls:
                print(url)
                list[0](url)

        except:
            print("\n")
            print("Invalid Youtube link, please reexecute the program")
        
        finish = True
    
    return finish
      

#Descargar todas las URLs del text
def ReadTXT(texto, finish = False):
    lines = []
    count = 0
    
    list = SelectDownload()
    if (list != []):

        try:
            with open(texto) as f:
                lines = f.readlines()
            print("Encontradas ", len(lines), "URLs.")
        except:
            print("\n")
            print("Problem with the text file")

        for video_url in lines:
            count += 1
            
            try:
                list[0](video_url)
            except:
                print("\n")
                print("Invalid Youtube link")

            print("Video ", count, "...")

        if (len(lines) > 0): finish = True
    
    return finish


#Preguntas para la descarga por URL
def Preguntas1():
    video_url = input("Please enter a valid youtube video url: ")
    PlayListBoolString = input("It's a playlist (y/n): ")
    MP3Mp4BoolString = input("Do u want it in mp3? [y=mp3, n=mp4] (y/n): ")
    if (MP3Mp4BoolString == "n"): print("Tenga en cuenta que la calidad de vídeo no podrá ser superior a 720p. Estamos trabajando para mejorarlo.")

    current_time1 = datetime.now() #Guardamos el tiempo para después calcular el tiempo que tarda el programa en ejecutar.

    return video_url, PlayListBoolString, MP3Mp4BoolString, current_time1


#Preguntas para la descarga por text
def Preguntas2():
    text = input("please enter the name/path of the text: ")
    MP3Mp4BoolString = input("Do u want it in mp3? [y=mp3, n=mp4] (y/n): ")

    current_time1 = datetime.now() #Guardamos el tiempo para después calcular el tiempo que tarda el programa en ejecutar.

    return text, MP3Mp4BoolString, current_time1








#Codigo del programa
CreateFolder()
finish = False
while (finish == False):
    URLorTEXTBoolString = input("It's a URL or a TEXT? [y=URL, n=TEXT] (y/n):")

    #Si es URL
    if (URLorTEXTBoolString == 'y'):
        video_url, PlayListBoolString, MP3Mp4BoolString, current_time1= Preguntas1()

        #Si no es playlist
        if (PlayListBoolString == 'n'):
            finish = SingleDownload(video_url)

        #Si es playlist
        elif (PlayListBoolString == 'y'):
            finish = PlayListDownload(video_url)

        #En otro caso
        else:
            print("\n")
            print("Unexpected Yes or No Playlist response")

    #Si es TEXT
    elif (URLorTEXTBoolString == 'n'):
        text, MP3Mp4BoolString, current_time1 = Preguntas2()

        finish = ReadTXT(text)

    #En otro caso
    else:
        print("\n")
        print("Unexpected URL or TEXT response")

        current_time1 = datetime.now() #Guardamos el tiempo para después calcular el tiempo que tarda el programa en ejecutar.



current_time2 = datetime.now()

print("\n")
print("tiempo en HH:MM:SS = ", current_time2 - current_time1)

#Fin del codigo del programa








"""
video_url = input("please enter youtube video url:")

video = YouTube(video_url)

print("*********************Video Title************************")
#get Video Title
print(video.title)

print("********************Tumbnail Image***********************")
#get Thumbnail Image
print(video.thumbnail_url)

print("Views: ", video.views)
print("Length: ", video.length, "seconds")
print("Publish date: ", video.publish_date)
#print("Description: ", video.description)
print("Ratings: ", video.rating)

print("********************Download video*************************")
#get all the stream resolution for the 
for stream in video.streams:
    print(stream)

#get all the stream resolution for the video
for stream in video.streams:
    print(stream)
print("\n")


#<Stream: itag="17" mime_type="video/3gpp" res="144p" fps="8fps" vcodec="mp4v.20.3" acodec="mp4a.40.2" progressive="True" type="video">
#<Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" type="video">
#<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2" progressive="True" type="video">
#<Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028" progressive="False" type="video">
#<Stream: itag="248" mime_type="video/webm" res="1080p" fps="30fps" vcodec="vp9" progressive="False" type="video">
#<Stream: itag="399" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="av01.0.08M.08" progressive="False" type="video">
#<Stream: itag="136" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.4d401f" progressive="False" type="video">
#<Stream: itag="247" mime_type="video/webm" res="720p" fps="30fps" vcodec="vp9" progressive="False" type="video">
#<Stream: itag="398" mime_type="video/mp4" res="720p" fps="30fps" vcodec="av01.0.05M.08" progressive="False" type="video">
#<Stream: itag="135" mime_type="video/mp4" res="480p" fps="30fps" vcodec="avc1.4d401f" progressive="False" type="video">
#<Stream: itag="244" mime_type="video/webm" res="480p" fps="30fps" vcodec="vp9" progressive="False" type="video">
#<Stream: itag="397" mime_type="video/mp4" res="480p" fps="30fps" vcodec="av01.0.04M.08" progressive="False" type="video">
#<Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e" progressive="False" type="video">
#<Stream: itag="243" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp9" progressive="False" type="video">
#<Stream: itag="396" mime_type="video/mp4" res="360p" fps="30fps" vcodec="av01.0.01M.08" progressive="False" type="video">
#<Stream: itag="133" mime_type="video/mp4" res="240p" fps="30fps" vcodec="avc1.4d4015" progressive="False" type="video">
#<Stream: itag="242" mime_type="video/webm" res="240p" fps="30fps" vcodec="vp9" progressive="False" type="video">
#<Stream: itag="395" mime_type="video/mp4" res="240p" fps="30fps" vcodec="av01.0.00M.08" progressive="False" type="video">
#<Stream: itag="160" mime_type="video/mp4" res="144p" fps="30fps" vcodec="avc1.4d400c" progressive="False" type="video">
#<Stream: itag="278" mime_type="video/webm" res="144p" fps="30fps" vcodec="vp9" progressive="False" type="video">
#<Stream: itag="394" mime_type="video/mp4" res="144p" fps="30fps" vcodec="av01.0.00M.08" progressive="False" type="video">
#<Stream: itag="139" mime_type="audio/mp4" abr="48kbps" acodec="mp4a.40.5" progressive="False" type="audio">
#<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audio">
#<Stream: itag="249" mime_type="audio/webm" abr="50kbps" acodec="opus" progressive="False" type="audio">
#<Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus" progressive="False" type="audio">
#<Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus" progressive="False" type="audio">
#<Stream: itag="17" mime_type="video/3gpp" res="144p" fps="8fps" vcodec="mp4v.20.3" acodec="mp4a.40.2" progressive="True" type="video">
#<Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" type="video">
#<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2" progressive="True" type="video">
#<Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028" progressive="False" type="video">
#<Stream: itag="248" mime_type="video/webm" res="1080p" fps="30fps" vcodec="vp9" progressive="False" type="video">
#<Stream: itag="399" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="av01.0.08M.08" progressive="False" type="video">
#<Stream: itag="136" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.4d401f" progressive="False" type="video">
#<Stream: itag="247" mime_type="video/webm" res="720p" fps="30fps" vcodec="vp9" progressive="False" type="video">
#<Stream: itag="398" mime_type="video/mp4" res="720p" fps="30fps" vcodec="av01.0.05M.08" progressive="False" type="video">
#<Stream: itag="135" mime_type="video/mp4" res="480p" fps="30fps" vcodec="avc1.4d401f" progressive="False" type="video">
#<Stream: itag="244" mime_type="video/webm" res="480p" fps="30fps" vcodec="vp9" progressive="False" type="video">
#<Stream: itag="397" mime_type="video/mp4" res="480p" fps="30fps" vcodec="av01.0.04M.08" progressive="False" type="video">
#<Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e" progressive="False" type="video">
#<Stream: itag="243" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp9" progressive="False" type="video">
#<Stream: itag="396" mime_type="video/mp4" res="360p" fps="30fps" vcodec="av01.0.01M.08" progressive="False" type="video">
#<Stream: itag="133" mime_type="video/mp4" res="240p" fps="30fps" vcodec="avc1.4d4015" progressive="False" type="video">
#<Stream: itag="242" mime_type="video/webm" res="240p" fps="30fps" vcodec="vp9" progressive="False" type="video">
#<Stream: itag="395" mime_type="video/mp4" res="240p" fps="30fps" vcodec="av01.0.00M.08" progressive="False" type="video">
#<Stream: itag="160" mime_type="video/mp4" res="144p" fps="30fps" vcodec="avc1.4d400c" progressive="False" type="video">
#<Stream: itag="278" mime_type="video/webm" res="144p" fps="30fps" vcodec="vp9" progressive="False" type="video">
#<Stream: itag="394" mime_type="video/mp4" res="144p" fps="30fps" vcodec="av01.0.00M.08" progressive="False" type="video">
#<Stream: itag="139" mime_type="audio/mp4" abr="48kbps" acodec="mp4a.40.5" progressive="False" type="audio">
#<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audio">
#<Stream: itag="249" mime_type="audio/webm" abr="50kbps" acodec="opus" progressive="False" type="audio">
#<Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus" progressive="False" type="audio">
#<Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus" progressive="False" type="audio">


#set stream resolution
video = video.streams.filter(only_audio=True).order_by('abr').desc().first()

#or
#video = video.streams.first()

#Download video
video.download()
"""