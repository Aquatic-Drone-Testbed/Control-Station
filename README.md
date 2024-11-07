# Control-Station
Control station code for remote operation of Unmanned-Surface-Vehicle(USV).

# install the required packages

create a new conda environment with the following command
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

after installing a new library, update the `requirements.txt` file with the following commands
```bash
   ~~pip freeze > requirements.txt~~ 
   Note from Alex: pip freeze only saves the packages that are installed with pip install in your environment.
   Also, pip freeze saves all packages in the environment including those that you don't use in your current project (if you don't have virtualenv)

   So it is recommended that you use this instead:

   pip install pipreqs
   pipreqs /path/to/project
```


# To run Control-Station:
```bash
    ./run-control-station.sh
```

# (Optional) Run the code when you developping with hot reload using watchdog

```bash
    python3 src/auto_reload.py . python3 src/webGUI.py
```