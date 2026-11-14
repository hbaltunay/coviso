# COVISO
Computer Vision Solutions

It is a library that includes algorithmic solutions to be used together with models developed for computer vision. It also includes structured methods used in the model training processes.

⚠️ It is under development.

## Install

### Python
```bash
git clone https://github.com/hbaltunay/coviso.git
cd coviso/python
pip install .
```

### C++

#### Shared Library

```bash
git clone https://github.com/hbaltunay/coviso.git
cd coviso
cmake -B build -DBUILD_SHARED_LIBS=ON
cmake --build build
sudo cmake --install build --prefix /opt/coviso
```

#### Static Library

```bash
git clone https://github.com/hbaltunay/coviso.git
cd coviso
cmake -B build -DBUILD_SHARED_LIBS=OFF
cmake --build build
sudo cmake --install build --prefix /opt/coviso
```