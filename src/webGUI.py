from pywebio.input import *
from pywebio.output import *
from pywebio import start_server

def indexPage():
    # title
    put_text("Unmanned-Surface-Vessel Control-Station").style('font-size: 24px; font-weight: bold; text-align: center; margin-top: 20px;')

    # CSS to improve the layout and appearance
    style = """
    <style>
        body { 
            font-family: Arial, sans-serif;
            margin: 40px; 
            background-color: #f4f4f9;
            color: #333;
        }
        #videoFrame { 
            width: 640px; 
            height: 480px; 
            border: 5px solid #333; 
            display: block; 
            margin: 20px auto;
        }
        h3 { 
            text-align: center; 
            color: #444; 
        }
    </style>
    """
    put_html(style)

    # video GUI screen with HTML & JavaScript for WebSocket
    video_html = """
    <h3>Video Stream</h3>
    <img id="videoFrame" src="" alt="Video Stream">
    <script>
        const socket = new WebSocket('ws://localhost:8765');
        
        socket.onmessage = function(event) {
            const arrayBuffer = event.data;
            const blob = new Blob([arrayBuffer], { type: 'image/jpeg' });
            const url = URL.createObjectURL(blob);
            document.getElementById('videoFrame').src = url;
        };
        
        socket.onclose = function(event) {
            if (event.wasClean) {
                console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
            } else {
                // Server process killed or network down
                console.log('[close] Connection died');
            }
        };
        
        socket.onerror = function(error) {
            console.log(`[error] ${error.message}`);
        };
    </script>
    """
    put_html(video_html)

# TODO:
    # GPS data
    # status of the USV
        # speed
        # acceleration
        # telemetry
    # radar mapping
    # controller input
    # a button to start the SLAM

if __name__ == '__main__':
    start_server(indexPage, port=8080)
