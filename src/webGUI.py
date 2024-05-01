from pywebio.input import *
from pywebio.output import *
from pywebio import start_server

def indexPage():
    # title
    put_text("Unmanned-Surface-Vessel Control-Station").style('font-size: 24px; font-weight: bold; text-align: center; margin-top: 20px;')

    # CSS to improve the layout and appearance
    style = """
    <style>
        /* CSS Reset */
        * {
            margin: 0;
            padding: 0;
        }

        html, body, .pywebio, #output-container, .container {
            width: 100%; 
            height: 100%;
            max-width: 100%;
            overflow: hidden;
        }

        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            background-color: #f4f4f9;
            color: #333;
        }

        .videoContainer {
            display: flex;
            justify-content: space-around;
            width: 100%;
            align-items: center;
            flex-wrap: nowrap;
            padding: 0 20px;
        }

        .videoContainer > div {
            flex: 1;
            padding: 10px;
            box-sizing: border-box;
        }

        .videoFrame { 
            width: 100%;
            /* height: 480px; */
            border: 5px solid #333; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-radius: 8px; 
        }

        h3 { 
            text-align: center; 
            color: #444; 
            margin-bottom: 10px;
        }
    </style>
    """
    
    put_html(style)

    # video GUI screen with HTML & JavaScript for WebSocket
    video_html = """
    <div class="videoContainer">
        <div>
            <h3>Camera Video Stream</h3>
            <img id="cameraVideoFrame" class="videoFrame" src="" alt="Camera Video Stream">
        </div>
        <div>
            <h3>Radar Video Stream</h3>
            <img id="radarVideoFrame" class="videoFrame" src="" alt="Radar Video Stream">
        </div>
    </div>
    <script>
        const socket = new WebSocket('ws://localhost:8765');
        
        socket.onopen = function(e) {
            console.log("Connection established");
        };

        socket.onmessage = function(event) {
            console.log("Message from server ", event.data);
        };

        socket.onclose = function(event) {
            if (event.wasClean) {
                console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
            } else {
                console.log('[close] Connection died');
            }
        };

        socket.onerror = function(error) {
            console.log(`[error] ${error.message}`);
        };

        socket.onmessage = function(event) {
            // console.log("Received binary data"); // Confirm binary data reception
            let reader = new FileReader(); // event.data is a Blob of binary data
            reader.onload = function() {
                // console.log("ArrayBuffer loaded"); // Confirm ArrayBuffer is loaded
                let arrayBuffer = this.result;
                let dataView = new DataView(arrayBuffer);
                let decoder = new TextDecoder("ascii");

                // Decode the first 6 bytes as the label, hard-code all type to be 6 bytes
                let label = decoder.decode(dataView.buffer.slice(0, 6)).trim();
                // console.log("Label decoded:", label); // Display the decoded label

                let imageBlob = new Blob([dataView.buffer.slice(7)], {type: 'image/jpeg'});
                let imageUrl = URL.createObjectURL(imageBlob);

                if (label === 'camera') {
                    document.getElementById('cameraVideoFrame').src = imageUrl;
                } else if (label === '_radar') {
                    document.getElementById('radarVideoFrame').src = imageUrl;
                }
            };
            reader.readAsArrayBuffer(event.data);
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