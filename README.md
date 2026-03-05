

  🌸 CLI-ANI: Edición De-Obfuscator v0.719

CLI-ANI es un cliente de terminal minimalista y potente desarrollado por Washaka (2026) con fines educativos. Permite buscar y reproducir anime sin anuncios, utilizando técnicas de desofuscación dinámica para extraer enlaces directos de diversos servidores.
🚀 Guía de Instalación

Este script está optimizado para PC (Linux/Windows) y especialmente para Android (Termux).
1. Requisitos Previos

Necesitarás tener instalados Python y dos herramientas esenciales:

    yt-dlp: Para el análisis de flujos de video.

    MPV: El motor de reproducción recomendado.

2. Instalación en Termux (Android)

Copia y pega este comando para preparar tu entorno:
Bash

pkg update && pkg upgrade
pkg install python mpv yt-dlp ffmpeg
pip install requests beautifulsoup4

3. Instalación en PC (Linux/Windows)

    Asegúrate de tener mpv y yt-dlp en tu PATH.

    Instala las librerías de Python:
    Bash

    pip install requests beautifulsoup4

🛠️ Cómo usarlo

Solo tienes que ejecutar el script y seguir las instrucciones en pantalla:
Bash

python cli_ani.py

💎 Características Destacadas

    Desofuscador P.A.C.K.E.R. Integrado: El script incluye una función js_unpack que traduce código JavaScript "enredado" en enlaces de video reales (.m3u8 o .mp4).

    Algoritmo de Tasa de Éxito: No pierdas tiempo con servidores caídos. El sistema registra cada intento exitoso o fallido y genera un ranking en tiempo real para ofrecerte siempre la mejor fuente disponible.

    Memoria Inteligente (JSON): Guarda tu historial de búsqueda y marca los episodios vistos con un sistema visual de puntos (● visto / ○ pendiente).

    Fuerza Bruta en Android: Capacidad única para lanzar reproductores externos (MPV Oficial o Forks) mediante Intents de sistema, asegurando que el video se abra incluso en entornos restringidos.

    Interfaz Dinámica: Incluye temporizadores de respuesta con colores y una barra de progreso honesta alimentada por los metadatos de yt-dlp.

📝 Nota Educativa

Este proyecto fue desarrollado por Washaka para demostrar el potencial de Python en la automatización de tareas y la interacción con la web moderna. Úsalo con respeto y curiosidad científica.
