import os

class Config:
    # Configuracion de TMDB
    # VALIDACION: [Issue #2] SEGURIDAD: Se elimina la API key hardcodeada para evitar fugas de credenciales.
    # Ahora se lee de variables de entorno, lo que permite rotar claves sin tocar el código.
    # VALIDACION: [Issue #2] LECTURA DE VARIABLE DE ENTORNO [VAR-01]: 'os.getenv' busca en el sistema operativo.
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    if not TMDB_API_KEY:
        # Fallo controlado: El servicio no debe arrancar si falta una credencial crítica.
        print("ERROR: La variable de entorno TMDB_API_KEY no está definida.")
        sys.exit(1)
    BASE_URL = "https://api.themoviedb.org/3"
    
    # Rutas
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    
    # Archivos
    JSON_FILE = os.path.join(DATA_DIR, "films.json")
    CSV_FILE = os.path.join(DATA_DIR, "films.csv")
    
    # Ejecucion
    INTERVAL_MINUTES = int(os.getenv("INTERVAL_MINUTES", 10))

    @staticmethod
    def ensure_directories():
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
