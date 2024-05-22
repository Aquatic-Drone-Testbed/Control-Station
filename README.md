# Control-Station
Control station code for remote operation of Unmanned-Surface-Vehicle(USV). 

# install the required packages

crate a new conda environment with the following command
```bash
    conda create --name capstone python=3.11.7
```
or install the libraries from the `requirements.txt` file (recommended)
```bash
    pip install -r requirements.txt
```

activate the environment
```bash
    conda activate capstone
```

after install a new library, update the environment.yml file with the following command
```bash
   pip freeze > requirements.txt
```

# How to run the Control-Station
1. run the `udp_receiver`:

```bash
    python3 ./src/udp_receiver.py 
```

2. run the `webGUI`:

```bash
    python3 ./src/webGUI.py 
```

2. (Optional) Run the code when you developping with hot reload using watchdog

```bash
    python3 src/auto_reload.py . python3 src/webGUI.py
```