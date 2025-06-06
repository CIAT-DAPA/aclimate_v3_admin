# AClimate V3 Admin

## 🏷️ Versión y Tags

**Versión actual:** `v3.0.0`  
**Tags:** `aclimate`, `clima`, `agricultura`, `python`

---

## 📌 Introducción

AClimate Admin es un sistema que permite a los usuarios gestionar diversos parámetros de AClimate, una plataforma que ofrece información precisa sobre pronósticos estacionales y subestacionales. A través de una interfaz amigable e intuitiva, AClimate Admin facilita la administración de elementos como los países utilizados en AClimate, la parametrización de simulaciones de cultivos, los roles de usuario, entre otros.

---

## ✅ Prerrequisitos

Antes de comenzar, asegúrate de tener instaladas las siguientes herramientas:

- Python 3.10
- [virtualenv](https://virtualenv.pypa.io/)
- Git

---

## ⚙️ Instalación

Clona el repositorio:

```bash
git clone https://github.com/CIAT-DAPA/aclimate_v3_admin
cd aclimate_v3_admin
```

Crear un entorno virtual e instalar los requerimientos:

```bash
py -m venv env
env\Scripts\activate
pip install -r requirements.txt 
```

Correr app de flask:

```bash
cd src
py run.py
```