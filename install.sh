#!/usr/bin/env bash

set -euo pipefail

SCRIPT_PARENT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." &>/dev/null && pwd)"
LIBRARY_DEPENDENCIES="build-essential cmake git libpoco-dev libeigen3-dev"
COPPELIASIM_ROOT="${COPPELIASIM_ROOT:-}"

function log() {
    local level=$1
    shift
    printf "[%s] %s\n" "$level" "$*"
}

function error() {
    log ERROR "$@"
}

function info() {
    log INFO "$@"
}

function warn() {
    info "$@"
}

function debug() {
    [ -n "${DEBUG:-}" ] && log DEBUG "$@"
}

function usage() {
    cat <<EOF
Usage: $(basename "$0") [--coppelia] [--pyrep] [--rlbench] [--libfranka] [--frankx] [--franka-ros] [--moveit] [--all] [--help/-h]
Install required software packages for robot reinforcement learning.

Options:
   --coppelia    Download and install CoppeliaSim. Simulation environment for robot reinforcement learning.
   --pyrep       Download and install PyRep. Toolkit for robot learning research, built on top of CoppeliaSim.
   --rlbench     Download and install RLBench. Benchmark suite for robot learning.
   --libfranka   Download and install libfranka. C++ interface for the Franka Emika research robot.
   --frankx      Download and install frankx. Python wrapper around libfranka.
   --franka-ros  Download and install franka ROS.
   --moveit      Download and install MoveIt. Control libraries for Franka Robot on ROS.
   --all         Download and install all packages.
   --help/-h     Show this help message.
EOF
}


function install_coppelia() {
    local coppelia_version=${1:-V4_1_0}
    local os_version=${2:-Ubuntu20_04}
    local coppelia_dir="${SCRIPT_PARENT}/CoppeliaSim_Edu_${coppelia_version}_${os_version}"
    local download_url="https://www.coppeliarobotics.com/files/CoppeliaSim_Edu_${coppelia_version}_${os_version}.tar.xz"
    local coppelia_tar="CoppeliaSim_Edu_${coppelia_version}_${os_version}.tar.xz"

    if ! command -v wget tar >/dev/null 2>&1; then
        error "Please install wget and tar before running this script."
        return 1
    fi

    local shell_init_file=
        case $SHELL in
            */bash) shell_init_file="${HOME}/.bashrc" ;;
            */zsh) shell_init_file="${HOME}/.zshrc" ;;
            *) shell_init_file="${HOME}/.profile" ;;
        esac

    if ! grep -q "COPPELIASIM_ROOT" "$shell_init_file"; then
        info "Adding COPPELIASIM_ROOT to $shell_init_file"
        sed -i '/^export '"COPPELIASIM_ROOT"'/d' "$shell_init_file"
        export COPPELIASIM_ROOT="${coppelia_dir}"
        echo "export COPPELIASIM_ROOT=${coppelia_dir}" >>"$shell_init_file"
    fi

    if [[ ! "${LD_LIBRARY_PATH}" =~ "${COPPELIASIM_ROOT}" ]]; then
        info "Adding COPPELIASIM_ROOT to LD_LIBRARY_PATH"
        sed -i '/^export '"LD_LIBRARY_PATH"'/d' "$shell_init_file"
        echo "export LD_LIBRARY_PATH=${COPPELIASIM_ROOT}:${LD_LIBRARY_PATH}" >> "$shell_init_file"
        export LD_LIBRARY_PATH=${COPPELIASIM_ROOT}:${LD_LIBRARY_PATH}
    fi

    if ! grep -q "QT_QPA_PLATFORM_PLUGIN_PATH" "$shell_init_file" || [ ! -n "${QT_QPA_PLATFORM_PLUGIN_PATH}" ]; then
        info "Adding QT_QPA_PLATFORM_PLUGIN_PATH to $shell_init_file"
        sed -i '/^export '"QT_QPA_PLATFORM_PLUGIN_PATH"'/d' "$shell_init_file"
        echo "export QT_QPA_PLATFORM_PLUGIN_PATH=${COPPELIASIM_ROOT}" >> "$shell_init_file"
    fi

    if [ -n "${COPPELIASIM_ROOT}" ] && [ -d "${COPPELIASIM_ROOT}" ] && [ -x "${COPPELIASIM_ROOT}/coppeliaSim" ]; then
        export COPPELIASIM_ROOT="${coppelia_dir}"
        info "CoppeliaSim is already installed at ${COPPELIASIM_ROOT}"
        return
    fi

    if [ -d "${coppelia_dir}" ]; then
        warn "Deleting existing CoppeliaSim directory: ${coppelia_dir}"
        rm -rf "${coppelia_dir}"
    fi

    if [ -f "${coppelia_tar}" ] && tar -tf "${coppelia_tar}" &> /dev/null; then
        info "Using existing CoppeliaSim archive: ${coppelia_tar}"
    else
        info "Downloading CoppeliaSim ${coppelia_version} for ${os_version}"
        wget "${download_url}" --no-check-certificate
        if ! tar -tf "${coppelia_tar}" &> /dev/null; then
            error "File download and/or extraction failed. Please check the downloaded file and try again."
            return 1
        else
            tar -xf "${coppelia_tar}" -C ${SCRIPT_PARENT}
            rm -rf "${coppelia_tar}"
        fi
    fi
    
    export COPPELIASIM_ROOT="${coppelia_dir}"
    info "CoppeliaSim installed successfully at ${coppelia_dir}"  
}

function install_pyrep() {
    local pyrep_dir="${SCRIPT_PARENT}/PyRep"

    if [ -d "${pyrep_dir}" ] && [ -n "$(find "${pyrep_dir}" -maxdepth 0 -type d -empty)" ]; then
        warn "Deleting existing PyRep directory: ${pyrep_dir}"
        rm -rf "${pyrep_dir}"
    elif [ ! -d "${pyrep_dir}" ]; then
        info "Downloading PyRep to ${pyrep_dir}"
        git clone https://github.com/stepjam/PyRep "${pyrep_dir}"
    else
        info "PyRep is already downloaded"
    fi

    if ! python3 -c "import pyrep"; then
        info "Installing PyRep dependencies to ${pyrep_dir}" 
        pip install "${pyrep_dir}"
    else
        info "PyRep is already installed"
    fi
}

function install_rlbench() {
    local rlbench_dir="${SCRIPT_PARENT}/RLBench"

    if [ -d "${rlbench_dir}" ] && [ -n "$(find "${rlbench_dir}" -maxdepth 0 -type d -empty)" ]; then
        warn "Deleting existing RLBench directory: ${rlbench_dir}"
        rm -rf "${rlbench_dir}"
    elif [ ! -d "${rlbench_dir}" ]; then
        info "Downloading RLBench to ${rlbench_dir}"
        git clone https://github.com/stepjam/RLBench "${rlbench_dir}"
    else
        info "RLBench is already downloaded"
    fi

    if ! python3 -c "import rlbench"; then
        info "Installing RLBench dependencies to ${rlbench_dir}"
        pip install "${rlbench_dir}"
    else
        info "RLBench is already installed"
    fi
}

function install_libfranka() {
    local shell_init_file=
        case $SHELL in
            */bash) shell_init_file="${HOME}/.bashrc" ;;
            */zsh) shell_init_file="${HOME}/.zshrc" ;;
            *) shell_init_file="${HOME}/.profile" ;;
        esac

    local libfranka_dir="${SCRIPT_PARENT}/libfranka"
    if [ -d "${libfranka_dir}" ] && [ -n "$(find "${libfranka_dir}" -maxdepth 0 -type d -empty)" ]; then
        warn "Deleting existing libfranka directory: ${libfranka_dir}"
        rm -rf "${libfranka_dir}"
    elif [ ! -d "${libfranka_dir}" ]; then
        info "Downloading libfranka to ${libfranka_dir}"
        git clone --recursive https://github.com/frankaemika/libfranka "${libfranka_dir}"
    else
        info "libfranka is already downloaded"
    fi

    if ! command -v cmake make >/dev/null 2>&1; then
        error "Please install cmake and make before running this script."
        return 1
    fi

    info "Building libfranka from source in ${libfranka_dir}"
    git config --global --add safe.directory /home/dev_user/libfranka
    git config --global --add safe.directory /home/dev_user/libfranka/common
    sudo apt update
    sudo apt install -y ${LIBRARY_DEPENDENCIES}

    cd "${libfranka_dir}"
    git checkout 0.9.0
    git submodule update

    if [[ ! "$LD_LIBRARY_PATH" =~ "${libfranka_dir}/build" ]]; then
        info "Adding libfranka to LD_LIBRARY_PATH in $shell_init_file"
        sed -i '/^export '"LD_LIBRARY_PATH"'/d' "$shell_init_file"
        echo "export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${libfranka_dir}/build" >> "$shell_init_file"
        export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${libfranka_dir}/build
    else
        info "${libfranka_dir}/build is already in LD_LIBRARY_PATH"
    fi

    mkdir -p build
    cd build
    cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=OFF ..
    cmake --build .
    info "libfranka installed successfully"
}


function install_franka_ros() {
    local shell_init_file=
        case $SHELL in
            */bash) shell_init_file="${HOME}/.bashrc" ;;
            */zsh) shell_init_file="${HOME}/.zshrc" ;;
            *) shell_init_file="${HOME}/.profile" ;;
        esac

    local franka_ros_dir="${SCRIPT_PARENT}/robotic_nerve_us/catkin_ws/src/franka_ros"

    info "source catkin_ws"
    cd catkin_ws
    source /opt/ros/noetic/setup.bash

    if [ -d "${franka_ros_dir}" ] && [ -n "$(find "${franka_ros_dir}" -maxdepth 0 -type d -empty)" ]; then
        warn "Deleting existing franka_ros directory: ${franka_ros_dir}"
        rm -rf "${franka_ros_dir}"
    elif [ ! -d "${franka_ros_dir}" ]; then
        info "Downloading franka_ros to ${franka_ros_dir}"
        git clone --recursive https://github.com/frankaemika/franka_ros "${franka_ros_dir}"
    else
        info "franka_ros is already downloaded"
    fi
    
    info "Build franka_ros"
    rosdep install --from-paths src --ignore-src --rosdistro noetic -y --skip-keys libfranka
    catkin build --cmake-args -DCMAKE_BUILD_TYPE=Release -DFranka_DIR:PATH=/"${SCRIPT_PARENT}/libfranka/build/"
    source devel/setup.sh
}

function install_moveit() {
    local shell_init_file=
        case $SHELL in
            */bash) shell_init_file="${HOME}/.bashrc" ;;
            */zsh) shell_init_file="${HOME}/.zshrc" ;;
            *) shell_init_file="${HOME}/.profile" ;;
        esac

    local moveit_dir="${SCRIPT_PARENT}/robotic_nerve_us/catkin_ws/src/moveit"

    info "source catkin_ws"
    cd catkin_ws
    source /opt/ros/noetic/setup.bash

    if [ -d "${moveit_dir}" ] && [ -n "$(find "${moveit_dir}" -maxdepth 0 -type d -empty)" ]; then
        warn "Deleting existing moveit directory: ${moveit_dir}"
        rm -rf "${moveit_dir}"
    elif [ ! -d "${moveit_dir}" ]; then
        info "Downloading moveit to ${moveit_dir}"
        wstool init src
        wstool merge -t src https://raw.githubusercontent.com/ros-planning/moveit/master/moveit.rosinstall
        wstool update -t src
    else
        info "moveit is already downloaded"
    fi
    
    info "Build moveit"
    rosdep install -y --from-paths src --ignore-src --rosdistro ${ROS_DISTRO}
    catkin config --extend /opt/ros/${ROS_DISTRO} --cmake-args -DCMAKE_BUILD_TYPE=Release
    catkin build
}

function install_catch2() {
    local catch2_dir="${SCRIPT_PARENT}/Catch2"

    if [ -d "${catch2_dir}" ] && [ -n "$(find "${catch2_dir}" -maxdepth 0 -type d -empty)" ]; then
        warn "Deleting existing Catch2 directory: ${catch2_dir}"
        rm -rf "${catch2_dir}"
    elif [ ! -d "${catch2_dir}" ]; then
        info "Downloading Catch2 to ${catch2_dir}"
        git clone https://github.com/catchorg/Catch2.git "${catch2_dir}"
    else
        info "Catch2 is already downloaded"
    fi

    if ! command -v cmake make >/dev/null 2>&1; then
        error "Please install cmake and make before running this script."
        return 1
    fi

    cd "${catch2_dir}"

    git checkout v2.5.0

    if [ ! -d "${catch2_dir}/build" ]; then
        mkdir "${catch2_dir}/build"
    fi

    cd build
    cmake -DCATCH_BUILD_TESTING=OFF -DCATCH_ENABLE_WERROR=OFF -DCATCH_INSTALL_DOCS=OFF -DCATCH_INSTALL_HELPERS=OFF ..
    make install
    info "Catch2 installed successfully"
}

function install_frankx() {
    install_catch2

    local shell_init_file=
        case $SHELL in
            */bash) shell_init_file="${HOME}/.bashrc" ;;
            */zsh) shell_init_file="${HOME}/.zshrc" ;;
            *) shell_init_file="${HOME}/.profile" ;;
        esac

    package_dir=$(pip show pybind11 | grep Location | cut -d " " -f2-)
    pybind_dir=${package_dir}/pybind11
    libfranka_dir="${SCRIPT_PARENT}/libfranka/build"

    export CMAKE_PREFIX_PATH=$pybind_dir:$libfranka_dir:$CMAKE_PREFIX_PATH

    if [[ ! "$CMAKE_PREFIX_PATH" =~ "${pybind_dir}" ]]; then
        info "Adding pybind11 to CMAKE_PREFIX_PATH in $shell_init_file"
        echo "export CMAKE_PREFIX_PATH=$CMAKE_PREFIX_PATH:$pybind_dir" >> "$shell_init_file"
    else
        info "${pybind_dir} is already in CMAKE_PREFIX_PATH"
    fi

    if [[ ! "$CMAKE_PREFIX_PATH" =~ "${libfranka_dir}" ]]; then
        info "Adding libfranka to CMAKE_PREFIX_PATH in $shell_init_file"
        echo "export CMAKE_PREFIX_PATH=$CMAKE_PREFIX_PATH:$libfranka_dir" >> "$shell_init_file"
    else
        info "${libfranka_dir} is already in CMAKE_PREFIX_PATH"
    fi
    
    local frankx_dir="${SCRIPT_PARENT}/frankx"
    if [ -d "${frankx_dir}" ] && [ -n "$(find "${frankx_dir}" -maxdepth 0 -type d -empty)" ]; then
        warn "Deleting existing frankx directory: ${frankx_dir}"
        rm -rf "${frankx_dir}"
    elif [ ! -d "${frankx_dir}" ]; then
        git clone --recurse-submodules git@github.com:pantor/frankx.git "${frankx_dir}"
    else
        info "frankx is already downloaded"
    fi

    mkdir -p "${frankx_dir}/build"
    cd "${frankx_dir}/build"
    cmake -DBUILD_TYPE=Release ..
    make
    make install

    if ! python3 -c "import frankx"; then
        info "Installing frankx dependencies to ${frankx_dir}"
        pip install "${frankx_dir}"
    else
        info "frankx is already installed"
    fi
}

function install_all() {
    echo "Installing libfranka..."
    install_libfranka
    echo "Installing franka_ros..."
    install_franka_ros
    echo "Installing moveit..."
    install_moveit
    echo "Installing CoppeliaSim..."
    install_coppelia
    echo "Installing PyRep..."
    install_pyrep
    echo "Installing RLbench..."
    install_rlbench
    echo "Installing Frankx..."
    install_frankx
}


if [ $# -eq 0 ]; then
    usage
    exit 1
fi

while [ $# -gt 0 ]; do
    case $1 in
        --coppelia) install_coppelia ;;
        --pyrep) install_pyrep ;;
        --rlbench) install_rlbench ;;
        --libfranka) install_libfranka ;;
        --frankx) install_frankx ;;
        --franka-ros) install_franka_ros ;;
        --moveit) install_moveit ;;
        --all) install_all ;;
        -h|--help) usage; exit 0 ;;
        *) error "Invalid option: $1"; usage; exit 1 ;;
    esac
    shift
done
