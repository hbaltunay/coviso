<p align="center"> <img src=".github/assets/banner.png" width="350" /> </p>

# COVISO
Computer Vision Solutions

It is a library that includes algorithmic solutions to be used together with models developed for computer vision. It also includes structured methods used in the model training processes.

⚠️ It is under development.

## 📦 Install

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

## 📜 License

This library is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

* **EN:** Contributions are always welcome; feel free to open an issue to support the development with your ideas.
* **TR:** Katkılarınız her zaman memnuniyetle karşılanır; fikirlerinizle geliştirmeye destek olmak için issue açabilirsiniz.