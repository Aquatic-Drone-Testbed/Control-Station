from pywebio.input import *
from pywebio.output import *
from pywebio import start_server

def indexPage():
    # Title
    put_text("Unmanned Surface Vessel Control Station").style('font-size: 24px; font-weight: bold; text-align: center; margin-top: 20px;')

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
            width: 80%;
            max-width: 1200px;
            margin: 20px auto;
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

        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
                grid-template-rows: auto;
                gap: 10px;
            }

            .diagnosticsPanel {
                grid-template-columns: 1fr;
            }
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
                <div class="diagnosticCard" id="cameraCard">
                    <img src="https://img.icons8.com/ios-filled/50/000000/camera.png" alt="Camera Icon">
                    <div class="label">Camera</div>
                    <div id="cameraStatus" class="value">Off</div>
                </div>
                <div class="diagnosticCard" id="gpsCard">
                    <img src="https://img.icons8.com/ios-filled/50/000000/gps-device.png" alt="GPS Icon">
                    <div class="label">GPS</div>
                    <div id="gpsStatus" class="value">Not Connected</div>
                </div>
                <div class="diagnosticCard" id="imuCard">
                    <img src="https://img.icons8.com/ios-filled/50/000000/gyroscope.png" alt="IMU Icon">
                    <div class="label">IMU</div>
                    <div id="imuStatus" class="value">Off</div>
                </div>
                <div class="diagnosticCard" id="thrusterCard">
                    <img src="https://cdn-icons-png.freepik.com/512/419/419108.png" alt="Thruster Icon">
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
    let cameraStatusElement = document.getElementById("cameraStatus");
    let cameraCard = document.getElementById("cameraCard");
    let gpsStatusElement = document.getElementById("gpsStatus");
    let gpsCard = document.getElementById("gpsCard");

    const socket = new WebSocket('ws://localhost:8765');
    
    socket.onmessage = function(event) {
            const message = event.data;
            if (message.startsWith("camera:")) {
                const imgBlob = message.slice(7); // Get the image part of the message
                const imgUrl = URL.createObjectURL(new Blob([imgBlob], { type: 'image/jpeg' }));
                document.getElementById('cameraVideoFrame').src = imgUrl;
            } 
            if (message.startsWith("_radar:")) {
                const imgBlob = message.slice(7); // Get the image part of the message
                const imgUrl = URL.createObjectURL(new Blob([imgBlob], { type: 'image/jpeg' }));
                document.getElementById('rawRadarVideoFrame').src = imgUrl;
            }
            else {
                const data = JSON.parse(message);
                if (data.type === "diagnostics") {
                    updateDiagnostics(data.data);
                }
            }
        };

    function updateDiagnostics(diagnostics) {
        if (diagnostics.camera) {
            cameraStatusElement.textContent = diagnostics.camera;
            cameraCard.classList.toggle('active', diagnostics.camera === 'On');
            cameraCard.classList.toggle('inactive', diagnostics.camera !== 'On');
        }
        if (diagnostics.gps) {
            gpsStatusElement.textContent = diagnostics.gps;
            gpsCard.classList.toggle('active', diagnostics.gps === 'Connected');
            gpsCard.classList.toggle('inactive', diagnostics.gps !== 'Connected');
        }
        // Update GPS status and other diagnostics similarly
    }

    socket.onopen = function() {
        console.log("WebSocket connection established.");
    };

    socket.onclose = function(event) {
        console.log("WebSocket connection closed:", event);
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