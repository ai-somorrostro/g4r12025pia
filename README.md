
## 🚀 Inicio Rápido

### 1. Levantar el sistema
```powershell
docker-compose up -d
```

### 2. Esperar inicialización (15-20 segundos)
```powershell
timeout /t 20
```

### 3. Ejecutar prueba automática
```powershell
.\test_sistema.ps1
```

---

## 📊 Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **FastAPI** | 8001 | API REST para CRUD de películas |
| **LLM Manager** | 8002 | Sistema RAG con Groq |
| **Logstash** | 8000 | Pipeline ETL |
| **Elasticsearch** | 9200 | Motor de búsqueda |
| **Scrapper** | - | Extractor de TMDB (cada 10 min) |

---

## 🎯 Endpoints Principales

### FastAPI (http://localhost:8001)
- `GET /health` - Health check
- `GET /film-data` - Obtener todas las películas
- `GET /film/{title}` - Buscar por título
- `POST /film-data` - Crear película
- `PUT /film-data/{title}` - Actualizar película
- `DELETE /film-data/{title}` - Eliminar película
- `POST /sync-logstash` - Sincronizar con Elasticsearch

### LLM Manager (http://localhost:8002)
- `GET /health` - Health check
- `POST /chat` - Consulta RAG (pregunta sobre películas)

---

## 💬 Ejemplo de Uso RAG

```powershell
# Crear consulta
@"
{
  "question": "¿Qué películas de acción me recomiendas?",
  "max_results": 5
}
"@ | Out-File query.json -Encoding utf8

# Enviar consulta
Invoke-WebRequest -Uri http://localhost:8002/chat -Method POST -InFile query.json -ContentType "application/json" -UseBasicParsing

# Limpiar
Remove-Item query.json
```

**Respuesta incluye:**
- Respuesta generada por LLM
- Fuentes (películas usadas)
- Métricas de tokens

---

## 📚 Documentación

- **[guia_pruebas.md](guia_pruebas.md)** - Guía completa de pruebas paso a paso
- **[funcionamiento_sistema.md](funcionamiento_sistema.md)** - Explicación técnica detallada
- **[reporte_verificacion.md](reporte_verificacion.md)** - Último reporte de pruebas
- **[cheat_sheet.md](cheat_sheet.md)** - Comandos rápidos

---

## 🔧 Comandos Útiles

```powershell
# Ver estado
docker-compose ps

# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Detener
docker-compose down

# Prueba completa
.\test_sistema.ps1
```

---

## 📝 Logs

Los logs se guardan en `services/logs/`:
- `api_YYYY-MM-DD.log` - Logs de FastAPI
- `llm_manager_YYYY-MM-DD.log` - Logs de LLM Manager
- `tokens_YYYY-MM-DD.log` - Registro de uso de tokens (JSON)
- `tmdb_scraper_YYYY-MM-DD.log` - Logs del scrapper

---

## 🛠️ Tecnologías

- **Python 3.11** - Backend
- **FastAPI** - Framework web
- **Elasticsearch 8.12** - Motor de búsqueda
- **Logstash 8.12** - Pipeline ETL
- **Groq API** - LLM (llama-3.3-70b-versatile)
- **Docker** - Containerización
- **TMDB API** - Fuente de datos

---

## ✅ Verificación Rápida

```powershell
# Health checks
Invoke-WebRequest http://localhost:8001/health -UseBasicParsing
Invoke-WebRequest http://localhost:8002/health -UseBasicParsing
Invoke-WebRequest http://localhost:9200/_cluster/health -UseBasicParsing
```

---

## 🎓 Conceptos Clave

### RAG (Retrieval-Augmented Generation)
1. **Retrieval**: Busca películas relevantes en Elasticsearch
2. **Augmented**: Añade contexto al prompt del LLM
3. **Generation**: LLM genera respuesta basada en datos reales

### Ventajas
- ✅ Respuestas basadas en datos actuales
- ✅ Reduce alucinaciones del LLM
- ✅ Fuentes verificables
- ✅ No requiere reentrenar el modelo

---

## 📊 Datos

- **Fuente**: TMDB API
- **Categorías**: Trending, Estrenos, Más votadas, Top rated
- **Actualización**: Cada 10 minutos (scrapper)
- **Formato**: JSON y CSV

---

## 🆘 Soporte

Si algo no funciona:
1. Revisa logs: `docker-compose logs [servicio]`
2. Verifica puertos: `docker-compose ps`
3. Reinicia: `docker-compose restart`
4. Consulta: `guia_pruebas.md` sección Troubleshooting

---

## 📄 Licencia

Proyecto educativo - IABD4 RETO 1

---

**¡Sistema listo para usar! 🚀**

Para empezar: `docker-compose up -d` → `.\test_sistema.ps1`
