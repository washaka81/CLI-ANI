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


def play_with_mpv(url, referer, cookie=None):
    """Reproduce video con mpv según la plataforma"""
    if is_termux():
        # Opciones para Android/Termux
        opts = [
            'mpv', url,
            '--referrer', referer,
            '--vo', 'tct',
            '--hwdec', 'mediacodec',
            '--cache', 'yes',
            '--cache-secs', '300',
            '--player-operation-mode', 'cplayer',
        ]
        
        if cookie:
            opts.extend(['--http-header-fields', f'Cookie: {cookie}'])
        
        # Intentar primero con mpv
        try:
            result = subprocess.run(opts, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                return True
        except:
            pass
        
        # Si falla, intentar con termux-open
        try:
            print("   📱 Abriendo con reproductor externo...")
            subprocess.run(['termux-open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except:
            pass
        
        return False
    else:
        # Opciones para desktop
        opts = [
            'mpv', url,
            '--referrer', referer,
            '--cache', 'yes',
            '--cache-secs', '300',
            '--force-window', 'yes',
        ]
        
        if cookie:
            opts.extend(['--http-header-fields', f'Cookie: {cookie}'])
        
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
    s_name = server['n']
    s_url = server['u']
    
    try:
        if s_name == "YourUpload":
            res = SESSION.get(s_url, timeout=4).text
            m = re.search(r'<meta property="og:video" content="([^"]+)"', res) or re.search(r"file:\s*'([^']+)'", res)
            if m: return m.group(1), None

        elif s_name == "Okru":
            res = html.unescape(SESSION.get(s_url, timeout=4).text).replace('\\', '')
            m = re.findall(r'\{"name":"([^"]+)","url":"([^"]+)"', res)
            if m: return m[0][1].replace("u0026", "&"), None

        elif s_name == "Mail.ru":
            res = SESSION.get(s_url, timeout=4).text
            meta = re.search(r'"metadataUrl"\s*:\s*"([^"]+)"', res)
            if meta:
                m_url = "https:" + meta.group(1) if meta.group(1).startswith('//') else meta.group(1)
                r_meta = SESSION.get(m_url, timeout=4)
                url = r_meta.json()['videos'][0]['url']
                cookie = f"video_key={r_meta.cookies.get('video_key')}"
                return url, cookie

        elif any(d in s_url for d in ['streamwish', 'embedwish', 'hlswish', 'awish', 'dwish', 'streamwish.to']):
            res = SESSION.get(s_url, timeout=5).text
            
            if 'main.js' in res or 'loading' in res.lower():
                print("   ⚠️ Streamwish nuevo detectado, intentando Playwright...")
                return try_playwright_streamwish(s_url), None
            
            m = re.search(r"eval\(function\(p,a,c,k,e,d\).*?}\('(.*?)',(\d+),(\d+),'(.*?)'\.split", res, re.DOTALL)
            if m:
                p, a, c, k = m.groups()
                a, c, k = int(a), int(c), k.split('|')
                d = {int2base(i, a): k[i] if (i < len(k) and k[i]) else int2base(i, a) for i in range(c)}
                unpacked = re.sub(r'\b(\w+)\b', lambda m: d.get(m.group(1), m.group(1)), p)
                m3u8 = re.search(r'(?:file|hls2|hls):"([^"]+\.m3u8[^"]*)"', unpacked.replace('\\', ''))
                if m3u8: return m3u8.group(1), None
            
            print("   ⚠️ Packer falló, intentando Playwright...")
            return try_playwright_streamwish(s_url), None
            
    except Exception as e:
        print(f"   ⚠️ Error: {e}")

    return s_url, None


def play_with_options(final_url, server_url, cookie=None, extra_opts=None):
    if is_termux():
        # Opciones para Termux/Android
        opts = [
            "mpv", final_url,
            f"--referrer={server_url}",
            "--vo", "tct",
            "--hwdec", "mediacodec",
            "--cache=yes",
            "--cache-secs=300",
            "--player-operation-mode=cplayer",
        ]
    else:
        # Opciones para desktop
        opts = [
            "mpv", final_url,
            f"--referrer={server_url}",
            "--cache=yes",
            "--cache-secs=300",
            "--demuxer-lavf-o=reconnect=1,reconnect_streamed=1,reconnect_at_eof=1,reconnect_delay_max=5",
            "--stream-buffer-size=16MiB",
            "--demuxer-max-bytes=100MiB",
            "--force-window=yes",
        ]
    
    if cookie:
        opts.append(f"--http-header-fields=Cookie: {cookie}")
    if extra_opts:
        opts.extend(extra_opts)
    
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
            print("   📱 Abriendo con reproductor externo...")
            # Intentar con termux-open
            try:
                subprocess.run(['termux-open', temp_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except:
                # Fallback a mpv
                subprocess.run(['mpv', temp_file, '--vo', 'tct', '--hwdec', 'mediacodec'], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
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
    print("   ▶️  Método 1: Reproducción directa...")
    if play_with_options(final_url, server_url, cookie) == 0:
        return True
    
    print("   ▶️  Método 2: Reproducción con cache...")
    if play_with_options(final_url, server_url, cookie, ["--cache-secs=600"]) == 0:
        return True
    
    print("   ▶️  Método 3: yt-dlp bridge...")
    if try_ytdlp_play(final_url, server_url) == 0:
        return True
    
    print("   ▶️  Método 4: Descargar y reproducir...")
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
        print(f"\n{'='*50}")
        print(f"🔄 Probando [{server['n']}] ({idx+1}/{len(sorted_servers)})")
        print("="*50)
        
        print(f"⚡ Extrayendo...")
        final_url, cookie = get_best_link(server)
        
        if not final_url:
            print("   ❌ Sin URL")
            continue
        
        print(f"   📡 {final_url[:50]}...")
        
        if try_all_methods(final_url, server['u'], cookie):
            ok = input("\n✅ ¿Se pudo reproducir el video? [s/n]: ").strip().lower()
            if ok == 's':
                # Marcar como visto
                mark_episode_viewed(slug, target)
                print(f"   ✅ Episodio {target} marcado como visto")
                break
        else:
            print("   ❌ No funcionó, intentando siguiente...")


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
