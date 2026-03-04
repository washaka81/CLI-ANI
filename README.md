🚀 CLI-ANI: Cliente de Streaming para ver Monos Chinos

  CLI-ANI es una potente herramienta de línea de comandos (CLI) escrita en Python para buscar y reproducir anime
  directamente desde AnimeFLV. Está diseñada para ser ligera, multiplataforma y altamente eficiente, con soporte
  especial para Android (Termux).


  ✨ Características Principales


   * 🔍 Búsqueda Inteligente: Encuentra tus series favoritas rápidamente a través de la terminal.
   * 📱 Soporte Nativo para Android: Optimizado para funcionar en Termux, permitiendo abrir videos directamente en la
     app de mpv-android.
   * 📊 Sistema de Ranking de Servidores: Aprende qué servidores funcionan mejor y los prioriza automáticamente para
     evitar enlaces caídos.
   * 📚 Historial y Seguimiento:
       * Guarda los últimos 10 animes buscados.
       * Marca visualmente (en verde) los episodios ya vistos.
   * ⚡ Optimización de Red: Detecta la latencia de tu conexión y ajusta automáticamente el buffer de mpv para una
     reproducción sin cortes.
   * 🔓 Desofuscación Avanzada: Soporte para múltiples servidores (YourUpload, Okru, Mail.ru, Streamwish, Streamtape,
     Netu/HQQ, Mega, y más) mediante técnicas de scraping dinámico.
   * 🛠️ Verificación de Dependencias: Herramienta integrada para diagnosticar si te falta algún componente necesario
     según tu sistema operativo.

  📋 Requisitos Proyectados



  ┌───────────────────────────┬──────────────────────────────────────────────────────────────────┐
  │ Componente                │ Uso                                                              │
  ├───────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ Python 3.x                │ Lenguaje base.                                                   │
  │ mpv                       │ Reproductor de video principal.                                  │
  │ yt-dlp                    │ Extracción de flujos de video.                                   │
  │ Node.js                   │ (Opcional) Para scraping avanzado de servidores como Streamwish. │
  │ Requests / BeautifulSoup4 │ Manejo de red y parseo de HTML.                                  │
  └───────────────────────────┴──────────────────────────────────────────────────────────────────┘

  🚀 Instalación Rápida

  En Linux (Debian/Ubuntu)


   1 sudo apt update && sudo apt install mpv nodejs
   2 pip install requests beautifulsoup4 yt-dlp

  En Android (Termux)


   1 pkg update && pkg upgrade
   2 pkg install mpv nodejs curl jq
   3 pip install yt-dlp requests beautifulsoup4
   4 termux-setup-storage

  🎮 Modo de Uso

  Simplemente ejecuta el script y sigue las instrucciones en pantalla:

   1 python cli_ani.py


   1. Buscar: Escribe el nombre del anime.
   2. Seleccionar: Elige el resultado correcto de la lista.
   3. Episodio: Introduce el número del episodio (o presiona Enter para el último disponible).
   4. Disfrutar: El script intentará automáticamente el mejor servidor disponible.

  ⚖️ Licencia y Aviso Legal


  Este proyecto se distribuye bajo la licencia GNU GPLv3.

  AVISO: Este software ha sido creado con fines educativos. El autor no se hace responsable del uso que los usuarios den
  a la herramienta ni del contenido visualizado. Respeta los derechos de autor y apoya a la industria del anime siempre
  que sea posible.

  ---

  ❤️ Créditos


  Desarrollado con mucho amor por Washaka (2026).

  Si este proyecto te ha servido, ¡no olvides dejar una ⭐ en el repositorio!

  ---


  Hecho por y para la comunidad. Disfruta de tus series favoritas desde la comodidad de tu terminal.
