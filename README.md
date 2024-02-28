# Control-Station
Control station code for remote operation of Unmanned-Surface-Vehicle(USV). 

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
    conda env export --no-builds > environment.yml
```