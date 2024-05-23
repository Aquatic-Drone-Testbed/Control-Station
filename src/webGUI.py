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
            box-sizing: border-box;
        }

        html, body, .pywebio, #output-container, .container {
            width: 100%; 
            height: 100%;
            max-width: 100%;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            color: #333;
        }

        .content {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }

        .gridContainer {
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 20px;
            width: 80%;
            justify-content: center;
        }

        .diagnosticContainer {
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 10px;
            padding: 20px;
            border: 5px solid #333; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-radius: 8px; 
            background-color: #fff;
            text-align: center;
        }

        .videoFrame, .diagnosticContainer { 
            width: 100%;
        }

        .icon {
            width: 50px;
            height: 50px;
            margin-bottom: 10px;
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
    <div class="content">
        <div class="gridContainer">
            <div>
                <h3>Camera Video Stream</h3>
                <img id="cameraVideoFrame" class="videoFrame" src="" alt="Camera Video Stream">
            </div>
            <div>
                <h3>Diagnostic Panel</h3>
                <div class="diagnosticContainer">
                    <div>
                        <img src="https://static-00.iconduck.com/assets.00/camera-icon-2048x1665-tjx7d3d2.png" class="icon" alt="Camera Icon">
                        <p id="cameraStatus">Camera Status</p>
                    </div>
                    <div>
                        <img src="https://cdn-icons-png.flaticon.com/512/1248/1248333.png" class="icon" alt="GPS Icon">
                        <p id="gpsStatus">GPS Status</p>
                    </div>
                    <div>
                        <img src="https://cdn-icons-png.flaticon.com/512/4259/4259396.png" class="icon" alt="Radar Icon">
                        <p id="radarStatus">Radar Status</p>
                    </div>
                    <div>
                        <img src="https://sheatransitions.com/wp-content/uploads/2019/04/image-placeholder-icon-10.png" class="icon" alt="PLACEHOLDER Icon">
                        <p id="PLACEHOLDERStatus">PLACEHOLDER Status</p>
                    </div>
                </div>
            </div>
            <div>
                <h3>Radar Video Stream</h3>
                <img id="radarVideoFrame" class="videoFrame" src="" alt="Radar Video Stream">
            </div>
            <div>
                <h3>SLAM Algorithm Stream</h3>
                <img id="slamVideoFrame" class="videoFrame" src="" alt="SLAM Algorithm Stream">
            </div>
        </div>
    </div>
    <script>
        const socket = new WebSocket('ws://localhost:8765');
        
        socket.onopen = () => console.log("Connected established");

        socket.onclose = event => {
            if (event.wasClean) {
                console.log(`Connection closed cleanly, code=${event.code}, reason=${event.reason}`);
            } else {
                console.log('Connection died');
            }
        };

        socket.onerror = error => console.log(`WebSocket error: ${error.message}`);
        socket.onmessage = event => {
            if (typeof event.data === 'string') {
                // Handle JSON text updates
                console.log("Received JSON message:", event.data);
                const message = JSON.parse(event.data);

                if (message.type === 'diagnostics') {
                    const diagnosticsData = message.data;

                    // Set the status text for each sensor
                    if (diagnosticsData.includes('Camera:')) {
                        document.getElementById('cameraStatus').innerText = diagnosticsData;
                    } else if (diagnosticsData.includes('GPS:')) {
                        document.getElementById('gpsStatus').innerText = diagnosticsData;
                    } else if (diagnosticsData.includes('Radar:')) {
                        document.getElementById('radarStatus').innerText = diagnosticsData;
                    }
                } else if (message.type === 'video') {
                    const { label, data } = message;

                    // Create a Blob from the base64 encoded data
                    const byteCharacters = atob(data);
                    const byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }
                    const byteArray = new Uint8Array(byteNumbers);
                    const blob = new Blob([byteArray], { type: 'image/jpeg' });
                    const imageUrl = URL.createObjectURL(blob);

                    // Update the video frame based on the label
                    if (label === 'camera') {
                        document.getElementById('cameraVideoFrame').src = imageUrl;
                    } else if (label === 'radar') {
                        document.getElementById('radarVideoFrame').src = imageUrl;
                    } else if (label === 'slam') {
                        document.getElementById('slamVideoFrame').src = imageUrl;
                    }
                }
            } else {
                // Handle binary image data
                const reader = new FileReader(); // event.data is a Blob of binary data
                reader.onload = () => {
                    const arrayBuffer = reader.result;
                    const dataView = new DataView(arrayBuffer);
                    const decoder = new TextDecoder("ascii");

                    const label = decoder.decode(dataView.buffer.slice(0, 6)).trim();
                    const data = decoder.decode(dataView.buffer.slice(7)).trim();

                    // Decode the first 6 bytes as the label, hard-code all type to be 6 bytes
                    const imageBlob = new Blob([dataView.buffer.slice(7)], { type: 'image/jpeg' });
                    const imageUrl = URL.createObjectURL(imageBlob);

                    if (label === 'status') {
                        const diagnosticsData = JSON.parse(data);
                        document.getElementById('cameraStatus').innerText = diagnosticsData.camera;
                        document.getElementById('gpsStatus').innerText = diagnosticsData.gps;
                        document.getElementById('radarStatus').innerText = diagnosticsData.radar;
                        document.getElementById('imuStatus').innerText = diagnosticsData.imu;
                    } else {
                        const imageBlob = new Blob([dataView.buffer.slice(7)], { type: 'image/jpeg' });
                        const imageUrl = URL.createObjectURL(imageBlob);
                        if (label === 'camera') {
                            document.getElementById('cameraVideoFrame').src = imageUrl;
                        } else if (label === '_radar') {
                            document.getElementById('radarVideoFrame').src = imageUrl;
                        } else if (label === '__slam') {
                            document.getElementById('slamVideoFrame').src = imageUrl;
                        }
                    }
                };
                reader.readAsArrayBuffer(event.data);
            }
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