from waitress import serve
from lipad_backend import wsgi

if __name__ == "__main__":
    serve(wsgi.application, host="127.0.0.1", port=8000, threads=8)
