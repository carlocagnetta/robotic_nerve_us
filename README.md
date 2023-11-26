# Robotic Nerve Ultrasound Scanning
### Author:
 Carlo Cagnetta
### Supervisor:
Yordanka Velikova, Vanessa Gonzalez Duque, Felix Dülmer
### External Supervisor:
Michael Panchenko
### Department:
Chair of Computed Aided Medical Prociedures & Augmented Reality \
School of Computation, Information and Technology \
Technical University Munich

---

This repo contains the work of the Master Thesis of the author at the CAMPAR chair at TUM

## Setup
To set up the proper environment for the project please follow the instruction below.

### Docker
In order to reproduce the same environment and run the project in every machine without trubles, this projects uses a Docker container. \
When using [docker](https://www.docker.com/), please make sure to have docker [installed](https://docs.docker.com/desktop/install/linux-install/) properly. Then use `docker-compose.sh` to build the container:
```
./docker-compose.sh
```
This command runs the `docker compose` command:
```
docker compose -f docker-compose.yaml up robUS-<GPU> -d --build
```
* \<GPU> is either `intel` or `nvidia`, depending on your hardware specifications.
* -f docker-compose.yaml: Specifies the location of the Docker Compose file (docker-compose.yaml in this case).
* up robUS-\<GPU>: Instructs Docker Compose to bring up the services defined in the docker-compose.yaml file, with a specific focus on the service named robUS-nvidia.
* -d: Runs the service in the background (detached mode).
* --build: Builds the image before starting the service. This is useful when you have made changes to your Dockerfile or any other related files and want to ensure that the latest image is used.

Once the container is running, you can interact with through a devcontainer or through:
```
docker exec -it <container-id> bash
```

### Poetry
For packaging and dependency management, we use [Poetry](https://python-poetry.org/). Please install the latest version following [this guide](https://python-poetry.org/docs/). \
To install the poetry requirements and start the poetry environment, run:
```
poetry install && poetry shell
```

### Install from source
Some other packages and repositories necessary for the project must be installed from source, which can be done by running the script `install.sh`:
```
./install.sh --all
source ~/.zshrc
```
This includes:
* coppelia: Simulation environment for robot reinforcement learning.
* pyrep: Toolkit for robot learning research, built on top of CoppeliaSim.
* rlbench: Benchmark suite for robot learning.
* libfranka: C++ interface for the Franka Emika research robot.
* frankx: Python wrapper around libfranka.