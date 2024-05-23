# Control-Station
Control station code for remote operation of Unmanned-Surface-Vehicle(USV).  

To run:
```bash
    ./run-control-station.sh
```

# install the required packages

crate a new conda environment with the following command
```bash
    conda create --name capstone python=3.11.7
```
or install the environment from the environment.yml file (recommended)
```bash
    conda env create -f environment.yml
```

activate the environment
```bash
    conda activate capstone
```

after install a new library, update the environment.yml file with the following command
```bash
    conda env export --no-builds > environment-mac.yml
    conda env export --no-builds > environment-win.yml
```

# Run the code when you developping with hot reload using watchdog
```bash
    python3 src/auto_reload.py . python3 src/webGUI.py
    
```