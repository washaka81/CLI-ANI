# 🌸 CLI-ANI

> Un cliente de terminal minimalista para ver anime sin anuncios, ahora en español

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/Licencia-GPL--3.0-green.svg)](LICENSE)

## ✨ ¿Qué es CLI-ANI?

CLI-ANI es una herramienta de terminal poderosa y fácil de usar que te permite **buscar y reproducir anime sin anuncios**. Está desarrollada en Python y utiliza técnicas de desofuscación dinámica para extraer enlaces directos de múltiples servidores de video.

¿Te gusta [ani-cli](https://github.com/pystardust/ani-cli)? ¡Esto es lo mismo pero completamente en español! 🎉

## 🚀 Características Principales

| Característica | Descripción |
|----------------|-------------|
| 🔓 **Desofuscador P.A.C.K.E.R.** | Traduce código JavaScript ofuscado en enlaces de video reales (.m3u8 o .mp4) |
| 📊 **Algoritmo de Éxito** | Aprende de los servidores caídos y siempre te ofrece la mejor opción disponible |
| 💾 **Memoria Inteligente** | Guarda tu historial y marca los episodios vistos con ● (visto) / ○ (pendiente) |
| 📱 **Fuerza Bruta en Android** | Lanza reproductores externos mediante Intents del sistema |
| 🎨 **Interfaz Dinámica** | Colores, temporizadores de respuesta y barra de progreso en tiempo real |

## 📋 Requisitos Previos

Antes de instalar, necesitas tener:

- **Python 3.x** - El lenguaje del script
- **yt-dlp** - Para análisis de flujos de video
- **mpv** - El reproductor de video recomendado
- **ffmpeg** - Para procesamiento de audio/video

## 🛠️ Instalación

### Termux (Android)

```bash
# Actualiza e instala las dependencias
pkg update && pkg upgrade
pkg install python mpv yt-dlp ffmpeg

# Instala las librerías de Python
pip install requests beautifulsoup4
```

### Linux / Windows (PC)

1. Asegúrate de tener `mpv` y `yt-dlp` instalados y en tu PATH
2. Instala las dependencias de Python:

```bashº
pip install requests beautifulsoup4
```

## ▶️ Cómo Usarlo

¡Es muy fácil! Solo ejecuta:

```bash
python cli_ani.py
```

Sigue las instrucciones en pantalla y disfruta de tu anime favorito. ¡Es così semplice! 🍝

## 📝 Estructura del Proyecto

```
CLI-ANI/
├── cli_ani.py      # El script principal
├── README.md       # Este archivo
└── LICENSE         # Licencia GPL-3.0
```

## ⚠️ Nota Educational

Este proyecto fue creado por **Washaka** (2026) con fines educativos. Su propósito es demostrar el poder de Python para automatizar tareas e interactuar con la web moderna.

> 💡 Úsalo con respeto y curiosidad científica. Aprende cómo funciona, experimenta y diviertete!

## 📄 Licencia

Este proyecto está bajo la licencia [GPL-3.0](LICENSE). Sientete libre de contribuir, modificar y compartir!

---

⭐ ¡Si te gusta el proyecto, no olvides dar una estrella!
