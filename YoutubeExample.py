from pytube import YouTube

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

#set stream resolution
out_file = video.streams.filter(adaptive=True, file_extension='mp4').order_by('resolution').desc().first().download()

print("fps= ",video.streams.filter(adaptive=True, file_extension='mp4').order_by('resolution').desc().first().fps)

#or
#video = video.streams.first()

#Download video
#video.download()
