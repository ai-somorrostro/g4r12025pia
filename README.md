# Informe de Benchmarking: Modelos de IA y Embeddings

Este anexo detalla los resultados de las pruebas de rendimiento y precisión realizadas para seleccionar los componentes críticos del Chatbot Híbrido.

## 1. Selección del Modelo LLM (Cerebro)

**Objetivo:** Evaluar la capacidad de los modelos para distinguir entre una búsqueda por **Trama/Sinopsis** (semántica) y una búsqueda de **Datos Estructurados** (API).

### Resultados del Test de Comprensión de Intención:

| Modelo | % Acierto Routing | Análisis |
| :--- | :--- | :--- |
| **GPT-4o Mini** | **100.0%** | **Seleccionado.** Distinción perfecta entre narrativa y datos técnicos. |
| **Gemini 2.5 Flash** | **98.0%** | Excelente alternativa, fallo marginal en casos muy ambiguos. |
| **Llama 3.1 8B** | **68.0%** | Rendimiento insuficiente. Confunde frecuentemente sinopsis con búsquedas de guion. |
| **Mistral 7B** | **46.0%** | No apto para producción. Aleatorio en la selección de herramientas. |

**Conclusión:**
La arquitectura requiere un enrutamiento preciso para no frustrar al usuario. **GPT-4o Mini** se establece como el estándar por su fiabilidad absoluta en la clasificación de intenciones, eliminando los falsos negativos en la recuperación de información.

---

## 2. Selección del Modelo de Embeddings (Motor de Búsqueda)

**Objetivo:** Encontrar el equilibrio entre la capacidad de recuperar el fragmento de guion correcto (Recall/Precisión) y la velocidad de respuesta (Latencia).

### Resultados del Trade-off (Precisión vs Velocidad):

*   **Distiluse:**
    *   **Latencia:** < 7ms (El más rápido).
    *   **Precisión:** ~82%.
    *   *Veredicto:* Excelente para entornos de recursos muy limitados, pero su comprensión multilingüe es básica.

*   **MiniLM-L12:**
    *   **Latencia:** ~11ms.
    *   **Precisión:** ~65%.
    *   *Veredicto:* **Descartado.** No ofrece suficiente precisión para justificar su uso frente a Distiluse.

*   **MPNet-Base (768 dims):**
    *   **Latencia:** ~12.5ms (El más lento).
    *   **Precisión Real:** **Superior en contextos complejos.**
    *   *Veredicto:* **Seleccionado.** Aunque en el gráfico sintético aparece con un 76% (debido a la dificultad de la traducción automática en el test), en pruebas cualitativas con guiones reales demostró la mejor capacidad para captar matices profundos y relaciones entre películas, justificando los milisegundos extra.

**Decisión Final:**
Se implementa **`paraphrase-multilingual-mpnet-base-v2`**. Su dimensionalidad de **768** permite una comprensión semántica "densa" que conecta preguntas en español con textos en inglés con mayor fidelidad conceptual que sus competidores más ligeros.
