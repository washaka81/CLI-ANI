# -*- coding: utf-8 -*-
# =============================================================================
# CLI-ANI - Edición De-Obfuscator v0.719
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

MW = 38 # Ancho móvil

def is_termux():
    return os.path.exists('/data/data/com.termux') or 'com.termux' in os.environ.get('PREFIX', '')

# --- UTILIDADES DE DESOFUSCACIÓN ---

def js_unpack(p, a, c, k, e, d):
    """Implementación de Unpacker P.A.C.K.E.R."""
    def baseN(num, b):
        chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return ((num == 0) and chars[0]) or (baseN(num // b, b).lstrip(chars[0]) + chars[num % b])
    
    for i in range(c - 1, -1, -1):
        if k[i]:
            p = re.sub(r'\b' + baseN(i, a) + r'\b', k[i], p)
    return p

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
    res = timed_input("❓ ¿Se abrió bien? (S/N)", timeout=10)
    if res == "": print()
    print("─"*MW)
    return res in ['s', 'si', 'sí', 'y', 'yes']

# --- EXTRACTORES AVANZADOS ---

def get_link(server):
    name, url = server['n'], server['u']
    print(f" ✨ Analizando: {name}")
    try:
        # Heurística YourUpload
        if "yourupload" in url.lower():
            res = SESSION.get(url.replace("download?file=", "embed/"), timeout=8).text
            m = re.search(r'og:video" content="([^"]+)"', res) or re.search(r"file:\s*'([^']+)'", res)
            if m: return (m.group(1) if "vid" in m.group(1) else f"https://www.yourupload.com{m.group(1)}"), None
        
        # Heurística Okru (Direct qualities)
        elif "ok" in url.lower():
            res = SESSION.get(url, timeout=8).text
            v = re.findall(r'\{"name":"([^"]+)","url":"([^"]+)"\}', html.unescape(res).replace('\\', ''))
            if v: return sorted(v, key=lambda x: x[0], reverse=True)[0][1].replace("u0026", "&"), None

        # Heurística Streamwish (P.A.C.K.E.R.)
        elif any(d in url.lower() for d in ['streamwish', 'swhoi']):
            res = SESSION.get(url, timeout=8).text
            pack = re.search(r"\}\('(.*?)',(\d+),(\d+),'(.*?)'\.split", res)
            if pack:
                unpacked = js_unpack(pack.group(1), int(pack.group(2)), int(pack.group(3)), pack.group(4).split('|'), 0, {})
                m3u8 = re.search(r'file:"([^"]+\.m3u8)"', unpacked)
                if m3u8: return m3u8.group(1), None

        # Heurística Netu / HQQ (Cookie bypass)
        elif any(d in url.lower() for d in ['hqq', 'netu', 'waaw']):
            res = SESSION.get(url, headers={'Referer': 'https://www3.animeflv.net/'}, timeout=8).text
            v = re.search(r'(https?://[^\s"\'<>]+\.(?:m3u8|mp4)[^\s"\'<>]*)', res)
            if v and "1s" not in v.group(1): return v.group(1), None
            
    except: pass
    return url, None

# --- REPRODUCCIÓN (FUERZA ANDROID) ---

def play(url, server_name, ref=None):
    print(f" 🚀 Lanzando: {server_name[:12]}")
    
    # STATUS HONESTO YT-DLP
    if not any(x in url.lower() for x in ['.m3u8', '.mp4']):
        print(" 📊 Status Real (yt-dlp):")
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

    if is_termux():
        methods = [
            ("MPV Oficial", ["am", "start", "--user", "0", "-a", "android.intent.action.VIEW", "-d", url, "-n", "io.mpv/.MPVActivity", "-f", "0x10000000", "--es", "http-header-referer", ref, "--es", "http-header-user-agent", UA]),
            ("MPV Fork", ["am", "start", "--user", "0", "-a", "android.intent.action.VIEW", "-d", url, "-n", "is.xyz.mpv/.MPVActivity", "-f", "0x10000000", "--es", "http-header-referer", ref, "--es", "http-header-user-agent", UA])
        ]
        for _, c in methods:
            try:
                res = subprocess.run(c, capture_output=True, timeout=5)
                if res.returncode == 0:
                    if ask_success(): return True
            except: continue
        return False
    else:
        cmd = ["mpv", url, f"--referrer={ref}", "--cache=yes", "--force-window=yes"]
        try: subprocess.run(cmd); return ask_success()
        except: pass
    return False

# --- GESTIÓN DE DATOS ---

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cli_ani_data.json')
DB = {"history": [], "vistos": {}, "ranks": {}}

def load_db():
    global DB
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f: DB.update(json.load(f))
    except: pass

def save_db():
    try:
        with open(DB_FILE, 'w') as f: json.dump(DB, f, indent=2)
    except: pass

def get_rate(n):
    r = DB["ranks"].get(n, {"s": 0, "t": 0})
    return (r["s"] / r["t"] * 100) if r.get("t", 0) > 0 else 50.0

# --- MAIN ---

def main():
    load_db()
    print("\n" + "🌸 BIENVENIDO A CLI-ANI 🌸".center(MW, "═"))
    
    print("\n 1. 🔍 ¡Busquemos un Anime!\n 2. 📚 Ver historial")
    op = input("\n ⏩ ¿Qué te apetece hoy?: ").strip() or "1"
    
    sel = None
    if op == "2" and DB["history"]:
        print("\n 📂 Tu historial:")
        for i, a in enumerate(DB["history"]): print(f"  {i+1}. {a['t'][:30]}")
        try:
            h_idx = int(input("\n ⏩ Elige (0=buscar): ") or "0")
            if h_idx > 0: sel = DB["history"][h_idx-1]
        except: pass

    query = input("\n 🔍 ¿Qué serie quieres ver?: ").strip() if not sel else None
    if not query and not sel: return

    if not sel:
        try:
            res = SESSION.get(f"{BASE_URL}/browse", params={'q': query}, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('ul.ListAnimes li')
            if not items: print(" ⚠️ Sin resultados."); return
            results = [{'t': i.find('h3').get_text(strip=True), 'u': i.find('a').get('href', '')} for i in items if i.find('h3')]
            print("\n 🌟 Resultados:")
            for i, r in enumerate(results[:10]): print(f"  {i+1}. {r['t'][:30]}")
            sel = results[int(input("\n 🔢 ¿Cuál prefieres?: ")) - 1]
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
    
    target = input(" 💬 ¿Qué episodio pongo?: ").strip() or str(eps[-1])
    try:
        res_e = SESSION.get(f"{BASE_URL}/ver/{slug}-{target}", timeout=10)
        v_raw = json.loads(re.search(r"var videos = ({.*?});", res_e.text).group(1))
        srvs = []
        for l in v_raw:
            for s in v_raw[l]: srvs.append({'n': s['title'], 'u': s['code'].replace('\\', '')})
    except: print(" ⚠️ Servidores ocupados."); return

    srvs = sorted(srvs, key=lambda x: get_rate(x['n']), reverse=True)

    print(f"\n 🎬 RANKING (Tasa de éxito):")
    print(f" {'#':<2} {'Fuente':<10} {'%':<4} {'Hist'}")
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
                save_db(); print(f" ✅ ¡Listo! Disfruta del episodio."); break
            else:
                if s['n'] not in DB["ranks"]: DB["ranks"][s['n']] = {"s": 0, "t": 0}
                DB["ranks"][s['n']]["t"] += 1; save_db()
        except: continue

if __name__ == "__main__":
    if not shutil.which("yt-dlp"): print(" ⚠️ Instala 'yt-dlp'"); sys.exit(1)
    try: main()
    except KeyboardInterrupt: print("\n 👋 ¡Chao!")
    except Exception as e: print(f"\n ⚠️ Oops: {type(e).__name__}")
