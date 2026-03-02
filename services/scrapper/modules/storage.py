import json
import os
import pandas as pd
from config import Config
from elasticsearch import Elasticsearch, helpers

class StorageManager:
    def __init__(self, logger):
        self.log = logger
        # VALIDACION: [Issue #9] LECTURA DE VARIABLE DE ENTORNO [VAR-02]: URL de Elasticsearch.
        self.es_url = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
        self.es_index = os.getenv("ES_INDEX", "movies-logstash")
        self.es = Elasticsearch([self.es_url])

    def save_data(self, movies):
        """Guarda los datos en múltiples formatos y destinos"""
        self.save_json(movies)
        self.save_csv(movies)
        self.save_to_elasticsearch(movies)

    def save_to_elasticsearch(self, movies):
        """
        [Issue #9] Indexa los datos directamente en Elasticsearch.
        VALIDACION: [Issue #9] PERSISTENCIA DISTRIBUIDA: Usamos 'helpers.bulk' para una ingesta eficiente.
        Esto permite que la API consulte los datos sin depender de archivos compartidos.
        """
        try:
            if not self.es.ping():
                self.log.error("Elasticsearch no disponible para indexación")
                return

            actions = [
                {
                    "_index": self.es_index,
                    "_id": movie.get("id"),
                    "_source": movie
                }
                for movie in movies
            ]
            
            success, _ = helpers.bulk(self.es, actions, refresh=True)
            self.log.info(f"Indexación exitosa en ES: {success} películas subidas")
        except Exception as e:
            self.log.error(f"Error indexando en Elasticsearch: {e}")

    def save_json(self, movies):
        """Guarda en archivo JSON (Backup local)"""
        try:
            with open(Config.JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(movies, f, ensure_ascii=False, indent=2)
            self.log.info(f"JSON guardado: {Config.JSON_FILE}")
        except Exception as e:
            self.log.error(f"Error guardando JSON: {e}")

    def save_csv(self, movies):
        """Guarda en archivo CSV usando pandas (Backup local y Logstash)"""
        try:
            df = pd.DataFrame(movies)
            df.to_csv(Config.CSV_FILE, index=False, encoding='utf-8')
            self.log.info(f"CSV guardado: {Config.CSV_FILE}")
        except Exception as e:
            self.log.error(f"Error guardando CSV: {e}")
