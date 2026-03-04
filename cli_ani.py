# -*- coding: utf-8 -*-
# =============================================================================
# CLI-ANI - Cliente de streaming para AnimeFLV
# =============================================================================
# Copyright (C) 2026 Washaka
# 
# Este programa es software libre: puede redistribuirlo y/o modificarlo
# bajo los términos de la Licencia Pública General GNU (GPLv3) publicada por
# la Free Software Foundation, ya sea la versión 3 de la Licencia, o
# (a su opción) cualquier versión posterior.
# 
# Este programa se distribuye con la esperanza de que sea útil,
# pero SIN NINGUNA GARANTÍA; incluso sin la garantía implícita de
# COMERCIABILIDAD o APTITUD PARA UN PROPÓSITO PARTICULAR.
# Vea la Licencia Pública General GNU para más detalles.
# 
# Debería haber recibido una copia de la Licencia Pública General GNU
# junto con este programa. Si no la ha recibido, consulte
# <https://www.gnu.org/licenses/>.
# =============================================================================
#
# AVISO LEGAL:
# Este software está diseñado únicamente con fines educativos.
# El usuario es responsable del uso que haga de este programa.
# El autor no respalda ni se hace responsable del uso que se le dé
# al contenido protegido por derechos de autor.
# =============================================================================

import requests
import re
import json
import subprocess
import string
import html
import sys
import os
from datetime import datetime
from bs4 import BeautifulSoup
import platform
import shutil

BASE_URL = "https://www3.animeflv.net"
SESSION = requests.Session()


def is_termux():
    """Detecta si está ejecutándose en Termux/Android"""
    return (
        os.environ.get('TERMUX_VERSION') is not None
        or os.path.exists('/data/data/com.termux')
        or 'com.termux' in os.environ.get('PREFIX', '')
    )


def check_android_players():
    """Verifica qué reproductores están disponibles en Android"""
    players = {
        'com.mpv.android': False,       # MPV Android
    }
    
    try:
        result = subprocess.run(
            ['pm', 'list', 'packages'],
            capture_output=True, text=True, timeout=5
        )
        packages = result.stdout
        for player in players:
            players[player] = player in packages
    except:
        pass
    
    return players


def play_android_mpv(url, referer=None):
    """Reproduce usando la app MPV Android (com.mpv.android) con am start"""
    try:
        # Construir URL con referer
        if referer:
            full_url = f"{url} --referrer={referer}"
        else:
            full_url = url
        
        # Método 1: Usar am start directamente (más efectivo)
        try:
            subprocess.run(
                ['am', 'start', '-n', 'com.mpv.android/com.mpv.ui.VideoPlayerActivity',
                 '--es', 'url', full_url],
                capture_output=True, timeout=10
            )
            return True
        except:
            pass
        
        # Método 2: Con scheme usando termux-open
        try:
            mpv_url = f"com.mpv.android://{full_url}"
            result = subprocess.run(
                ['termux-open', mpv_url],
                capture_output=True, text=True, timeout=15
            )
            return result.returncode == 0
        except:
            return False
    except:
        return False


def play_with_mpv(url, referer, cookie=None):
    """Reproduce video con mpv según la plataforma - Versión optimizada tipo ani-cli"""
    
    if is_termux():
        # Verificar players disponibles en Android
        android_players = check_android_players()
        
        # PRIORIDAD: MPV Android (com.mpv.android)
        if android_players.get('com.mpv.android', False):
            try:
                print("   📱 Abriendo con MPV Android...")
                if play_android_mpv(url, referer):
                    return True
            except:
                pass
        
        # Fallback: termux-open genérico
        try:
            print("   📱 Abriendo con reproductor disponible...")
            subprocess.run(['termux-open', url], capture_output=True, timeout=15)
            return True
        except:
            pass
        
        return False
        
        # 4. ÚLTIMO RECURSO: termux-open genérico
        try:
            print("   📱 Abriendo con reproductor disponible...")
            subprocess.run(['termux-open', url], capture_output=True, timeout=15)
            return True
        except:
            pass
        
        return False
    
    else:
        # Desktop: reproducción normal
        opts = [
            'mpv', url,
            '--referrer', referer,
            '--cache=yes',
            '--cache-secs=300',
            '--force-window=yes',
        ]
        
        if cookie:
            opts.append(f'--http-header-fields=Cookie: {cookie}')
        
        return subprocess.run(opts).returncode == 0


def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    missing = []
    system = platform.system()
    is_android = is_termux()
    
    # Python packages
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    try:
        import bs4
    except ImportError:
        missing.append("beautifulsoup4")
    
    # System binaries
    if not shutil.which("mpv"):
        missing.append("mpv")
    
    if not shutil.which("yt-dlp"):
        missing.append("yt-dlp")
    
    if not shutil.which("node"):
        missing.append("node")
    
    # Si hay faltantes, mostrar mensaje de error
    if missing:
        print("\n" + "="*60)
        print("❌ FALTAN DEPENDENCIAS")
        print("="*60)
        
        if is_android:
            print("\n📦 Instalación en TERMUX (Android):")
            print("-" * 40)
            print("  pkg update && pkg upgrade")
            print("  pkg install curl jq mpv nodejs")
            print("  pip install yt-dlp")
            print("  npm install playwright && npx playwright install chromium")
            print("")
            print("  # Para reproducir en Android:")
            print("  termux-setup-storage")
            
        elif system == "Linux":
            print("\n📦 Instalación en LINUX:")
            print("-" * 40)
            if "requests" in missing or "beautifulsoup4" in missing:
                print("  pip install requests beautifulsoup4")
            if "mpv" in missing:
                print("  # Debian/Ubuntu: sudo apt install mpv")
                print("  # Arch Linux: sudo pacman -S mpv")
            if "yt-dlp" in missing:
                print("  pip install yt-dlp")
            if "node" in missing:
                print("  # Debian/Ubuntu: sudo apt install nodejs npm")
                print("  npm install playwright && npx playwright install chromium")
        
        elif system == "Darwin":
            print("\n📦 Instalación en MACOS:")
            print("-" * 40)
            if "requests" in missing or "beautifulsoup4" in missing:
                print("  pip3 install requests beautifulsoup4")
            if "mpv" in missing:
                print("  brew install mpv")
            if "yt-dlp" in missing:
                print("  brew install yt-dlp")
            if "node" in missing:
                print("  brew install node")
                print("  npm install playwright && npx playwright install chromium")
        
        elif system == "Windows":
            print("\n📦 Instalación en WINDOWS:")
            print("-" * 40)
            if "requests" in missing or "beautifulsoup4" in missing:
                print("  pip install requests beautifulsoup4")
            if "mpv" in missing:
                print("  Descargar mpv desde: https://mpv.io/installation/")
            if "yt-dlp" in missing:
                print("  pip install yt-dlp")
            if "node" in missing:
                print("  Descargar Node.js desde: https://nodejs.org/")
                print("  npm install playwright && npx playwright install chromium")
        
        print("\n" + "="*60)
        return False
    
    # Mostrar plataforma detectada
    if is_android:
        print("\n📱 Detectado: Termux/Android")
    else:
        print(f"\n💻 Detectado: {system}")
    
    return True


def get_network_speed():
    """Detecta la velocidad de red y retorna configuración de buffer recomendada"""
    try:
        import time
        test_url = "https://www.google.com/generate_204"
        start = time.time()
        SESSION.get(test_url, timeout=5)
        latency = (time.time() - start) * 1000  # ms
        
        # Estimar velocidad según latencia y tipo de conexión
        if is_termux():
            # En Termux, asumimos conexión móvil
            if latency < 100:
                # 4G/LTE bueno
                return {
                    "cache_secs": 600,      # 10 min cache
                    "stream_buffer": "32MiB",
                    "demuxer_bytes": "150MiB",
                    "reconnect": True,
                    "priority": "alto"
                }
            else:
                # 3G o conexión lenta
                return {
                    "cache_secs": 1200,     # 20 min cache
                    "stream_buffer": "64MiB",
                    "demuxer_bytes": "300MiB",
                    "reconnect": True,
                    "priority": "bajo"
                }
        else:
            # Desktop
            if latency < 50:
                # Fibra/GB excelente
                return {
                    "cache_secs": 300,      # 5 min
                    "stream_buffer": "16MiB",
                    "demuxer_bytes": "100MiB",
                    "reconnect": False,
                    "priority": "excelente"
                }
            elif latency < 100:
                # Cable/ADSL bueno
                return {
                    "cache_secs": 600,      # 10 min
                    "stream_buffer": "32MiB",
                    "demuxer_bytes": "200MiB",
                    "reconnect": True,
                    "priority": "alto"
                }
            else:
                # Conexión lenta
                return {
                    "cache_secs": 1200,     # 20 min
                    "stream_buffer": "64MiB",
                    "demuxer_bytes": "400MiB",
                    "reconnect": True,
                    "priority": "bajo"
                }
    except:
        #默认值 si falla la detección
        if is_termux():
            return {
                "cache_secs": 600,
                "stream_buffer": "32MiB",
                "demuxer_bytes": "150MiB",
                "reconnect": True,
                "priority": "medio"
            }
        else:
            return {
                "cache_secs": 300,
                "stream_buffer": "16MiB",
                "demuxer_bytes": "100MiB",
                "reconnect": False,
                "priority": "medio"
            }


SESSION = requests.Session()
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
SESSION.headers.update({'User-Agent': USER_AGENT, 'Referer': 'https://www3.animeflv.net/'})

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'history.json')

HISTORY = {"animes": [], "vistos": {}}

def load_history():
    global HISTORY
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                HISTORY = json.load(f)
    except:
        pass

def save_history():
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(HISTORY, f)
    except:
        pass

def add_to_history(title, url, slug):
    global HISTORY
    # Remover si ya existe
    HISTORY["animes"] = [a for a in HISTORY["animes"] if a['slug'] != slug]
    # Agregar al inicio
    HISTORY["animes"].insert(0, {
        "title": title,
        "url": url,
        "slug": slug,
        "timestamp": datetime.now().isoformat()
    })
    # Mantener solo 10
    HISTORY["animes"] = HISTORY["animes"][:10]
    save_history()

def mark_episode_viewed(slug, episode):
    # Convertir a string para consistencia
    episode_str = str(episode)
    if slug not in HISTORY["vistos"]:
        HISTORY["vistos"][slug] = []
    if episode_str not in HISTORY["vistos"][slug]:
        HISTORY["vistos"][slug].append(episode_str)
        save_history()

def is_episode_viewed(slug, episode):
    # Convertir a string para comparar correctamente
    episode_str = str(episode)
    return episode_str in HISTORY.get("vistos", {}).get(slug, [])

def print_history():
    if not HISTORY["animes"]:
        return []
    print("\n📚 Historial (últimos 10):")
    for i, a in enumerate(HISTORY["animes"]):
        print(f"  {i+1}. {a['title']}")
    return HISTORY["animes"]


def try_playwright_streamwish(embed_url, referer="https://www3.animeflv.net/"):
    try:
        import subprocess
        import json
        result = subprocess.run(
            ['node', 'streamwish_scraper.js', embed_url, referer],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            data = json.loads(result.stdout.strip())
            return data.get('url')
    except Exception as e:
        print(f"   ⚠️ Playwright error: {e}")
    return None


def int2base(x, base):
    chars = string.digits + string.ascii_letters
    if x < base:
        return chars[x]
    return int2base(x // base, base) + chars[x % base]


def get_best_link(server):
    """Extrae la URL directa del servidor con técnicas avanzadas de desofuscación"""
    s_name = server['n']
    s_url = server['u']
    
    print(f"   🔍 Extrayendo de [{s_name}]...")
    
    try:
        # === YourUpload (optimizado según JSON + código fuente) ===
        if "yourupload" in s_url.lower():
            try:
                # Headers como en el código fuente
                headers = {
                    'Referer': 'https://www3.animeflv.net/',
                    'User-Agent': USER_AGENT
                }
                
                # Si es URL de download, convertir a embed
                if "download" in s_url.lower():
                    s_url = s_url.replace("download?file=", "embed/")
                
                res = SESSION.get(s_url, timeout=8, headers=headers).text
                
                # Verificar si el archivo fue borrado
                if "File was deleted" in res or "File not found" in res:
                    print("   ⚠️ YourUpload: Archivo borrado")
                    return None, None
                
                # Buscar og:video (método principal del código fuente)
                url = re.search(r'<meta property="og:video" content="([^"]+)"', res)
                if not url:
                    # Buscar file: '...' (del código fuente)
                    url = re.search(r"file:\s*'([^']+)'", res)
                if not url:
                    # Buscar file: "..." 
                    url = re.search(r'file:\s*"([^"]+)"', res)
                if not url:
                    # Buscar src en video
                    url = re.search(r'src:\s*"([^"]+\.mp4[^"]*)"', res)
                
                if url:
                    video_url = url.group(1)
                    
                    # Si es vidcache, no necesita dominio
                    if "vidcache" not in video_url:
                        video_url = f"https://www.yourupload.com{video_url}"
                    
                    # Devolver con Referer
                    return video_url, None
                    
            except Exception as e:
                print(f"   ⚠️ YourUpload error: {e}")
        
        # === Okru (Odnoklassniki) - Optimizado según JSON + código fuente ===
        elif "okru" in s_url.lower() or "ok.ru" in s_url.lower():
            try:
                headers = {
                    'User-Agent': USER_AGENT,
                    'Referer': 'https://www3.animeflv.net/',
                    'Accept': '*/*',
                }
                
                # Normalizar URL según JSON
                url = s_url
                
                # Convertir diferentes formatos de URL okru
                # ok.ru/videoembed/xxx -> https://ok.ru/videoembed/xxx
                # www.ok.ru/videoembed/xxx -> https://ok.ru/videoembed/xxx
                if "ok.ru" not in url and "okru" in url.lower():
                    url = url.replace("okru", "ok.ru")
                
                # Patrones de URL según JSON
                url_patterns = [
                    (r'ok\.ru/videoembed/(\d+)', r'https://ok.ru/videoembed/\1'),
                    (r'okru\.link/v2/embed_vf_s\.html\?t=([a-zA-Z0-9_.]+)', r'https://okru.link/v2/embed_vf_s.html?t=\1'),
                    (r'okru\.link/embed\.html\.t=(\w+)', r'https://okru.link/embed.html?t=\1'),
                ]
                
                for pattern, replacement in url_patterns:
                    url = re.sub(pattern, replacement, url)
                
                # Headers como en código fuente
                kwargs = {
                    'set_tls': True,
                    'set_tls_min': True,
                    'timeout': 8,
                }
                
                res = SESSION.get(url, timeout=10, headers=headers)
                
                # Verificar restricciones de copyright (código fuente)
                if "copyrightsRestricted" in res.text or "COPYRIGHTS_RESTRICTED" in res.text or "LIMITED_ACCESS" in res.text:
                    print("   ⚠️ Okru: Video eliminado por copyright")
                    return None, None
                
                # Verificar si no existe (código fuente)
                if "notFound" in res.text or "u0026urls" not in res.text:
                    print("   ⚠️ Okru: Video no encontrado")
                    return None, None
                
                # Decodificar HTML entities
                data = html.unescape(res.text).replace('\\', '')
                
                # Extraer URLs de video (código fuente)
                video_urls = []
                for name, video_url in re.findall(r'\{"name":"([^"]+)","url":"([^"]+)"\}', data):
                    video_url = video_url.replace("%3B", ";").replace("u0026", "&")
                    # Ignorar mobile
                    if "mobile" not in name.lower():
                        video_urls.append((name, video_url))
                
                # Si encontramos videos, devolver el de mejor calidad
                if video_urls:
                    # Priorizar calidades mayores
                    video_urls.sort(key=lambda x: x[0], reverse=True)
                    return video_urls[0][1], None
                
                # Manejo especial para okru.link (código fuente)
                if "okru.link/v2" in url:
                    v = re.search(r't=([\w.]+)', url)
                    if v:
                        try:
                            post_data = {"video": v.group(1)}
                            api_res = SESSION.post(
                                "https://apizz.okru.link/decoding",
                                json=post_data,
                                headers={"Content-Type": "application/x-www-form-urlencoded", "Origin": url}
                            ).json()
                            if api_res.get("url"):
                                return api_res["url"], None
                        except:
                            pass
                
                # Manejo para okru.link/embed
                if "okru.link/embed" in url:
                    v = re.search(r't=(\w+)', url)
                    if v:
                        try:
                            api_res = SESSION.get(
                                f"https://okru.link/details.php?v={v.group(1)}",
                                timeout=8
                            ).json()
                            if api_res.get("file"):
                                return api_res["file"], None
                        except:
                            pass
                
            except Exception as e:
                print(f"   ⚠️ Okru error: {e}")
        
        # === Mail.ru (optimizado según JSON + código fuente) ===
        elif "mail.ru" in s_url.lower():
            try:
                headers = {
                    'User-Agent': USER_AGENT,
                    'Referer': 'https://www3.animeflv.net/'
                }
                
                # URLs válidas según JSON
                # http://videoapi.my.mail.ru/videos/embed/mail/inbox/xxx/_myvideo/xxx.html
                # http://my.mail.ru/+/video/meta/xxx
                
                vurl = s_url
                
                # Si es URL con /+/, usar directamente
                if "/+/" not in s_url:
                    # Obtener la página para procesar
                    res = SESSION.get(s_url, timeout=8, headers=headers)
                    
                    # Verificar si el video no existe (código fuente)
                    if res.status_code == 404 or '"error":"video_not_found"' in res.text or '"error":"Can\'t find VideoInstance"' in res.text:
                        print("   ⚠️ Mail.ru: Video no encontrado")
                        return None, None
                    
                    # Buscar metadataUrl
                    meta = re.search(r'"metadataUrl"\s*:\s*"([^"]+)"', res.text)
                    if meta:
                        m_url = meta.group(1)
                        if m_url.startswith('//'):
                            m_url = "https:" + m_url
                        vurl = m_url
                
                # Obtener datos JSON con la cookie video_key
                response = SESSION.get(vurl, timeout=8, headers=headers)
                datos = response.json()
                
                # Obtener cookie video_key (código fuente)
                cookie_header = response.headers.get('set-cookie', '')
                cookie_match = re.search(r'(video_key=[a-f0-9]+)', cookie_header)
                video_key = cookie_match.group(1) if cookie_match else SESSION.cookies.get('video_key')
                
                if datos.get('videos') and len(datos['videos']) > 0:
                    video_url = datos['videos'][0]['url']
                    
                    # Formar URL con cookie (como en código fuente)
                    if not video_url.startswith('http'):
                        video_url = "http:" + video_url
                    
                    # Cookie especial para Mail.ru
                    cookie = f"video_key={video_key}"
                    return video_url, cookie
                    
            except Exception as e:
                print(f"   ⚠️ Mail.ru error: {e}")
        
        # === Streamwish / SW (optimizado según JSON + código fuente Alfa) ===
        # Dominios: streamwish, embedwish, hlswish, wishfast, playerwish, sfastwish, 
        # wishembed, cdnwish, obeywish, flastwish, jodwish, swdyu, strwish, swhoi,
        # jwplayerhls, wishonly, cdnstream, cybervynx, swishsrv, swiftplayers, etc.
        elif any(d in s_url.lower() for d in ['streamwish', 'embedwish', 'hlswish', 'awish', 'dwish', 
                                                'streamwish.to', 'streamwish.com', 'wishfast', 'playerwish',
                                                'sfastwish', 'wishembed', 'cdnwish', 'obeywish', 'flastwish',
                                                'jodwish', 'swdyu', 'strwish', 'swhoi', 'jwplayerhls', 'wishonly',
                                                'cdnstream', 'cybervynx', 'swishsrv', 'swiftplayers', '74k',
                                                'ghbrisk', 'dhcplay', 'hgplaycdn', 'hgbazooka', 'dumbalag',
                                                'hglink', 'eliota', 'asnwish', 'haxloppd', 'wishonly.site',
                                                'iplayerhls.com', 'doodporn.xyz']):
            try:
                # Headers como en código fuente Alfa
                headers = {
                    'User-Agent': USER_AGENT,
                    'Referer': 'https://www3.animeflv.net/',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                }
                
                # Manejar |Referer= en la URL (como en código fuente)
                actual_url = s_url
                if "|Referer=" in s_url:
                    parts = s_url.split("|Referer=")
                    actual_url = parts[0]
                    headers['Referer'] = parts[1] if len(parts) > 1 else headers['Referer']
                
                res = SESSION.get(actual_url, timeout=10, headers=headers)
                
                # Verificar si el video no existe o está restringido (código fuente)
                if res.status_code == 404 or "no longer available" in res.text or "Not Found" in res.text:
                    print("   ⚠️ Streamwish: Video no disponible")
                    return None, None
                if "restricted for this domain" in res.text:
                    print("   ⚠️ Streamwish: Restringido en tu país")
                    return None, None
                
                # Intentar desofuscación packer (versión Alfa)
                try:
                    pack = re.search(r'p,a,c,k,e,d.*?</script>', res.text, re.DOTALL)
                    if pack:
                        # Usar método manual similar a jsunpack
                        pack_text = pack.group()
                        pack_match = re.search(r"}\('(.*?)',(\d+),(\d+),'(.*?)'\.split", pack_text)
                        if pack_match:
                            p, a, c, k = pack_match.groups()
                            a, c = int(a), int(c)
                            k = k.split('|')
                            d = {}
                            for i in range(c):
                                key = int2base(i, a)
                                value = k[i] if (i < len(k) and k[i]) else int2base(i, a)
                                d[key] = value
                            unpacked = re.sub(r'\b(\w+)\b', lambda m: d.get(m.group(1), m.group(1)), p)
                            
                            # Buscar m3u8 (prioridad: hls2 para evitar hls4)
                            m3u8 = re.search(r'(?:file|"hls2"):"([^"]+\.m3u8[^"]*)"', unpacked)
                            if not m3u8:
                                m3u8 = re.search(r'(?:file|hls):"([^"]+\.m3u8[^"]*)"', unpacked)
                            if m3u8:
                                return m3u8.group(1), None
                except:
                    pass
                
                # Intentar desofuscación packer manual (versión anterior)
                pack_match = re.search(r"eval\(function\(p,a,c,k,e,d\).*?}\('(.*?)',(\d+),(\d+),'(.*?)'\.split", res.text, re.DOTALL)
                if pack_match:
                    p, a, c, k = pack_match.groups()
                    a, c, k = int(a), int(c), k.split('|')
                    d = {int2base(i, a): k[i] if (i < len(k) and k[i]) else int2base(i, a) for i in range(c)}
                    unpacked = re.sub(r'\b(\w+)\b', lambda m: d.get(m.group(1), m.group(1)), p)
                    m3u8 = re.search(r'(?:file|"hls2"|hls):"([^"]+\.m3u8[^"]*)"', unpacked.replace('\\', ''))
                    if m3u8:
                        return m3u8.group(1), None
                
                # Buscar subtítulos VTT
                subtitles = re.findall(r'file:"([^"]+\.vtt[^"]*)",label:"([^"]+)"', res.text)
                
                # Buscar m3u8 directamente en el HTML/JS
                m3u8_direct = re.search(r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)', res.text)
                if m3u8_direct:
                    return m3u8_direct.group(1), None
                
                # Verificar si es la versión nueva (con JavaScript)
                if 'main.js' in res.text or 'player' in res.text.lower():
                    print("   ⚠️ Streamwish JS detectado, intentando Playwright...")
                    result = try_playwright_streamwish(actual_url)
                    if result:
                        return result, None
                    
            except Exception as e:
                print(f"   ⚠️ Streamwish error: {e}")
        
        # === Streamtape / Stape - Optimizado según JSON + código fuente ===
        # Dominios: streamtape, streamtapeadblock, streamtapeadblockuser, strtape, tapepops
        elif any(d in s_url.lower() for d in ['streamtape', 'streamtapeadblock', 'streamtapeadblockuser', 
                                                'strtape', 'tapepops', 'stape']):
            try:
                # Normalizar URL según JSON
                url = s_url
                
                # Convertir diferentes formatos de URL según JSON
                # https://streamtape.com/e/xxx
                url_patterns = [
                    (r'streamtape(?:adblock|adblockuser)?\.cloud/(\w+)', r'https://streamtape.com/e/\1'),
                    (r'streamtape\.(\w{2,4})/(v|e)/(\w+)', r'https://streamtape.com/e/\3'),
                    (r'strtape\.(\w{2,4})/(\w+)', r'https://streamtape.com/e/\2'),
                    (r'tapepops\.(\w{2,4})/(\w+)', r'https://streamtape.com/e/\2'),
                ]
                
                for pattern, replacement in url_patterns:
                    url = re.sub(pattern, replacement, url)
                
                headers = {
                    'User-Agent': USER_AGENT,
                    'Referer': 'https://www3.animeflv.net/',
                }
                
                res = SESSION.get(url, timeout=10, headers=headers)
                
                # Verificar si video no existe (código fuente)
                if "Video not found" in res.text:
                    print("   ⚠️ Streamtape: Video no encontrado")
                    return None, None
                
                # Verificar si está en conversión (código fuente)
                if "Video is converting" in res.text:
                    print("   ⚠️ Streamtape: Video en conversión, intenta más tarde")
                    return None, None
                
                # Método del código fuente: buscar innerHTML y evaluar con js2py
                find_url_matches = re.findall(r'innerHTML = ([^;]+)', res.text)
                
                if find_url_matches:
                    # Último match suele ser el correcto
                    find_url = find_url_matches[-1]
                    
                    # Intentar evaluar el JavaScript
                    try:
                        # Simular la evaluación de js2py
                        # El código usa: possible_url = js2py.eval_js(find_url)
                        
                        # Buscar patrones comunes en el HTML
                        js_patterns = [
                            r"innerHTML\s*=\s*[\"'](.+?)[\"']",
                            r"src\s*=\s*[\"'](.+?)[\"']",
                            r"videojs\([^)]+\)\.src\({[\"']src[\"']:\s*[\"'](.+?)[\"']",
                        ]
                        
                        for js_pattern in js_patterns:
                            js_match = re.search(js_pattern, res.text)
                            if js_match:
                                possible_url = js_match.group(1)
                                
                                # Si es una expresión JS, simplificarla
                                if ' + ' in possible_url or "'" in possible_url:
                                    # Buscar las variables
                                    var_match = re.findall(r'var\s+(\w+)\s*=\s*["\']([^"\']+)["\']', res.text)
                                    vars_dict = dict(var_match)
                                    
                                    # Reemplazar variables en la expresión
                                    for var_name, var_value in vars_dict.items():
                                        possible_url = possible_url.replace(var_name, var_value)
                                    
                                    # Limpiar comillas extras
                                    possible_url = possible_url.strip("'\" +")
                                
                                if possible_url.startswith('//'):
                                    possible_url = 'https:' + possible_url
                                elif possible_url.startswith('/'):
                                    possible_url = 'https://streamtape.com' + possible_url
                                elif not possible_url.startswith('http'):
                                    possible_url = 'https:' + possible_url
                                
                                # Obtener la URL final con redirect
                                try:
                                    final_res = SESSION.get(possible_url, headers=headers, allow_redirects=False)
                                    if final_res.headers.get('location'):
                                        return final_res.headers['location'], None
                                    return possible_url, None
                                except:
                                    return possible_url, None
                    except Exception as e:
                        pass
                
                # Fallback: buscar directamente en el HTML
                patterns = [
                    r"document\.getElementById\(['\"]videojs[^'\"]+['\"]\)\.src\s*=\s*['\"]([^'\"]+)['\"]",
                    r"videojs\([^)]+\)\.src\s*\(\s*\{[\"']src[\"']:\s*[\"']([^\"']+)[\"']",
                    r"src:\s*['\"]([^'\"]+\.(?:mp4|m3u8)[^'\"]*)['\"]",
                    r'file:\s*"([^"]+\.m3u8[^"]*)"',
                    r"src\s*=\s*['\"]([^'\"]+streamtape[^'\"]+)['\"]",
                ]
                
                for pattern in patterns:
                    m = re.search(pattern, res.text)
                    if m:
                        video_url = m.group(1)
                        if video_url.startswith('//'):
                            video_url = 'https:' + video_url
                        return video_url, None
                
                # Fallback: intentar con Playwright
                result = try_playwright_streamwish(url)
                if result:
                    return result, None
                    
            except Exception as e:
                print(f"   ⚠️ Streamtape error: {e}")
        
        # === Netu / HQQ / Waaw / NetuTV - Optimizado según JSON + código fuente ===
        # Dominios: hqq, waaw, netu, waaw1, porntoday, richhioon, woffxxx, veev.to, etc.
        elif any(d in s_url.lower() for d in ['hqq.tv', 'hqq', 'netu', 'waaw', 'waaw1', 'waaw2', 
                                                 'porntoday', 'richhioon', 'woffxxx', 'veev.to',
                                                 'player.megaxserie', 'netutv', 'netu.tv']):
            try:
                # Normalizar URL según JSON
                url = s_url
                
                # Convertir diferentes formatos de URL
                url = url.replace("/watch_video.php?v=", "/player/embed_player.php?vid=")
                url = url.replace("https://netu.tv/", "https://hqq.to/")
                url = url.replace("https://waaw.tv/", "https://hqq.to/")
                url = url.replace("http://netu.tv/", "http://hqq.watch/")
                url = url.replace("http://waaw.tv/", "http://hqq.watch/")
                
                # Headers como en código fuente
                headers = {
                    'User-Agent': USER_AGENT,
                    'Referer': 'https://www3.animeflv.net/',
                }
                
                # Verificar si hay hash
                if "hash=" in url:
                    data = SESSION.get(url, timeout=10).text
                    import urllib.parse
                    data = urllib.parse.unquote(data)
                    video_id = re.search(r"vid':'([^']+)'", data)
                    if video_id:
                        url = f"https://hqq.to/player/embed_player.php?vid={video_id.group(1)}"
                
                res = SESSION.get(url, timeout=10, headers=headers)
                
                # Verificar si el archivo no existe
                if "var userid = '';" in res.text.lower():
                    print("   ⚠️ Netu: Video no existe o fue borrado")
                    return None, None
                
                # Intentar desofuscar JavaScript (jswise del código fuente)
                js_wise_match = re.search(r"<script type=[\"']text/javascript[\"']>\s*;?(eval.*?)</script>", res.text, re.DOTALL)
                
                if js_wise_match:
                    # Aquí iría la función jswise pero es compleja
                    # Intentamos con la API directamente
                    pass
                
                # Intentar con la API de hqq (código fuente)
                video_id = re.search(r'embed_player\.php\?vid=([a-zA-Z0-9]+)', url)
                if video_id:
                    # Obtener IP primero (como en código fuente)
                    import random
                    alea = str(random.random())[2:]
                    
                    ip_url = f"https://hqq.to/player/ip.php?type=json&rand={alea}"
                    try:
                        ip_res = SESSION.get(ip_url, timeout=5, headers=headers).json()
                        ip_addr = ip_res.get("ip", "")
                        
                        # Buscar la URL de redirección
                        redirect_match = re.search(r'self\.location\.replace\("([^)]+)\)"', res.text)
                        if redirect_match:
                            redirect_url = redirect_match.group(1)
                            redirect_url = redirect_url.replace('"+rand+"', alea)
                            redirect_url = redirect_url.replace('"+data.ip+"', ip_addr)
                            redirect_url = redirect_url.replace('"+need_captcha+"', "0")
                            redirect_url = redirect_url.replace('"+token', "")
                            
                            # Obtener el JavaScript final
                            final_url = "https://hqq.to" + redirect_url
                            final_res = SESSION.get(final_url, timeout=10, headers=headers)
                            
                            # Extraer link del JSON final
                            codigo_js = re.findall(r'document\.write\(unescape\("([^"]+)', final_res.text)
                            
                            if codigo_js:
                                import urllib.parse
                                js_aux = urllib.parse.unquote(codigo_js[0])
                                at = re.search(r'var at = "([^"]+)"', js_aux)
                                
                                if at:
                                    # Obtener variables
                                    var_match = re.findall(r'var ([a-zA-Z0-9]+) = "([^"]+)";', final_res.text)
                                    vars_dict = dict(var_match)
                                    
                                    link_1 = vars_dict.get('link_1', '')
                                    server_2 = vars_dict.get('server_2', '')
                                    vid = vars_dict.get('vid', '')
                                    
                                    if link_1 and vid:
                                        # Construir URL final del video
                                        m3u8_url = f"https://hqq.to/player/get_md5.php?ver=2&at={at.group(1)}&adb=0&b=1&link_1={link_1}&server_2={server_2}&vid={vid}&ext=.mp4.m3u8"
                                        return m3u8_url, None
                    except Exception as e:
                        pass
                
                # Fallback: buscar directamente en el HTML
                patterns = [
                    r'src:\s*"([^"]+\.mp4[^"]*)"',
                    r'file:\s*"([^"]+\.m3u8[^"]*)"',
                    r'source\s+src="([^"]+)"',
                    r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)',
                ]
                for pattern in patterns:
                    m = re.search(pattern, res.text)
                    if m:
                        return m.group(1), None
                
                # Último intento: API simple
                if video_id:
                    api_url = f"https://hqq.tv/player/get_sources/{video_id.group(1)}"
                    try:
                        api_res = SESSION.get(api_url, timeout=10, headers=headers).json()
                        if api_res.get('result') == 'ok':
                            sources = api_res.get('sources', [])
                            if sources:
                                return sources[0].get('file'), None
                    except:
                        pass
                        
            except Exception as e:
                print(f"   ⚠️ Netu/HQQ error: {e}")
        
        # === Mega (optimizado según JSON + código fuente) ===
        elif "mega" in s_url.lower():
            try:
                # Normalizar URL según JSON
                url = s_url
                
                # Convertir diferentes formatos de URL MEGA
                url_patterns = [
                    (r'mega\.nz/file/([^\#]+)\#([A-Za-z0-9-_]+)', r'https://mega.nz/#!\1!\!\2'),
                    (r'mega\.nz/embed/([A-Za-z0-9\-_]+)\#([A-Za-z0-9\-_]+)', r'https://mega.nz/#!\1!!!!\2'),
                    (r'mega\.nz/embed/\#(\![A-z0-9-]+\![A-z0-9-]+)', r'https://mega.nz/\1'),
                    (r'mega\.nz/embed/([A-Za-z0-9-_!]+)', r'https://mega.nz/#\1'),
                    (r'mega\.nz/file/\#([A-Za-z0-9-_!]+)', r'https://mega.nz/#\1'),
                    (r'mega\.co\.nz/\#\!([A-Za-z0-9\-_]+)\!([A-Za-z0-9\-_]+)', r'https://mega.nz/#!\1!!!!\2'),
                    (r'mega\.co\.nz/\#F\!([A-Za-z0-9\-_]+)\!([A-Za-z0-9\-_]+)', r'https://mega.nz/#F!\1!!!!\2'),
                ]
                
                for pattern, replacement in url_patterns:
                    url = re.sub(pattern, replacement, url)
                
                # Asegurar que tenga el formato correcto
                if '/embed#' in url:
                    url = url.replace('/embed#', '/#')
                
                # MEGA funciona mejor con yt-dlp o megaserver
                # Intentar con yt-dlp primero
                print("   ⚠️ MEGA: usando yt-dlp...")
                return url, None
                
            except Exception as e:
                print(f"   ⚠️ MEGA error: {e}")
        
        # === Maru (similar estructura a Mail.ru) ===
        elif "maru" in s_url.lower():
            try:
                headers = {
                    'User-Agent': USER_AGENT,
                    'Referer': 'https://www3.animeflv.net/'
                }
                
                res = SESSION.get(s_url, timeout=10, headers=headers)
                
                # Verificar si video no existe
                if res.status_code == 404 or '"error"' in res.text:
                    print("   ⚠️ Maru: Video no encontrado")
                    return None, None
                
                # Buscar múltiples patrones de video (similar a Mail.ru)
                patterns = [
                    r'"metadataUrl"\s*:\s*"([^"]+)"',  # Igual que Mail.ru
                    r'"file"\s*:\s*"([^"]+\.m3u8[^"]*)"',  # m3u8
                    r'"file"\s*:\s*"([^"]+\.mp4[^"]*)"',  # mp4 directo
                    r'file:\s*"([^"]+\.mp4[^"]*)"',
                    r'source:\s*"([^"]+\.mp4[^"]*)"',
                    r'src:\s*"([^"]+\.mp4[^"]*)"',
                    r'video\[0\]\.file\s*=\s*"([^"]+)"',
                ]
                
                for pattern in patterns:
                    m = re.search(pattern, res.text)
                    if m:
                        video_url = m.group(1)
                        
                        # Si es metadataUrl, hacer request adicional
                        if 'metadataUrl' in pattern:
                            meta_url = video_url
                            if meta_url.startswith('//'):
                                meta_url = "https:" + meta_url
                            
                            meta_res = SESSION.get(meta_url, timeout=10, headers=headers).json()
                            if meta_res.get('videos') and len(meta_res['videos']) > 0:
                                video_url = meta_res['videos'][0]['url']
                                if not video_url.startswith('http'):
                                    video_url = "http:" + video_url
                                return video_url, None
                        else:
                            return video_url, None
                            
            except Exception as e:
                print(f"   ⚠️ Maru error: {e}")
                
    except Exception as e:
        print(f"   ⚠️ Error general: {e}")
    
    # Fallback: devolver URL original para que yt-dlp la procese
    return s_url, None


def play_with_options(final_url, server_url, cookie=None, extra_opts=None):
    # Obtener configuración de red
    net_config = get_network_speed()
    
    if is_termux():
        # Opciones para Termux/Android - optimizadas según velocidad
        cache_secs = net_config["cache_secs"]
        
        opts = [
            "mpv", final_url,
            f"--referrer={server_url}",
            "--vo", "tct",
            "--hwdec", "mediacodec",
            "--cache=yes",
            f"--cache-secs={cache_secs}",
            "--player-operation-mode=cplayer",
            # Buffer adicional para conexiones lentas
            f"--stream-buffer-size={net_config['stream_buffer']}",
            f"--demuxer-max-bytes={net_config['demuxer_bytes']}",
            # Reconnect para estabilidad
            "--demuxer-lavf-o=reconnect=1,reconnect_streamed=1,reconnect_at_eof=1,reconnect_delay_max=10",
        ]
    else:
        # Opciones para desktop - optimizadas según velocidad
        cache_secs = net_config["cache_secs"]
        
        opts = [
            "mpv", final_url,
            f"--referrer={server_url}",
            "--cache=yes",
            f"--cache-secs={cache_secs}",
            f"--stream-buffer-size={net_config['stream_buffer']}",
            f"--demuxer-max-bytes={net_config['demuxer_bytes']}",
            "--force-window=yes",
        ]
        
        # Agregar opciones de reconnect si la conexión no es excelente
        if net_config.get("reconnect"):
            opts.extend([
                "--demuxer-lavf-o=reconnect=1,reconnect_streamed=1,reconnect_at_eof=1,reconnect_delay_max=10",
                "--http-reconnect=yes",
                "--http-reconnect-stream=yes",
                "--http-reconnect-delay-max=15",
            ])
    
    if cookie:
        opts.append(f"--http-header-fields=Cookie: {cookie}")
    if extra_opts:
        opts.extend(extra_opts)
    
    # Mostrar configuración de red (solo en desktop)
    if not is_termux():
        print(f"   📶 Buffer: {net_config['priority']} ({net_config['cache_secs']}s cache)")
    
    return subprocess.run(opts).returncode


def try_ytdlp_play(final_url, server_url):
    try:
        cmd = ["yt-dlp", "-f", "best", "--no-playlist", "--referer", server_url, "-o", "-", final_url]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mpv_cmd = ["mpv", "-", f"--referrer={server_url}", "--cache=yes", "--force-window=yes"]
        mpv = subprocess.Popen(mpv_cmd, stdin=proc.stdout, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if proc.stdout:
            proc.stdout.close()
        return mpv.wait()
    except Exception as e:
        print(f"   ❌ yt-dlp bridge error: {e}")
        return -1


def download_and_play(final_url, server_url):
    print("   📥 Descargando (buffer alto)...")
    
    if is_termux():
        # Termux: descargar a Downloads y abrir con reproductor externo
        temp_file = '/sdcard/Download/cli_ani_video.mp4'
        
        cmd = [
            'yt-dlp', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '-o', temp_file, '--referer', server_url, '--no-playlist', '--buffer-size', '16M', final_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            cmd_alt = ['yt-dlp', '-f', 'best', '-o', temp_file, '--referer', server_url, '--no-playlist', final_url]
            result = subprocess.run(cmd_alt, capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                return False
        
        if os.path.exists(temp_file):
            # Verificar players disponibles en Android
            android_players = check_android_players()
            
            # 1. MPV Android
            if android_players.get('com.mpv.android', False):
                try:
                    print("   📱 Abriendo con MPV Android...")
                    mpv_url = f"com.mpv.android://{temp_file}"
                    subprocess.run(['termux-open', mpv_url], 
                                 capture_output=True, timeout=10)
                    return True
                except:
                    pass
            
            # Fallback: termux-open genérico
            try:
                print("   📱 Abriendo con reproductor externo...")
                subprocess.run(['termux-open', temp_file], capture_output=True, timeout=10)
                return True
            except:
                pass
        return False
    else:
        # Desktop
        import tempfile
        temp_file = os.path.join(tempfile.gettempdir(), 'cli_ani_temp.mp4')
        
        cmd = [
            'yt-dlp', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '-o', temp_file, '--referer', server_url, '--no-playlist', '--buffer-size', '16M', final_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            cmd_alt = ['yt-dlp', '-f', 'best', '-o', temp_file, '--referer', server_url, '--no-playlist', final_url]
            result = subprocess.run(cmd_alt, capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                return False
        
        if os.path.exists(temp_file):
            print("   ▶️  Reproduciendo archivo local...")
            subprocess.run(["mpv", temp_file, "--force-window=yes"])
            try:
                os.remove(temp_file)
            except:
                pass
            return True
        return False


def try_all_methods(final_url, server_url, cookie=None):
    # Mensaje corto para móvil
    method_msg = "Reproduciendo..." if is_termux() else "   ▶️  Método 1: Reproducción directa..."
    print(method_msg)
    
    if play_with_options(final_url, server_url, cookie) == 0:
        return True
    
    if is_termux():
        print("Directo falló, intentando otro...")
    else:
        print("   ▶️  Método 2: Reproducción con cache...")
    
    if play_with_options(final_url, server_url, cookie, ["--cache-secs=600"]) == 0:
        return True
    
    if is_termux():
        print("Cache falló, descargando...")
    else:
        print("   ▶️  Método 3: yt-dlp bridge...")
    
    if try_ytdlp_play(final_url, server_url) == 0:
        return True
    
    print("📥 Descargando...")
    if download_and_play(final_url, server_url):
        return True
    
    return False


def select_from_history():
    if not HISTORY["animes"]:
        return None
    
    print_history()
    print(f"\n0. Nueva búsqueda")
    
    try:
        choice = int(input("\nSelecciona (0-10): "))
    except:
        return None
    
    if choice == 0:
        return None
    
    if 0 < choice <= len(HISTORY["animes"]):
        return HISTORY["animes"][choice - 1]
    
    return None


def main():
    load_history()
    
    print("\n" + "="*60)
    print("🚀  CLI-ANI v0.666  🚀")
    print("="*60 + "\n")
    
    # Menú principal
    print("1. Buscar anime")
    print("2. Ver historial")
    
    try:
        menu_choice = input("\nOpción: ").strip()
    except:
        menu_choice = "1"
    
    selected = None
    
    if menu_choice == "2":
        selected = select_from_history()
        if selected is None:
            query = input("\n🔍 Anime a buscar: ").strip()
        else:
            query = None
    else:
        query = input("🔍 Anime a buscar: ").strip()
    
    if not query and not selected:
        print("❌ Sin texto de búsqueda")
        return
    
    # Obtener anime
    if selected:
        anime_title = selected['title']
        anime_url = selected['url']
    else:
        try:
            res = SESSION.get(f"{BASE_URL}/browse", params={'q': query}, timeout=10)
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return
        
        if not res or not res.text:
            print("❌ Error: Respuesta vacía")
            return
        
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('ul.ListAnimes li')
        results = []
        for i in items:
            h3 = i.find('h3')
            a = i.find('a')
            if h3 and a:
                results.append({'t': h3.get_text(strip=True), 'u': a.get('href', '')})

        if not results:
            print("❌ No se encontraron resultados.")
            return
            
        for i, r in enumerate(results[:10]):
            print(f"{i+1}. {r['t']}")

        idx = int(input("\n🔢 Selecciona: ")) - 1
        anime_title = results[idx]['t']
        anime_url = results[idx]['u']
    
    # Obtener episodios
    try:
        res_anime = SESSION.get(f"{BASE_URL}{anime_url}", timeout=10)
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    slug_match = re.search(r"var anime_info = \[(.*?)\];", res_anime.text)
    eps_match = re.search(r"var episodes = (\[\[.*\]\]);", res_anime.text)
    
    if not slug_match or not eps_match:
        print("❌ No se pudieron parsear los episodios")
        return
    
    slug = slug_match.group(1).split(',')[-1].strip('" ')
    eps_list = sorted([e[0] for e in json.loads(eps_match.group(1))])
    
    # Guardar en historial
    add_to_history(anime_title, anime_url, slug)
    
    print(f"\n📺 {anime_title}")
    print(f"📑 Episodios: {eps_list[0]} - {eps_list[-1]}")
    
    # Mostrar episodios con verde para vistos
    print("\n📋 Lista de episodios:")
    print("-" * 40)
    for ep in eps_list:
        if is_episode_viewed(slug, ep):
            print(f"  \033[92m● {ep}\033[0m")  # Verde
        else:
            print(f"  ○ {ep}")
    print("-" * 40)
    print("Leyenda: \033[92m●\033[0m = visto, ○ = no visto")
    
    target = input("\n💬 Episodio: ").strip() or eps_list[-1]
    
    # Obtener servidores
    try:
        res_ep = SESSION.get(f"{BASE_URL}/ver/{slug}-{target}", timeout=10)
        videos_match = re.search(r"var videos = ({.*?});", res_ep.text)
        if not videos_match:
            print("❌ No se encontraron servidores en la página")
            return
        servers_raw = json.loads(videos_match.group(1))
    except Exception as e:
        print(f"❌ Error obteniendo servidores: {e}")
        return

    raw_list = []
    for lang in servers_raw:
        for s in servers_raw[lang]:
            raw_list.append({'n': s['title'], 'u': s['code'].replace('\\', '')})

    priority = {"YourUpload": 0, "Maru": 1, "Streamwish": 2}
    sorted_servers = sorted(raw_list, key=lambda x: priority.get(x['n'], 99))

    print(f"\n🎬 Servidores ({len(sorted_servers)}):")
    for i, s in enumerate(sorted_servers):
        print(f"  {i+1}. [{s['n']}]")

    # Intentar cada servidor
    for idx, server in enumerate(sorted_servers):
        # Mensajes cortos para móvil
        print(f"\n[{server['n']}] ({idx+1}/{len(sorted_servers)})")
        
        print("Extrayendo...")
        final_url, cookie = get_best_link(server)
        
        if not final_url:
            print("❌ Sin URL")
            continue
        
        # Solo mostrar URL en desktop
        if not is_termux():
            print(f"   📡 {final_url[:40]}...")
        
        if try_all_methods(final_url, server['u'], cookie):
            ok = input("Funciono? [s/n]: ").strip().lower()
            if ok == 's':
                mark_episode_viewed(slug, target)
                print(f"   ✅ Episodio {target} marcado")
                break
        else:
            print("❌ Fallo, siguiente...")


if __name__ == "__main__":
    # Verificar dependencias primero
    if not check_dependencies():
        print("\n⚠️  Instala las dependencias faltantes y vuelve a ejecutar.")
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋")
    except Exception as e:
        print(f"\n❌ Error: {e}")
