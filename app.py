#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
西北风喝吗 · 个人主页 后端服务
纯 Python 标准库实现（http.server + sqlite3），无第三方依赖。
功能：访客统计、随机一言（本地 105 句 + hitokoto 接口补充）、留言板、摸鱼计数、静态文件托管。
"""
import json
import os
import re
import sqlite3
import time
import random
import urllib.request
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "site.db")
START_TIME = time.time()
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "3000"))

# ---- 本地随机一言（105 句精选）----
QUOTES = [
    "你指尖跃动的电光，是我此生不变的信仰。",
    "真正的强大，是温柔。",
    "人类皆是棋子，但棋子也能改变棋局。",
    "吾王剑锋所指，吾等心之所向。",
    "等价交换，是炼金术不变的原则。",
    "我不做人了，JOJO！",
    "前方高能反应，请注意！",
    "不要停下来啊！",
    "真相只有一个。",
    "以我之名，守护我想守护的一切。",
    "即使折断翅膀，也要飞翔。",
    "世界上没有偶然，有的只是必然。",
    "只要不放弃，就还有希望。",
    "所谓觉悟，就是在漆黑的荒野上开辟出一条理当前进的光明大道。",
    "人的梦想，是不会结束的！",
    "我想要活下去，把你也带出这片海。",
    "雏鸟若无飞翔的勇气，就无法遨游天际。",
    "时间会证明一切。",
    "愿你的眼中总有光芒，活成你想要的模样。",
    "温柔正确的人总是难以生存，因为这世界既不温柔，也不正确。",
    "比孤独更可怕的，是在人群中感到孤独。",
    "如果可以的话，我想永远停留在那个夏天。",
    "所有的相遇，都是久别重逢。",
    "心若没有栖息的地方，到哪里都是流浪。",
    "我们仰望着同一片天空，却看着不同的地方。",
    "代码一时爽，一直代码一直爽。",
    "人生就像写代码，偶尔也会出 bug。",
    "如果代码能说话，它一定在骂你。",
    "复制粘贴一时爽，改起 bug 火葬场。",
    "世界上没有解决不了的 bug，只有没熬到的夜。",
    "程序员的三宝：咖啡、耳机、Ctrl+Z。",
    "代码要像女朋友一样，能跑就别乱动。",
    "先让程序跑起来，再谈优雅。",
    "不要重复造轮子，除非你造的轮子更圆。",
    "计算机从不犯错，犯错的只有程序员。",
    "Talk is cheap. Show me the code.",
    "世界上有两件难事：命名、缓存失效和差一错误。",
    "认真读文档，是程序员最高贵的品质。",
    "一个 bug 的诞生，往往始于「我觉得这样写没问题」。",
    "凌晨四点的代码，最香。",
    "种一棵树最好的时间是十年前，其次是现在。",
    "慢慢来，比较快。",
    "世界上只有一种英雄主义，就是认清生活真相后依然热爱生活。",
    "愿你出走半生，归来仍是少年。",
    "今天的努力，是为了明天的不加班。",
    "只要有梦想，什么时候开始都不晚。",
    "勇气，是看清世界的真相后依然热爱它。",
    "生活不止眼前的苟且，还有诗和远方。",
    "心之所向，素履以往。",
    "路虽远，行则将至；事虽难，做则必成。",
    "星光不问赶路人，时光不负有心人。",
    "但行好事，莫问前程。",
    "越努力，越幸运。",
    "你的坚持，终将美好。",
    "别怕，往前走，天总会亮。",
    "人生没有白走的路，每一步都算数。",
    "你只管努力，剩下的交给时间。",
    "凡是过往，皆为序章。",
    "所有的失去，都会以另一种方式归来。",
    "眼里有光，心中有火，脚下有路。",
    "长风破浪会有时，直挂云帆济沧海。",
    "会当凌绝顶，一览众山小。",
    "天生我材必有用，千金散尽还复来。",
    "山重水复疑无路，柳暗花明又一村。",
    "莫愁前路无知己，天下谁人不识君。",
    "千磨万击还坚劲，任尔东西南北风。",
    "纸上得来终觉浅，绝知此事要躬行。",
    "问渠那得清如许，为有源头活水来。",
    "落红不是无情物，化作春泥更护花。",
    "宝剑锋从磨砺出，梅花香自苦寒来。",
    "不畏浮云遮望眼，自缘身在最高层。",
    "海内存知己，天涯若比邻。",
    "及时当勉励，岁月不待人。",
    "少年易老学难成，一寸光阴不可轻。",
    "路漫漫其修远兮，吾将上下而求索。",
    "衣带渐宽终不悔，为伊消得人憔悴。",
    "众里寻他千百度，蓦然回首，那人却在灯火阑珊处。",
    "春风得意马蹄疾，一日看尽长安花。",
    "沉舟侧畔千帆过，病树前头万木春。",
    "千淘万漉虽辛苦，吹尽狂沙始到金。",
    "人类是一种连五分钟都等不了的生物。",
    "浪漫，就是浪费时间慢慢看一朵花开。",
    "如果这个世界没有你喜欢的人，那就创造一个。",
    "兴趣是最好的老师。",
    "坚持做一件小事，时间会给你惊喜。",
    "热爱可抵岁月漫长。",
    "世界很大，你值得去看看。",
    "保持热爱，奔赴山海。",
    "你认真生活的样子，真的很酷。",
    "把日子过成诗，简单而精致。",
    "微笑面对生活，生活也会微笑面对你。",
    "知足者常乐。",
    "独行快，众行远。",
    "细节决定成败。",
    "一切都会好起来的。",
    "明天又是新的一天。",
    "活在当下，珍惜眼前。",
    "有梦就去追，趁年轻。",
    "努力的意义，就是让自己拥有更多选择的权利。",
    "愿你被这世界温柔以待。",
    "每一份热爱，都值得被认真对待。",
    "时间不语，却回答了所有问题。",
    "你只管盛开，蝴蝶自来。",
    "心宽一寸，路宽一丈。",
    "简单点，再简单点。",
]

# 限流：同 IP 点「摸鱼」的最小间隔（秒）
CLICK_COOLDOWN = 1.5
_click_last = {}


def now_date():
    return time.strftime("%Y-%m-%d")


def ip_hash(ip):
    return hashlib.md5(ip.encode("utf-8")).hexdigest()


_geo_cache = {}


def geo_lookup(ip):
    """根据 IP 查国家（ip-api.com 免费接口，失败返回空）。"""
    if ip in _geo_cache:
        return _geo_cache[ip]
    result = ("", "")
    try:
        req = urllib.request.Request(
            "http://ip-api.com/json/{0}?fields=country,countryCode&lang=zh-CN".format(ip),
            headers={"User-Agent": "Mozilla/5.0 (XbfhmSite)"},
        )
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("status") == "success":
            result = (data.get("country") or "", data.get("countryCode") or "")
    except Exception:
        pass
    _geo_cache[ip] = result
    return result


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS visits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_hash TEXT NOT NULL,
        date TEXT NOT NULL,
        ts INTEGER NOT NULL,
        UNIQUE(ip_hash, date)
    )""")
    _cols = [r["name"] for r in conn.execute("PRAGMA table_info(visits)").fetchall()]
    if "country" not in _cols:
        conn.execute("ALTER TABLE visits ADD COLUMN country TEXT DEFAULT ''")
    if "country_code" not in _cols:
        conn.execute("ALTER TABLE visits ADD COLUMN country_code TEXT DEFAULT ''")
    conn.execute("""CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        content TEXT NOT NULL,
        ts INTEGER NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS counter(
        id INTEGER PRIMARY KEY CHECK(id = 1),
        clicks INTEGER NOT NULL DEFAULT 0
    )""")
    conn.execute("INSERT OR IGNORE INTO counter(id, clicks) VALUES(1, 0)")
    conn.commit()
    conn.close()


def record_visit(ip):
    h = ip_hash(ip)
    d = now_date()
    conn = get_db()
    exists = conn.execute(
        "SELECT 1 FROM visits WHERE ip_hash = ? AND date = ?", (h, d)
    ).fetchone()
    if exists:
        conn.close()
        return
    country, cc = geo_lookup(ip)
    conn.execute(
        "INSERT INTO visits(ip_hash, date, country, country_code, ts) VALUES(?, ?, ?, ?, ?)",
        (h, d, country, cc, int(time.time())),
    )
    conn.commit()
    conn.close()


def stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) AS c FROM visits").fetchone()["c"]
    today = conn.execute(
        "SELECT COUNT(*) AS c FROM visits WHERE date = ?", (now_date(),)
    ).fetchone()["c"]
    clicks = conn.execute("SELECT clicks FROM counter WHERE id = 1").fetchone()["clicks"]
    conn.close()
    return {
        "visits_total": total,
        "visits_today": today,
        "clicks": clicks,
        "uptime_seconds": int(time.time() - START_TIME),
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(START_TIME)),
    }


def locations():
    conn = get_db()
    rows = conn.execute(
        "SELECT country, country_code, COUNT(*) AS cnt FROM visits "
        "WHERE country != '' GROUP BY country ORDER BY cnt DESC LIMIT 30"
    ).fetchall()
    conn.close()
    return {
        "locations": [
            {"country": r["country"], "country_code": r["country_code"], "count": r["cnt"]}
            for r in rows
        ]
    }


def server_status():
    mem_total = mem_used = 0
    try:
        info = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k, v = line.split(":", 1)
                info[k.strip()] = int(v.strip().split()[0])
        mem_total = info.get("MemTotal", 0)
        mem_used = mem_total - info.get("MemAvailable", 0)
    except Exception:
        pass
    disk_total = disk_used = 0
    try:
        st = os.statvfs("/")
        disk_total = st.f_blocks * st.f_frsize
        disk_used = (st.f_blocks - st.f_bfree) * st.f_frsize
    except Exception:
        pass
    load = ""
    try:
        with open("/proc/loadavg") as f:
            load = f.read().strip()
    except Exception:
        pass
    sys_uptime = 0
    try:
        with open("/proc/uptime") as f:
            sys_uptime = float(f.read().split()[0])
    except Exception:
        pass
    import sys as _sys
    return {
        "memory": {"total": mem_total, "used": mem_used},
        "disk": {"total": disk_total, "used": disk_used},
        "load": load,
        "sys_uptime": int(sys_uptime),
        "app_uptime": int(time.time() - START_TIME),
        "python": ".".join(map(str, _sys.version_info[:3])),
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(START_TIME)),
    }


def random_quote():
    """优先取 hitokoto 接口（更多样），失败则用本地 105 句。"""
    try:
        req = urllib.request.Request(
            "https://v1.hitokoto.cn/?encode=json",
            headers={"User-Agent": "Mozilla/5.0 (XbfhmSite)"},
        )
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = (data.get("hitokoto") or "").strip()
        if text:
            src = data.get("from_who") or ""
            frm = data.get("from") or ""
            source = (src + " · " + frm).strip(" ·") if (src or frm) else ""
            return {"quote": text, "source": source, "api": True}
    except Exception:
        pass
    return {"quote": random.choice(QUOTES), "source": "", "api": False}


def add_message(name, content):
    name = re.sub(r"<[^>]*>", "", name).strip()[:20] or "匿名"
    content = re.sub(r"<[^>]*>", "", content).strip()[:500]
    if not content:
        return None
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO messages(name, content, ts) VALUES(?, ?, ?)",
        (name, content, int(time.time())),
    )
    conn.commit()
    mid = cur.lastrowid
    conn.close()
    return {
        "id": mid,
        "name": name,
        "content": content,
        "ts": int(time.time()),
    }


def list_messages(limit=50):
    conn = get_db()
    rows = conn.execute(
        "SELECT id, name, content, ts FROM messages ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "content": r["content"],
            "ts": r["ts"],
            "time": time.strftime("%m-%d %H:%M", time.localtime(r["ts"])),
        }
        for r in rows
    ]


def do_click(ip):
    h = ip_hash(ip)
    now = time.time()
    if h in _click_last and (now - _click_last[h]) < CLICK_COOLDOWN:
        return {"ok": False, "msg": "点太快啦，歇一下~", **stats()}
    _click_last[h] = now
    conn = get_db()
    conn.execute("UPDATE counter SET clicks = clicks + 1 WHERE id = 1")
    conn.commit()
    clicks = conn.execute("SELECT clicks FROM counter WHERE id = 1").fetchone()["clicks"]
    conn.close()
    return {"ok": True, "clicks": clicks, **stats()}


class Handler(BaseHTTPRequestHandler):
    server_version = "XbfhmSite/1.0"

    def _client_ip(self):
        fwd = self.headers.get("X-Forwarded-For")
        if fwd:
            return fwd.split(",")[0].strip()
        return self.client_address[0]

    def _send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, relpath):
        full = os.path.normpath(os.path.join(BASE_DIR, relpath))
        if not full.startswith(BASE_DIR) or not os.path.isfile(full):
            self._send_json({"error": "not found"}, 404)
            return
        ext = os.path.splitext(full)[1].lower()
        ctype = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".ico": "image/x-icon",
            ".svg": "image/svg+xml",
            ".json": "application/json; charset=utf-8",
            ".apk": "application/vnd.android.package-archive",
        }.get(ext, "application/octet-stream")
        with open(full, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "public, max-age=3600")
        self.end_headers()
        self.wfile.write(body)

    def _handle_api(self, path):
        record_visit(self._client_ip())

        if path == "/api/stats":
            return self._send_json(stats())
        if path == "/api/visit":
            return self._send_json(stats())
        if path == "/api/quote":
            return self._send_json(random_quote())
        if path == "/api/locations":
            return self._send_json(locations())
        if path == "/api/status":
            return self._send_json(server_status())
        if path == "/api/messages":
            if self.command == "POST":
                try:
                    ln = int(self.headers.get("Content-Length", 0))
                    data = json.loads(self.rfile.read(ln).decode("utf-8") or "{}")
                    name = str(data.get("name", "") or "")
                    content = str(data.get("content", "") or "")
                    msg = add_message(name, content)
                    if msg is None:
                        return self._send_json({"ok": False, "msg": "内容不能为空"}, 400)
                    return self._send_json({"ok": True, "message": msg})
                except Exception as e:
                    return self._send_json({"ok": False, "msg": str(e)}, 400)
            limit = min(int(parse_qs(urlparse(self.path).query).get("limit", ["50"])[0]), 200)
            return self._send_json({"ok": True, "messages": list_messages(limit)})
        if path == "/api/click":
            if self.command != "POST":
                return self._send_json({"ok": False, "msg": "POST only"}, 405)
            return self._send_json(do_click(self._client_ip()))
        return None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/"):
            r = self._handle_api(path)
            if r is not None:
                return
            return self._send_json({"error": "api not found"}, 404)
        if path == "/":
            path = "/index.html"
        return self._send_file(path.lstrip("/"))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/"):
            r = self._handle_api(path)
            if r is not None:
                return
        return self._send_json({"error": "not found"}, 404)

    def log_message(self, fmt, *args):
        pass


def main():
    init_db()
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"[xbfhm-site] serving on http://{HOST}:{PORT}  db={DB_PATH}  quotes={len(QUOTES)}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
