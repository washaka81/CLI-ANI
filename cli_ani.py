# -*- coding: utf-8 -*-
# =============================================================================
# CLI-ANI - Edición Termux Fix v0.716
# =============================================================================
# Desarrollado con honestidad por Washaka (2026)
# =============================================================================

import requests, re, json, subprocess, string, html, sys, os, time, select, shutil, platform
from datetime import datetime
from bs4 import BeautifulSoup

BASE_URL = "https://www3.animeflv.net"
SESSION = requests.Session()
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
SESSION.headers.update({'User-Agent': UA, 'Referer': 'https://www3.animeflv.net/'})

MW = 38 # Ancho estricto para Termux

def is_termux():
    """Detección robusta de Termux"""
    return (
        os.environ.get('TERMUX_VERSION') is not None or 
        os.path.exists('/data/data/com.termux') or
        'com.termux' in os.environ.get('PREFIX', '')
    )

# --- INTERFAZ ---

def get_timer_color(rem):
    if rem > 7: return "\033[38;5;82m" 
    if rem > 4: return "\033[38;5;226m"
    return "\033[38;5;196m"            

def timed_input(prompt, timeout=10):
    start = time.time()
    try:
        while True:
            rem = int(timeout - (time.time() - start))
            if rem <= 0:
                sys.stdout.write(f"\r{prompt} [\033[91m0s\033[0m]: ")
                sys.stdout.flush()
                return ""
            color = get_timer_color(rem)
            sys.stdout.write(f"\r{prompt} ({color}{rem}s\033[0m): ")
            sys.stdout.flush()
            r, _, _ = select.select([sys.stdin], [], [], 0.5)
            if r: return sys.stdin.readline().strip().lower()
    except: return ""

def ask_success():
    print("\n" + "─"*MW)
    res = timed_input("❓ ¿Se abrió bien el video? (S/N)", timeout=10)
    print("\n" + "─"*MW)
    return res in ['s', 'si', 'sí', 'y', 'yes']

# --- EXTRACTORES ---

def get_link(server):
    name, url = server['n'], server['u']
    print(f"\n ✨ Conectando: {name}")
    try:
        if "yourupload" in url.lower():
            res = SESSION.get(url.replace("download?file=", "embed/"), timeout=8).text
            m = re.search(r'og:video" content="([^"]+)"', res) or re.search(r"file:\s*'([^']+)'", res)
            if m: return (m.group(1) if "vid" in m.group(1) else f"https://www.yourupload.com{m.group(1)}"), None
        elif any(d in url.lower() for d in ['hqq', 'netu', 'waaw']):
            res = SESSION.get(url, headers={'Referer': 'https://www3.animeflv.net/'}, timeout=8).text
            v = re.search(r'(https?://[^\s"\'<>]+\.(?:m3u8|mp4)[^\s"\'<>]*)', res)
            if v and "1s" not in v.group(1): return v.group(1), None
    except: pass
    return url, None

# --- REPRODUCCIÓN (SALIDA HONESTA) ---

def play(url, server_name, ref=None):
    termux = is_termux()
    print(f" 🚀 Lanzando: {server_name}")
    
    if not any(x in url.lower() for x in ['.m3u8', '.mp4']):
        print(" 📊 STATUS REAL (yt-dlp):")
        try:
            cmd = ['yt-dlp', '--no-check-certificate', '--progress', '-g', url]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            final_url = ""
            for line in p.stdout:
                if line.strip().startswith('http'): final_url = line.strip()
                else: sys.stdout.write(f"\r   ▷ {line.strip()[:MW-6]} ")
            p.wait()
            if final_url: url = final_url
            print("")
        except: pass

    if termux:
        # Prioridad a las apps de MPV antes que termux-open
        methods = [
            ("MPV Oficial", ["am", "start", "--user", "0", "-a", "android.intent.action.VIEW", "-d", url, "-n", "io.mpv/.MPVActivity", "-f", "0x10000000", "--es", "http-header-referer", ref]),
            ("MPV Fork", ["am", "start", "--user", "0", "-a", "android.intent.action.VIEW", "-d", url, "-n", "is.xyz.mpv/.MPVActivity", "-f", "0x10000000"]),
            ("Navegador/Otros", ["termux-open", url])
        ]
        for name, c in methods:
            try:
                res = subprocess.run(c, capture_output=True, timeout=5)
                if res.returncode == 0:
                    print(f"   🎬 Abriendo con {name}...")
                    if ask_success(): return True
            except: continue
    else:
        cmd = ["mpv", url, f"--referrer={ref}", "--cache=yes", "--force-window=yes"]
        try:
            subprocess.run(cmd)
            return ask_success()
        except: pass
    return False

# --- DATOS ---

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cli_ani_data.json')
DB = {"history": [], "vistos": {}, "ranks": {}}

def load_db():
    global DB
    try:
        if os.path.exists(DB_FILE):
            DB.update(json.load(open(DB_FILE)))
    except: pass

def save_db():
    try: json.dump(DB, open(DB_FILE, 'w'), indent=2)
    except: pass

def get_rate(n):
    r = DB["ranks"].get(n, {"s": 0, "t": 0})
    return (r["s"] / r["t"] * 100) if r.get("t", 0) > 0 else 50.0

# --- MAIN ---

def main():
    load_db()
    print("\n" + "═"*MW)
    print(" ✨ CLI-ANI v0.716 ✨ ".center(MW))
    print("═"*MW)
    
    if is_termux(): print("📱 Android detectado".center(MW))
    
    print("\n 1. 🔍 ¡Buscar Anime!\n 2. 📚 Ver historial")
    op = input("\n ⏩ Elige: ").strip() or "1"
    
    sel = None
    if op == "2" and DB["history"]:
        print("\n 📂 Recientes:")
        for i, a in enumerate(DB["history"]): print(f"  {i+1}. {a['t'][:30]}")
        try:
            h_idx = int(input("\n ⏩ Selecciona (0=buscar): ") or "0")
            if h_idx > 0: sel = DB["history"][h_idx-1]
        except: pass

    query = input("\n 🔍 Escribe el nombre: ").strip() if not sel else None
    if not query and not sel: return

    if not sel:
        try:
            res = SESSION.get(f"{BASE_URL}/browse", params={'q': query}, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('ul.ListAnimes li')
            if not items: print(" ⚠️ Sin resultados."); return
            results = [{'t': i.find('h3').get_text(strip=True), 'u': i.find('a').get('href', '')} for i in items if i.find('h3')]
            print("\n 🌟 Encontrados:")
            for i, r in enumerate(results[:10]): print(f"  {i+1}. {r['t'][:30]}")
            sel = results[int(input("\n 🔢 Número: ")) - 1]
        except: return

    res_a = SESSION.get(f"{BASE_URL}{sel['u']}", timeout=10)
    sm = re.search(r"var anime_info = \[(.*?)\];", res_a.text)
    slug = [p.strip('" ') for p in sm.group(1).split(',')][2] if sm else sel['u'].split('/')[-1]
    
    eps_raw = json.loads(re.search(r"var episodes = (\[\[.*\]\]);", res_a.text).group(1))
    try: eps = sorted([e[0] for e in eps_raw], key=lambda x: float(x))
    except: eps = sorted([e[0] for e in eps_raw])
    
    DB["history"] = [a for a in DB["history"] if a['u'] != sel['u']]
    DB["history"].insert(0, sel); DB["history"] = DB["history"][:10]; save_db()

    print(f"\n 📺 Serie: \033[92m{sel['t'][:30]}\033[0m")
    vistos = DB["vistos"].get(slug, [])
    for i, e in enumerate(eps):
        m = "\033[92m●\033[0m" if str(e) in vistos else "○"
        print(f"{m}{str(e).ljust(3)}", end=" " if (i+1)%4 != 0 else "\n")
    print("\n")
    
    target = input(" 💬 Episodio: ").strip() or str(eps[-1])
    try:
        res_e = SESSION.get(f"{BASE_URL}/ver/{slug}-{target}", timeout=10)
        v_raw = json.loads(re.search(r"var videos = ({.*?});", res_e.text).group(1))
        srvs = []
        for l in v_raw:
            for s in v_raw[l]: srvs.append({'n': s['title'], 'u': s['code'].replace('\\', '')})
    except: print(" ⚠️ Error de conexión."); return

    srvs = sorted(srvs, key=lambda x: get_rate(x['n']), reverse=True)

    print(f"\n 🎬 RANKING ÉXITO:")
    print(f" {'#':<2} {'Fuente':<10} {'%':<5} {'Hist'}")
    print("─"*MW)
    for i, s in enumerate(srvs):
        r = get_rate(s['n'])
        st = DB["ranks"].get(s['n'], {"s": 0, "t": 0})
        print(f" {i+1:<2} {s['n'][:10]:<10} {int(r):>3}%  {st['s']}/{st['t']}")

    for idx, s in enumerate(srvs):
        try:
            print(f"\n 📡 Probando: {s['n']} ({int(get_rate(s['n']))}%)")
            f_url, _ = get_link(s)
            if play(f_url, s['n'], s['u']):
                if s['n'] not in DB["ranks"]: DB["ranks"][s['n']] = {"s": 0, "t": 0}
                DB["ranks"][s['n']]["t"] += 1; DB["ranks"][s['n']]["s"] += 1
                if slug not in DB["vistos"]: DB["vistos"][slug] = []
                if str(target) not in DB["vistos"][slug]: DB["vistos"][slug].append(str(target))
                save_db(); print(f" ✅ ¡Listo! Que lo disfrutes."); break
            else:
                if s['n'] not in DB["ranks"]: DB["ranks"][s['n']] = {"s": 0, "t": 0}
                DB["ranks"][s['n']]["t"] += 1; save_db()
        except: continue

if __name__ == "__main__":
    if not shutil.which("yt-dlp"): print(" ⚠️ Instala 'yt-dlp'"); sys.exit(1)
    try: main()
    except KeyboardInterrupt: print("\n 👋 ¡Chao!")
    except Exception as e: print(f"\n ⚠️ Error: {type(e).__name__}")
