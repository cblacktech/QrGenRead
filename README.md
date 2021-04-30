# QrGenRead

## Introduction

A multi-platform application that can create and read qr codes

## Prerequisites

### Programs / Libraries

- [Python](https://www.python.org)
  
- [Git](https://git-scm.com/)

- Pip packages listed in [requirements.txt](./requirements.txt)

## Installation & Running

### Linux

#### Installing

- Retrieve project from git repo
  - For default branch use this command
  
    ```bash
    git clone https://gitlab.com/cblacktech/qrgenread.git
    ```

  - For a specific branch add --branch and the name of the branch
  
    ```bash
    git clone --branch develop https://gitlab.com/cblacktech/qrgenread.git
    ```

- Navigate into the project
  
  ```bash
  cd ./grgenread
  ```

- Create and activate a virtual environment
  
  ```bash
  python -m venv venv
  source ./venv/bin/activate  
  ```

#### Running

- To run the program run this command
  
  ```bash
  python ./main.py
  ```

### Android

- WARING: Buildozer may download and build more the 2 GiB of data and tools to build the Android apk

- Follow instructions for the [Linux installation](#linux)

- To build an Android apk
  
  ```bash
  buildozer android debug
  ```

- To build the Android apk and install it on a device that is connected
  
  ```bash
  buildozer android debug deploy
  ```

- The .apk file will be located in the bin directory of the project

- To see logs from an Android device that is plugged in
  
  ```bash
  adb logcat | grep python
  ```

## Notes

- Project does not need to be compiled to run on Linux, it does need to be compiled using buildozer to run on Android

- Currently, Video QR Scanner is not avaliable

- Android apk build is very unstable

- Currently, the ci/cd android build pipeline is not building the apk correctly.
