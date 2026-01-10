from http.server import SimpleHTTPRequestHandler
import socketserver
from pathlib import Path
from functools import partial

HOST = "127.0.0.1"
PORT = 8000

# Servir siempre desde la carpeta del script
WEB_DIR = Path(__file__).parent.resolve()

class SilentThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    # Suprimir el volcado de tracebacks cuando el cliente cierra la conexión
    def handle_error(self, request, client_address):
        return

Handler = partial(SimpleHTTPRequestHandler, directory=str(WEB_DIR))

if __name__ == '__main__':
    with SilentThreadingTCPServer((HOST, PORT), Handler) as httpd:
        print(f"Escuchando en http://{HOST}:{PORT} (presiona Ctrl+C para detener)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Servidor detenido")
