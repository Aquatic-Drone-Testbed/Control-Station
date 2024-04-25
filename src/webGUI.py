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
    <h3>Camera Video Stream</h3>
    <img id="cameraVideoFrame" class="videoFrame" src="" alt="Camera Video Stream">
    <h3>Radar Video Stream</h3>
    <img id="radarVideoFrame" class="videoFrame" src="" alt="Radar Video Stream">
    <script>
        const socket = new WebSocket('ws://localhost:8765');
        
        socket.onmessage = function(event) {
            
            // The first part of the message is the type identifier followed by a colon
            const typeIdentifierLength = 6; // Length of 'camera:' or 'radar:'
            
            // Get the stream type from the identifier
            const streamType = event.data.slice(0, typeIdentifierLength).decode();
            // Extract the image data
            const imageData = event.data.slice(typeIdentifierLength);
            const blob = new Blob([imageData], { type: 'image/jpeg' });
            const url = URL.createObjectURL(blob);

            if (streamType === 'camera') {
                document.getElementById('mainVideoFrame').src = url;
            } else if (streamType === 'radar') {
                document.getElementById('radarVideoFrame').src = url;
            }
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
