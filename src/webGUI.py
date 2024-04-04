from pywebio.input import *
from pywebio.output import *
from pywebio import start_server
from pywebio.output import put_html

def indexPage():
    # title
    put_text("Unmanned-Surface-Vessel Control-Station") 
    
    # video GUI screen
    # pywebio does not support video streaming, but we can consider using the following code to embed a video
    # 1. Create HTTP streams using FFmpeg
    #      could use something like this: ffmpeg -f rawvideo -pixel_format bgr24 -video_size 640x480 -i - http://localhost:8080/feed.ffm
    # 2. Embed the stream in the web page
    # put_html('<video src="http://localhost:8080/feed.ffm" controls autoplay></video>')

    # GPS data
    
    # status of the USV
        # speed
        # acceleration
        # telemetry
    # radar mapping
    # controlor input
    # a button to start the SLAM


if __name__ == '__main__':
    start_server(indexPage, port=8080)
