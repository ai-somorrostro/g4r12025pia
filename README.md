# Proyecto RETO 1 - Sistema de Gestion de Peliculas

Este proyecto implementa un sistema completo de ingesta, almacenamiento y exposicion de datos de peliculas, utilizando una arquitectura de microservicios contenerizada con Docker.

## Funcionalidades

### 1. Scrapper (Extraccion de Datos)
- **Modulo de Extraccion**: Obtiene datos de peliculas de TMDB.
- **Almacenamiento**: Guarda los datos en formato JSON en `services/data/films.json`.
- **Logging**: Registra el proceso de extraccion en `services/logs/`.

### 2. API REST (FastAPI)
- **Endpoints CRUD**:
    - `GET /film-data`: Obtener todas las peliculas.
    - `GET /film/{title}`: Buscar pelicula por titulo.
    - `POST /film-data`: Crear nueva pelicula.
    - `PUT /film-data/{title}`: Actualizar pelicula.
    - `DELETE /film-data/{title}`: Eliminar pelicula.
- **Sincronizacion**: Endpoint `/sync-logstash` para enviar datos a ElasticSearch.
- **Documentacion**: Swagger UI disponible en `/docs`.
- **Logging**: Middleware para registrar todas las peticiones HTTP.

### 3. Almacenamiento y Busqueda (Elastic Stack)
- **Elasticsearch**: Motor de busqueda y analitica.
- **Logstash**: Pipeline de procesamiento de datos.

## Tecnologias
- **Lenguaje**: Python 3.9+
- **Framework Web**: FastAPI
- **Contenedores**: Docker & Docker Compose
- **Base de Datos**: Elasticsearch (NoSQL)

## Requisitos Previos
- Docker Desktop instalado y corriendo.
- Git.

## Instalacion y Despliegue

1.  **Clonar el repositorio**:
    ```bash
    git clone https://github.com/ai-somorrostro/g4r12025pia.git
    cd g4r12025pia
    ```

2.  **Iniciar los servicios**:
    ```bash
    docker-compose up -d --build
    ```

## Documentacion de la API
Una vez levantado el servicio, accede a la documentacion interactiva:
- **Swagger UI**: [http://localhost:8001/docs](http://localhost:8001/docs)

## Estructura del Proyecto
```
.
├── services/
│   ├── api/            # Servicio FastAPI
│   ├── scrapper/       # Servicio de extraccion de datos
│   ├── data/           # Volumen de datos (JSON)
│   ├── logs/           # Logs compartidos
│   └── logstash/       # Configuracion de Logstash
├── docker-compose.yml  # Orquestacion de contenedores
└── README.md           # Documentacion
```

## Contribucion
1.  Crear una rama para la nueva funcionalidad (`git checkout -b feature/nueva-funcionalidad`).
2.  Realizar cambios y commits descriptivos.
3.  Subir cambios y crear un Pull Request.
