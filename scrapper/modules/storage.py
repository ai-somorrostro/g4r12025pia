import json
import pandas as pd
from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure
from config import Config

class StorageManager:
    def __init__(self, logger):
        self.log = logger
        self.mongo_client = None
        self.db = None
        self.collection = None
        self._connect_mongo()

    def _connect_mongo(self):
        """Establece conexión con MongoDB"""
        try:
            self.mongo_client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
            # Verificar conexión
            self.mongo_client.admin.command('ping')
            self.db = self.mongo_client[Config.DB_NAME]
            self.collection = self.db[Config.COLLECTION_NAME]
            
            # Crear índices
            self.collection.create_index("id", unique=True)
            self.collection.create_index("title")
            self.collection.create_index("release_date")
            
            self.log.success(f"Conectado a MongoDB: {Config.MONGO_URI}")
        except Exception as e:
            self.log.error(f"No se pudo conectar a MongoDB: {e}")
            self.mongo_client = None

    def save_data(self, movies):
        """Guarda los datos en todos los formatos configurados"""
        self.save_json(movies)
        self.save_csv(movies)
        self.save_to_mongo(movies)

    def save_json(self, movies):
        """Guarda en archivo JSON"""
        try:
            with open(Config.JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(movies, f, ensure_ascii=False, indent=2)
            self.log.info(f"JSON guardado: {Config.JSON_FILE}")
        except Exception as e:
            self.log.error(f"Error guardando JSON: {e}")

    def save_csv(self, movies):
        """Guarda en archivo CSV usando pandas"""
        try:
            df = pd.DataFrame(movies)
            # Seleccionar columnas relevantes si es necesario, o guardar todo
            df.to_csv(Config.CSV_FILE, index=False, encoding='utf-8')
            self.log.info(f"CSV guardado: {Config.CSV_FILE}")
        except Exception as e:
            self.log.error(f"Error guardando CSV: {e}")

    def save_to_mongo(self, movies):
        """Guarda/Actualiza en MongoDB usando bulk operations"""
        if not self.collection:
            self.log.warning("MongoDB no disponible, saltando guardado en DB")
            return

        try:
            operations = []
            for movie in movies:
                # UpdateOne con upsert=True: si existe actualiza, si no crea
                operations.append(
                    UpdateOne(
                        {"id": movie["id"]},
                        {"$set": movie},
                        upsert=True
                    )
                )
            
            if operations:
                result = self.collection.bulk_write(operations)
                self.log.success(f"MongoDB Sync: {result.upserted_count} insertados, {result.modified_count} actualizados")
        except Exception as e:
            self.log.error(f"Error sincronizando con MongoDB: {e}")
