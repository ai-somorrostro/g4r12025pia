# services/api/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from elasticsearch import Elasticsearch
import os
import logging
from datetime import datetime
import time

app = FastAPI(title="API de Peliculas", version="2.0")

# ===================== CONFIGURACIÓN =====================
# VALIDACION: [Issue #9] CAMBIO ESTRUCTURAL: Se sustituye 'films.json' por Elasticsearch como fuente de verdad.
# Esto garantiza que la API siempre lea los datos más recientes de forma segura y consistente.
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
ES_INDEX = os.getenv("ES_INDEX", "movies-logstash")

# Inicializar cliente oficial de Elasticsearch
es = Elasticsearch([ELASTICSEARCH_URL])

# Ruta de logs
if os.path.exists("/app/logs"):
    LOGS_DIR = "/app/logs"
else:
    LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))

os.makedirs(LOGS_DIR, exist_ok=True)

# Configurar logger
log_filename = os.path.join(LOGS_DIR, f"api_{datetime.now():%Y-%m-%d}.log")

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger = logging.getLogger("FilmAPI")
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

for log_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
    uvicorn_log = logging.getLogger(log_name)
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == log_filename for h in uvicorn_log.handlers):
        uvicorn_log.addHandler(file_handler)

# ===================== MIDDLEWARE DE LOGGING =====================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware que registra cada petición HTTP"""
    start_time = time.time()
    
    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    path = request.url.path
    
    logger.info(f"-> {method} {path} | IP: {client_ip}")
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        logger.info(f"<- {method} {path} | Status: {response.status_code} | {process_time:.2f}ms")
        
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(f"Error: {method} {path} | Error: {str(e)} | {process_time:.2f}ms")
        raise

# ===================== HELPERS =====================
def _check_es_connection():
    """Verifica la conexión con Elasticsearch"""
    if not es.ping():
        logger.error("No se puede conectar a Elasticsearch")
        raise HTTPException(status_code=503, detail="Elasticsearch no disponible")

def _search_all_films():
    """Busca todas las películas en Elasticsearch"""
    _check_es_connection()
    try:
        result = es.search(
            index=ES_INDEX,
            body={"query": {"match_all": {}}, "size": 10000},
        )
        return [hit["_source"] for hit in result["hits"]["hits"]]
    except Exception as e:
        logger.error(f"Error buscando películas en ES: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error consultando Elasticsearch: {str(e)}")

# ===================== ENDPOINTS =====================
@app.get("/health")
def health():
    """Endpoint de salud para verificar que la API funciona"""
    es_status = "connected" if es.ping() else "disconnected"
    logger.info(f"Health check ejecutado - ES: {es_status}")
    return {
        "status": "ok",
        "elasticsearch": es_status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/film-data")
def get_film_data():
    """Devuelve todas las películas desde Elasticsearch"""
    # VALIDACION: [Issue #9] CONSULTA DIRECTA: Al consultar la DB, eliminamos la necesidad de
    # volúmenes compartidos de Docker, haciendo el despliegue más limpio.
    films = _search_all_films()
    logger.info(f"Devolviendo {len(films)} películas")
    return {
        "total": len(films),
        "films": films
    }

@app.get("/film/{film_title}")
def get_film_by_title(film_title: str):
    """Obtiene una película específica por su título exacto"""
    _check_es_connection()
    
    try:
        result = es.search(
            index=ES_INDEX,
            body={
                "query": {
                    "term": {"title.keyword": film_title.strip()}
                }
            }
        )
        
        hits = result["hits"]["hits"]
        if not hits:
            # Fallback: búsqueda con match exacto en campo title
            result = es.search(
                index=ES_INDEX,
                body={
                    "query": {
                        "match_phrase": {"title": film_title.strip()}
                    }
                }
            )
            hits = result["hits"]["hits"]
        
        if not hits:
            logger.warning(f"Película no encontrada: {film_title}")
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró ninguna película con el título: '{film_title}'"
            )
        
        logger.info(f"Película encontrada: {film_title}")
        return {
            "success": True,
            "film": hits[0]["_source"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error buscando película '{film_title}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al buscar la película: {str(e)}")

@app.post("/film-data")
def create_film(film_data: dict):
    """Crea/añade una nueva película al catálogo en Elasticsearch"""
    _check_es_connection()
    
    try:
        # Usar el campo 'id' como document_id si existe
        doc_id = film_data.get("id")
        
        if doc_id:
            # Verificar si ya existe
            if es.exists(index=ES_INDEX, id=str(doc_id)):
                logger.warning(f"Intento de crear película con ID duplicado: {doc_id}")
                raise HTTPException(
                    status_code=409,
                    detail=f"Ya existe una película con el ID: {doc_id}"
                )
        
        result = es.index(
            index=ES_INDEX,
            id=str(doc_id) if doc_id else None,
            document=film_data,
            refresh="wait_for"
        )
        
        logger.info(f"Película creada: {film_data.get('title', 'Sin título')} (ES ID: {result['_id']})")
        
        return {
            "success": True,
            "message": "Película creada correctamente",
            "created_film": film_data,
            "es_id": result["_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear película: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al crear la película: {str(e)}")

@app.put("/film-data/{film_title}")
def update_film(film_title: str, film_data: dict):
    """Actualiza los datos de una película por su título"""
    _check_es_connection()
    
    try:
        # Buscar la película por título
        result = es.search(
            index=ES_INDEX,
            body={
                "query": {
                    "match_phrase": {"title": film_title.strip()}
                }
            }
        )
        
        hits = result["hits"]["hits"]
        if not hits:
            logger.warning(f"Intento de actualizar película inexistente: {film_title}")
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró ninguna película con el título: '{film_title}'"
            )
        
        doc_id = hits[0]["_id"]
        es.update(
            index=ES_INDEX,
            id=doc_id,
            doc=film_data,
            refresh="wait_for"
        )
        
        # Obtener el documento actualizado
        updated = es.get(index=ES_INDEX, id=doc_id)
        
        logger.info(f"Película actualizada: {film_title}")
        
        return {
            "success": True,
            "message": f"Película '{film_title}' actualizada correctamente",
            "updated_film": updated["_source"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar película '{film_title}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar la película: {str(e)}")

@app.delete("/film-data/{film_title}")
def delete_film(film_title: str):
    """Elimina una película por nombre exacto"""
    _check_es_connection()
    
    try:
        # Buscar la película
        result = es.search(
            index=ES_INDEX,
            body={
                "query": {
                    "match_phrase": {"title": film_title.strip()}
                }
            }
        )
        
        hits = result["hits"]["hits"]
        if not hits:
            logger.warning(f"Intento de eliminar película inexistente: {film_title}")
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró ninguna película con el título: '{film_title}'"
            )
        
        # Eliminar todos los matches
        deleted_count = 0
        for hit in hits:
            es.delete(index=ES_INDEX, id=hit["_id"], refresh="wait_for")
            deleted_count += 1
        
        logger.info(f"Película eliminada: {film_title} ({deleted_count} eliminada(s))")
        
        return {
            "success": True,
            "message": f"Película '{film_title}' eliminada correctamente",
            "deleted_count": deleted_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar película '{film_title}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar la película: {str(e)}")