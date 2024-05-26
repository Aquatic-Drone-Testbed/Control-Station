# Control-Station
Control station code for remote operation of Unmanned-Surface-Vehicle(USV).

# install the required packages

crate a new conda environment with the following command
```bash
    conda create --name capstone python=3.11.7
```

activate the environment
```bash
    conda activate capstone
```

install the libraries from the `requirements.txt` file (recommended)
```bash
    pip install -r requirements.txt
```

after install a new library, update the `requirements.txt` file with the following command
```bash
   pip freeze > requirements.txt
```


# To run Control-Station:
```bash
    ./run-control-station.sh
```

# (Optional) Run the code when you developping with hot reload using watchdog

```bash
    python3 src/auto_reload.py . python3 src/webGUI.py
```