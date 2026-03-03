# 🚀 CLI-ANI v0.666

**CLI-ANI** es un potente cliente de streaming para terminal que te permite buscar y ver anime desde **AnimeFLV** sin necesidad de abrir un navegador, utilizando reproductores externos para una experiencia sin publicidad y de alto rendimiento.

---

## ✨ Características

* 🔍 **Búsqueda Integrada:** Encuentra cualquier anime disponible en el catálogo.
* 📺 **Streaming Externo:** Soporte para `mpv` con configuración de buffer optimizada.
* 📚 **Historial Inteligente:** Guarda tus últimos 10 animes buscados.
* ✅ **Control de Vistos:** Marca automáticamente los episodios que ya viste (se muestran en verde en la lista).
* 🛠️ **Multi-Servidor:** Soporte para extraer enlaces de *YourUpload, Okru, Mail.ru y Streamwish*.
* 🤖 **Scraping Avanzado:** Incluye soporte para `Playwright` en servidores con protección.

---

## 🛠️ Requisitos del Sistema

El programa utiliza herramientas externas para procesar y reproducir los videos. Asegúrate de tener:

### 1. Binarios del Sistema

* **Python 3.x**
* **mpv:** El reproductor de video principal.
* **yt-dlp:** Para procesar y descargar streams de video.
* **Node.js:** Necesario si deseas usar el scraper de Playwright.

### 2. Librerías de Python

```bash
pip install requests beautifulsoup4 yt-dlp

```

---

## 🚀 Instalación y Uso

1. **Clona el repositorio:**
```bash
git clone https://github.com/washaka81/CLI-ANI.git
cd CLI-ANI

```


2. **Ejecuta el programa:**
```bash
python cli_ani.py

```


*El programa verificará automáticamente si te falta alguna dependencia al iniciar.*

---

## 📖 Instrucciones por Plataforma

| Sistema | Comando de Instalación Sugerido |
| --- | --- |
| **Linux (Ubuntu/Debian)** | `sudo apt install mpv nodejs npm && pip install requests bs4 yt-dlp` |
| **Arch Linux** | `sudo pacman -S mpv nodejs npm && pip install requests bs4 yt-dlp` |
| **Android (Termux)** | `pkg install mpv nodejs python && pip install requests bs4 yt-dlp` |
| **Windows** | Instala Python, Node.js y descarga `mpv.exe` añadiéndolo al PATH. |

---

## ⚖️ Licencia y Aviso Legal

Este proyecto está bajo la licencia **GNU General Public License v3.0 (GPLv3)**.

> **⚠️ AVISO LEGAL:** Este software ha sido diseñado únicamente con **fines educativos**. El usuario es el único responsable del uso que haga de este programa. El autor no respalda ni se hace responsable del consumo de contenido protegido por derechos de autor.

---

## 🤝 Contribuir

Si tienes ideas para mejorar la extracción de enlaces o el manejo de la terminal, ¡los Pull Requests son bienvenidos!

**Desarrollado con ❤️ por Washaka (2026)**

---

### ¿Cómo subir este archivo a tu GitHub?

Como ya configuraste tu repositorio antes, solo haz esto en tu terminal de Linux:

1. Crea el archivo: `nano README.md` (pega el contenido de arriba y guarda con `Ctrl+O`, `Enter` y `Ctrl+X`).
2. Sube los cambios:
```bash
git add README.md
git commit -m "Añadido README profesional"
git push origin main

```
