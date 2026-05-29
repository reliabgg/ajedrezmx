#!/usr/bin/env python3
"""
Servidor LAN para AjedrezMX: sirve los archivos estáticos (igual que
`python3 -m http.server`) y además ofrece un mini-servicio de señalización
para emparejar a los dos jugadores por WebRTC SIN copiar/pegar SDP a mano.

Solo usa la biblioteca estándar de Python (no instala nada).

Uso:
    python3 chess-lan-server.py                 # escucha en 0.0.0.0:8000 (toda la LAN)
    python3 chess-lan-server.py --port 9000
    python3 chess-lan-server.py --host 127.0.0.1  # solo local (p. ej. tras un túnel SSH)

Cómo juegan dos personas en la misma red:
    1. El anfitrión corre este script y abre http://localhost:PORT
       (o http://SU-IP-LAN:PORT). En 📡 LAN elige "Crear sala" y obtiene un código.
    2. El invitado abre http://IP-DEL-ANFITRION:PORT en su navegador, elige
       "Unirse a sala" y escribe ese código. La conexión se establece sola.

Seguridad: el emparejamiento solo transporta el "saludo" WebRTC (SDP). Las
jugadas viajan cifradas de extremo a extremo por el canal WebRTC (DTLS), no
por este servidor. Aun así, NO expongas este puerto a internet: úsalo solo en
tu red local de confianza.

Señalización (HTTP, JSON):
    GET  /lan/ping                  -> {"ok": true}
    POST /lan/offer  {room, sdp}    -> guarda la oferta del anfitrión
    GET  /lan/offer?room=CODE       -> {"sdp": ...} | 404 si no existe
    POST /lan/answer {room, sdp}    -> guarda la respuesta del invitado
    GET  /lan/answer?room=CODE      -> {"sdp": ...} | {} si aún no hay
Las salas expiran solas tras 10 minutos de inactividad.
"""

import argparse
import functools
import json
import os
import threading
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROOMS = {}
LOCK = threading.Lock()
ROOM_TTL = 600  # segundos


def _cleanup(now):
    stale = [k for k, v in ROOMS.items() if now - v["ts"] > ROOM_TTL]
    for k in stale:
        del ROOMS[k]


class Handler(SimpleHTTPRequestHandler):
    def _json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return None
        if length <= 0 or length > 500000:
            return None
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return None

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/lan/ping":
            return self._json(200, {"ok": True})
        if path in ("/lan/offer", "/lan/answer"):
            room = (parse_qs(urlparse(self.path).query).get("room") or [""])[0]
            key = "offer" if path == "/lan/offer" else "answer"
            now = time.time()
            with LOCK:
                _cleanup(now)
                r = ROOMS.get(room)
                if r and r.get(key):
                    return self._json(200, {"sdp": r[key]})
            # La oferta ausente = 404 (la sala no existe aún); la respuesta
            # ausente = 200 {} (la sala existe, el invitado aún no contestó).
            return self._json(404 if key == "offer" else 200, {})
        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path in ("/lan/offer", "/lan/answer"):
            data = self._read_json()
            if not data or "room" not in data or "sdp" not in data:
                return self._json(400, {"ok": False})
            room = str(data["room"])[:16]
            now = time.time()
            with LOCK:
                _cleanup(now)
                r = ROOMS.setdefault(room, {"offer": None, "answer": None, "ts": now})
                r["ts"] = now
                if path == "/lan/offer":
                    r["offer"] = data["sdp"]
                    r["answer"] = None  # nueva oferta invalida respuestas viejas
                else:
                    r["answer"] = data["sdp"]
            return self._json(200, {"ok": True})
        self.send_error(404)

    def log_message(self, fmt, *args):
        # Silencioso para no ensuciar la consola; las jugadas no pasan por aquí.
        pass


def _local_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description="Servidor LAN de AjedrezMX (sirve + señaliza WebRTC).")
    ap.add_argument("--host", default="0.0.0.0", help="interfaz a escuchar (0.0.0.0 = toda la LAN; 127.0.0.1 = solo local)")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--dir", default=os.path.dirname(os.path.abspath(__file__)), help="carpeta a servir (por defecto, la del script)")
    args = ap.parse_args()

    handler = functools.partial(Handler, directory=args.dir)
    httpd = ThreadingHTTPServer((args.host, args.port), handler)

    print("AjedrezMX — servidor LAN")
    print("  Sirviendo: %s" % args.dir)
    print("  Escuchando en %s:%d" % (args.host, args.port))
    print("  Local:  http://localhost:%d" % args.port)
    ip = _local_ip()
    if ip and args.host != "127.0.0.1":
        print("  En tu red LAN (compártelo con tu rival): http://%s:%d" % (ip, args.port))
    print("  (No expongas este puerto a internet — úsalo solo en tu red local.)")
    print("  Ctrl+C para detener.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDetenido.")
        httpd.server_close()


if __name__ == "__main__":
    main()
