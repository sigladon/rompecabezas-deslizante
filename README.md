# 8-Puzzle Solver

Solucionador del problema del 8-Puzzle implementado en Python con cuatro algoritmos de búsqueda:

- **BFS** — Búsqueda en amplitud
- **IDDFS** — Búsqueda iterativa en profundidad
- **A\* (Fuera de lugar)** — Heurística: piezas fuera de su posición
- **A\* (Manhattan)** — Heurística: distancia Manhattan

Incluye una interfaz visual interactiva con **Streamlit** (`app.py`) y una ejecución por consola comparando todos los algoritmos (`main.py`).

## Estructura del proyecto

```
trabajo02/
├── algorithms.py       # BFS, IDDFS y A*
├── heuristics.py       # Funciones heurísticas
├── models.py           # Modelo del estado del puzzle
├── visualization.py    # Visualización con matplotlib/graphviz
├── app.py              # Interfaz web (Streamlit)
├── main.py             # Ejecución por consola
└── requirements.txt    # Dependencias
```

## Requisitos previos

- Python 3.8 o superior
- `pip`

## Configuración del entorno

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd trabajo02
```

### 2. Crear el entorno virtual

```bash
python -m venv .venv
```

### 3. Activar el entorno virtual

**Linux / macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Ejecución

### Interfaz web (Streamlit)

```bash
streamlit run app.py
```

### Comparación por consola

```bash
python main.py
```
