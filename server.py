import json, os, mimetypes, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
BASE=os.path.dirname(os.path.abspath(__file__)); PUBLIC=os.path.join(BASE,"public"); DATA_FILE=os.path.join(BASE,"data.json"); LOCK=threading.Lock(); DB_URL=os.environ.get("DATABASE_URL",""); _pg=None
def pg_conn():
    global _pg
    if _pg is None:
        import psycopg2
        _pg=psycopg2.connect(DB_URL.replace("postgres://","postgresql://",1), sslmode="require", connect_timeout=10); _pg.autocommit=True
        with _pg.cursor() as c:
            c.execute("CREATE TABLE IF NOT EXISTS shop (id INT PRIMARY KEY, data JSONB NOT NULL)")
            c.execute("INSERT INTO shop (id, data) VALUES (1, '{}'::jsonb) ON CONFLICT (id) DO NOTHING")
    return _pg
def _normalize(d):
    if not isinstance(d,dict): d={}
    for k,v in [("products",[]),("settings",{}),("ads",{}),("banners",[]),("categories",[]),("locations",[]),("chats",[]),("users",[]),("payments",[]),("broadcasts",[])]: d.setdefault(k,v)
    return d
def load():
    if DB_URL:
        try:
            with pg_conn().cursor() as c:
                c.execute("SELECT data FROM shop WHERE id=1"); row=c.fetchone(); return _normalize(row[0] if row else {})
        except Exception:
            global _pg; _pg=None
            with pg_conn().cursor() as c:
                c.execute("SELECT data FROM shop WHERE id=1"); row=c.fetchone(); return _normalize(row[0] if row else {})
    try:
        with open(DATA_FILE) as f: return _normalize(json.load(f))
    except Exception: return _normalize({})
def save(data):
    data=_normalize(data)
    if DB_URL:
        with pg_conn().cursor() as c: c.execute("INSERT INTO shop (id, data) VALUES (1, %s) ON CONFLICT (id) DO UPDATE SET data=EXCLUDED.data", [json.dumps(data)])
        return
    tmp=DATA_FILE+".tmp"
    with open(tmp,"w") as f: json.dump(data,f)
    os.replace(tmp,DATA_FILE)
class H(SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
    def _send(self,code,obj):
        b=json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(b))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u=urlparse(self.path).path
        if u in ("/api/shop","/api/shop/"):
            try: return self._send(200, load())
            except Exception as e: return self._send(500, {"error": str(e)[:200]})
        if u in ("/api/health","/health"):
            try: d=load(); return self._send(200, {"ok":True,"storage":"postgres" if DB_URL else "local-file","products":len(d.get("products") or [])})
            except Exception as e: return self._send(500, {"ok":False,"error":str(e)[:200]})
        if u=="/": u="/index.html"
        fp=None
        for root in (PUBLIC, BASE):
            _fp=os.path.normpath(os.path.join(root,u.lstrip("/")))
            if _fp.startswith(root) and os.path.isfile(_fp): fp=_fp; break
        if fp is None: fp=os.path.join(PUBLIC,"index.html")
        mt,_=mimetypes.guess_type(fp); mt=mt or "application/octet-stream"
        with open(fp,"rb") as f: data=f.read()
        self.send_response(200); self.send_header("Content-Type",mt); self.send_header("Cache-Control","no-store" if fp.endswith(".html") else "public, max-age=3600"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_PUT(self): self._write()
    def do_POST(self): self._write()
    def _write(self):
        u=urlparse(self.path).path
        if u not in ("/api/shop","/api/shop/"): return self._send(404,{"error":"not found"})
        n=int(self.headers.get("Content-Length") or 0); raw=self.rfile.read(n) if n else b"{}"
        try: data=json.loads(raw or b"{}")
        except Exception: return self._send(400,{"error":"invalid json"})
        if not isinstance(data,dict): return self._send(400,{"error":"shop must be an object"})
        with LOCK:
            cur=load()
            if isinstance(data.get("products"),list) and len(data["products"])==0 and isinstance(cur.get("products"),list) and len(cur["products"])>0 and not data.get("allowEmpty"):
                return self._send(409,{"error":"refusing to overwrite live shop with empty products","products":len(cur["products"])})
            save(data)
        return self._send(200,{"ok":True,"products":len(data.get("products") or [])})
if __name__=="__main__":
    port=int(os.environ.get("PORT","10000")); print("Storage:", "Postgres" if DB_URL else "local data.json", flush=True)
    ThreadingHTTPServer(("0.0.0.0",port),H).serve_forever()
