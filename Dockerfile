ARG IMAGE
FROM ${IMAGE}
LABEL authors="Carlo Cagnetta"
ARG GPU

# Disable interactive mode for installed packages
ENV DEBIAN_FRONTEND noninteractive
# This seems to be a workaround in a bug in glvnd library
#ENV __GLVND_DISALLOW_PATCHING 1

# alias python version
# RUN ln -s /usr/bin/python3 /usr/bin/python & \
#     ln -s /usr/bin/pip3 /usr/bin/pip

# Install system packages
RUN apt-get update && apt-get install -y apt-utils
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  language-pack-en \
  pip \
  bzip2 \
  sudo \
  curl \
  g++ \
  git \
  ffmpeg \
  vim \
  nano \
  wget \
  htop \
  tmux \
  mesa-utils \
  glmark2 \
  iputils-ping

# Install Intel graphics drivers
RUN if [ "$GPU" = "intel" ] ; then curl fsSL https://repositories.intel.com/graphics/intel-graphics.key | apt-key add - ; fi
RUN if [ "$GPU" = "intel" ] ; then echo "deb [trusted=yes arch=amd64] https://repositories.intel.com/graphics/ubuntu focal main" > /etc/apt/sources.list.d/intel-graphics.list ; fi

RUN if [ "$GPU" = "intel" ] ; then \
  apt-get update && \
  apt-get -y install libgl1-mesa-glx libgl1-mesa-dri  && \
  rm -rf /var/lib/apt/lists/* ; fi

# Install Nvidia graphics drivers
RUN if [ "$GPU" = "nvidia" ] ; then apt-get update && apt-get install -y nvidia-container-toolkit ; fi

# install zsh
RUN apt update && apt install -y zsh \
  && chsh -s $(which zsh) \
  && sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" \
  && git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

# modify .zshrc to allow nice plugins
RUN sed -i '11s/ZSH_THEME="robbyrussell"/ZSH_THEME="agnoster"/' ~/.zshrc
RUN sed -i '73s/plugins=(git)/plugins=(git zsh-syntax-highlighting)/' ~/.zshrc

# Add user
ENV DEV_USER dev_user
RUN useradd -rm -d /home/$DEV_USER -s /bin/bash -p "$(openssl passwd -1 $DEV_USER)" -u 1000 $DEV_USER
RUN chown -R $DEV_USER /home/$DEV_USER

# ROS related packages

## Set ROS distro
ENV ROS_DISTRO noetic

## install ros related packages for nvidia
RUN if [ "$GPU" = "nvidia" ] ; then apt-get update && apt-get install -y --no-install-recommends \
    lsb-release \
    gnupg2 \
    nvidia-container-toolkit \
    && rm -rf /var/lib/apt/lists/* ; fi
## add ros noetic repo
RUN if [ "$GPU" = "nvidia" ] ; then curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add - && \
  sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-noetic.list'; fi

## update package list and install ros noetic
RUN apt update && \
  apt install -y --no-install-recommends \
  ros-noetic-desktop \
  && rm -rf /var/lib/apt/lists/*

## install bootstrap tools
RUN apt-get update && apt-get install --no-install-recommends -y \
  build-essential \
  python3-rosdep \
  python3-rosinstall \
  python3-rosinstall-generator \
  python3-wstool \
  python3-vcstools \
  && rm -rf /var/lib/apt/lists/*

## bootstrap rosdep
RUN rosdep init && \
  rosdep update --rosdistro $ROS_DISTRO

## source ros distro
RUN echo 'source "/opt/ros/$ROS_DISTRO/setup.zsh"' >> ~/.zshrc

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"
ENV POETRY_VIRTUALENVS_IN_PROJECT=1

WORKDIR /home/$DEV_USER/robotic_nerve_us

CMD tail -f /dev/null