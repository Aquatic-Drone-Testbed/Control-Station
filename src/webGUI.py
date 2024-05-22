from pywebio.input import *
from pywebio.output import *
from pywebio import start_server

def indexPage():
    # Title
    put_text("Unmanned Surface Vessel Control Station").style('font-size: 24px; font-weight: bold; text-align: center; margin-top: 20px;')

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

        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 20px;
            width: 100%;
            padding: 20px;
        }

        .videoSection, .diagnosticsSection {
            padding: 10px;
            box-sizing: border-box;
        }

        .videoFrame, .diagnosticsPanel { 
            width: 100%;
            height: 100%;
            border: 5px solid #333; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-radius: 8px; 
        }

        .diagnosticsPanel {
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-gap: 10px;
            padding: 10px;
        }

        .diagnosticsCard {
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .diagnosticsCard.active {
            background-color: #2ecc71;
            color: #ffffff;
        }

        .diagnosticsCard.inactive {
            background-color: #e74c3c;
            color: #ffffff;
        }

        .diagnosticsIcon {
            font-size: 24px;
            margin-right: 10px;
        }

        h3 { 
            text-align: center; 
            color: #444; 
            margin-bottom: 10px;
        }
    </style>
    """
    
    put_html(style)

    # GUI layout with HTML & JavaScript for WebSocket
    gui_html = """
    <div class="container">
        <div class="videoSection">
            <h3>Camera Video Stream</h3>
            <img id="cameraVideoFrame" class="videoFrame" src="" alt="Camera Video Stream">
        </div>
        <div class="diagnosticsSection">
            <h3>Diagnostics Panel</h3>
            <div id="diagnosticsPanel" class="diagnosticsPanel">
                <div class="diagnosticCard">
                    <img src="https://img.icons8.com/ios-filled/50/000000/camera.png" alt="Camera Icon">
                    <div class="label">Camera</div>
                    <div id="cameraStatus" class="value">Off</div>
                </div>
                <div class="diagnosticCard">
                    <img src="https://img.icons8.com/ios-filled/50/000000/gps-device.png" alt="GPS Icon">
                    <div class="label">GPS</div>
                    <div id="gpsStatus" class="value">Off</div>
                </div>
                <div class="diagnosticCard">
                    <img src="https://img.icons8.com/ios-filled/50/000000/gyroscope.png" alt="IMU Icon">
                    <div class="label">IMU</div>
                    <div id="imuStatus" class="value">Off</div>
                </div>
                <div class="diagnosticCard">
                    <img src="https://img.icons8.com/ios-filled/50/000000/boat.png" alt="Thruster Icon">
                    <div class="label">Thruster</div>
                    <div id="thrusterStatus" class="value">Off</div>
                </div>
            </div>
        </div>
        <div class="videoSection">
            <h3>Raw Radar Video Stream</h3>
            <img id="rawRadarVideoFrame" class="videoFrame" src="" alt="Raw Radar Video Stream">
        </div>
        <div class="videoSection">
            <h3>Filtered Radar Video Stream</h3>
            <img id="filteredRadarVideoFrame" class="videoFrame" src="" alt="Filtered Radar Video Stream">
        </div>
    </div>
    <script>
    const socket = new WebSocket('ws://localhost:8765');
    
    socket.onopen = function(e) {
        console.log("Connection established");
    };

    socket.onmessage = function(event) {
        // Check if the received data is a Blob (binary data) or a string (text data)
        if (typeof event.data === 'string') {
            // Handle text data (diagnostics)
            try {
                let json = JSON.parse(event.data);
                if (json.type === 'diagnostics') {
                    console.log('Diagnostics received:', json.data); // Log diagnostic data
                    if (json.data.camera) {
                        let cameraElement = document.getElementById('cameraStatus');
                        if (cameraElement) {
                            cameraElement.innerText = json.data.camera;
                        }
                    }
                    if (json.data.gps) {
                        let gpsElement = document.getElementById('gpsStatus');
                        if (gpsElement) {
                            gpsElement.innerText = json.data.gps;
                        }
                    }
                    // Add other diagnostics updates here with similar checks
                }
            } catch (e) {
                console.error('Failed to parse JSON:', e);
            }
        } else {
            // Handle binary data (images)
            let reader = new FileReader(); // event.data is a Blob of binary data
            reader.onload = function() {
                let arrayBuffer = this.result;
                let dataView = new DataView(arrayBuffer);
                let decoder = new TextDecoder("ascii");

                // Decode the first 6 bytes as the label, hard-code all type to be 6 bytes
                let label = decoder.decode(dataView.buffer.slice(0, 6)).trim();

                if (label === 'camera' || label === '_radar') {
                    let imageBlob = new Blob([dataView.buffer.slice(7)], {type: 'image/jpeg'});
                    let imageUrl = URL.createObjectURL(imageBlob);

                    if (label === 'camera') {
                        document.getElementById('cameraVideoFrame').src = imageUrl;
                        document.getElementById('rawRadarVideoFrame').src = imageUrl;
                        document.getElementById('filteredRadarVideoFrame').src = imageUrl;
                    } else if (label === '_radar') {
                        document.getElementById('rawRadarVideoFrame').src = imageUrl;
                        document.getElementById('filteredRadarVideoFrame').src = imageUrl;
                    }
                }
            };
            reader.readAsArrayBuffer(event.data);
        }
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
</script>

    """

    put_html(gui_html)

if __name__ == '__main__':
    start_server(indexPage, port=8080)

# # TODO:
#     # GPS data
#     # status of the USV
#         # speed
#         # acceleration
#         # telemetry
#     # radar mapping
#     # controller input
#     # a button to start the SLAM