import streamlit as st
import time
import tracemalloc
import random
import os
from models import es_soluble
from algorithms import ejecutar_astar_puzzle, ejecutar_bfs, ejecutar_iddfs
import streamlit.components.v1 as components

st.set_page_config(layout="centered", page_title="Rompecabezas Deslizante", initial_sidebar_state="collapsed")

# --- UI/UX: Premium Light Mode (SaaS style, ui-ux-pro-max) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #0f172a;
    background-color: #f8fafc;
}

.stApp {
    background-color: #f8fafc;
}

header, #MainMenu, footer { visibility: hidden; }

h1 {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.02em;
    font-size: 2.5rem !important;
    text-align: center;
    margin-bottom: 2rem;
}

/* ── Buttons ── */
div.stButton > button,
div[data-testid="stButton"] > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05) !important;
    cursor: pointer !important;
    white-space: nowrap !important;
}

div.stButton > button:hover {
    background: #f8fafc !important;
    border-color: #94a3b8 !important;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05) !important;
    transform: translateY(-1px) !important;
}

div.stButton > button:active {
    transform: scale(0.98) !important;
    box-shadow: none !important;
}

/* Primary Button */
div.stButton > button[kind="primary"] {
    background: linear-gradient(180deg, #3b82f6, #2563eb) !important;
    color: #ffffff !important;
    border: 1px solid #1d4ed8 !important;
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
}

div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(180deg, #2563eb, #1d4ed8) !important;
    border-color: #1e40af !important;
    box-shadow: 0 6px 8px -1px rgba(37, 99, 235, 0.3) !important;
}

/* IconButton (Refresh) */
.icon-btn-container button {
    width: 60px !important;
    height: 60px !important;
    padding: 0 !important;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 16px !important;
    font-size: 1.5rem !important;
}


</style>
""", unsafe_allow_html=True)

def get_puzzle_builder_html(n=3):
    """Genera HTML interactivo para puzzle n×n dinámicamente."""
    cell_size = min(84, int(280 / n))  # Ajusta tamaño según n (max 84px)
    font_size = int(cell_size * 0.4)
    grid_cols = f"repeat({n}, {cell_size}px)"
    
    # Generar estilos de colores para todas las fichas hasta n²
    tile_styles = ""
    colors = [
        "#ef4444, #dc2626", "#f97316, #ea580c", "#f59e0b, #d97706", "#10b981, #059669",
        "#06b6d4, #0891b2", "#3b82f6, #2563eb", "#8b5cf6, #7c3aed", "#d946ef, #c026d3",
        "#ec4899, #db2777", "#6366f1, #4f46e5", "#14b8a6, #0d9488", "#f43f5e, #e11d48"
    ]
    
    borders = [
        "#b91c1c", "#c2410c", "#b45309", "#047857",
        "#0e7490", "#1d4ed8", "#6d28d9", "#a21caf",
        "#be185d", "#3730a3", "#0f766e", "#9d174d"
    ]
    
    for i in range(1, n * n):
        color_pair = colors[(i - 1) % len(colors)]
        border_color = borders[(i - 1) % len(borders)]
        tile_styles += f".tile-{i} {{ background: linear-gradient(135deg, {color_pair}); color: white; border: 1px solid {border_color}; text-shadow: 0 1px 2px rgba(0,0,0,0.2); }}\n        "
    
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background: transparent;
            margin: 0;
            padding: 20px;
            width: 100%;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        .grid {{
            display: grid;
            grid-template-columns: {grid_cols};
            gap: 10px;
            background: #ffffff;
            padding: 16px;
            border-radius: 18px;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
            border: 1px solid #e2e8f0;
            margin: 0 auto;
        }}
        .cell {{
            width: {cell_size}px; height: {cell_size}px;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-family: 'JetBrains Mono', monospace; font-size: {font_size}px; font-weight: 700;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            user-select: none;
            box-shadow: 0 2px 4px -1px rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        }}
        .cell:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        }}
        .cell:active {{ transform: scale(0.96); box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05); }}
        .cell.empty {{
            background: #f8fafc; box-shadow: inset 0 2px 4px 0 rgba(0,0,0,0.06); color: transparent; cursor: default; border: 1px solid #e2e8f0;
        }}
        .cell.empty:hover {{ transform: none; box-shadow: inset 0 2px 4px 0 rgba(0,0,0,0.06); }}
        
        {tile_styles}
    </style>
</head>
<body>
    <div class="grid" id="main-board"></div>
    <script>
        const GRID_SIZE = {n};
        let currentBoard = [];
        let currentResetKey = -1;
        
        function renderBoard() {{
            const boardEl = document.getElementById('main-board');
            boardEl.innerHTML = '';
            for (let i = 0; i < GRID_SIZE * GRID_SIZE; i++) {{
                const val = currentBoard[i];
                const cell = document.createElement('div');
                cell.innerText = val === 0 ? '' : val;
                cell.className = 'cell ' + (val === 0 ? 'empty' : 'tile-' + (val % GRID_SIZE * GRID_SIZE));
                cell.onclick = () => handleTileClick(i);
                boardEl.appendChild(cell);
            }}
        }}
        
        function handleTileClick(index) {{
            const emptyIndex = currentBoard.indexOf(0);
            const row = Math.floor(index / GRID_SIZE);
            const col = index % GRID_SIZE;
            const emptyRow = Math.floor(emptyIndex / GRID_SIZE);
            const emptyCol = emptyIndex % GRID_SIZE;
            const isAdjacent = (Math.abs(row - emptyRow) === 1 && col === emptyCol) || 
                               (Math.abs(col - emptyCol) === 1 && row === emptyRow);
            if (isAdjacent) {{
                const temp = currentBoard[index];
                currentBoard[index] = currentBoard[emptyIndex];
                currentBoard[emptyIndex] = temp;
                renderBoard();
                window.parent.postMessage({{ isStreamlitMessage: true, type: "streamlit:setComponentValue", value: currentBoard }}, "*");
            }}
        }}
        
        window.addEventListener("message", function(event) {{
            if (event.data.type === "streamlit:render") {{
                const args = event.data.args;
                if (args && args.board && args.reset_key !== currentResetKey) {{
                    currentResetKey = args.reset_key;
                    currentBoard = args.board.slice ? Array.from(args.board) : args.board;
                    renderBoard();
                }}
            }}
        }});
        
        window.addEventListener("load", function() {{
            window.parent.postMessage({{ isStreamlitMessage: true, type: "streamlit:componentReady", apiVersion: 1 }}, "*");
            window.parent.postMessage({{ isStreamlitMessage: true, type: "streamlit:setFrameHeight", height: {cell_size * n + 70} }}, "*");
        }});
    </script>
</body>
</html>
"""

def format_memory(bytes_val):
    """Convierte bytes a KB, MB o GB de forma legible."""
    kb = bytes_val / 1024
    if kb < 1024:
        return f"{kb:.1f} KB"
    else:
        mb = kb / 1024
        if mb < 1024:
            return f"{mb:.1f} MB"
        else:
            gb = mb / 1024
            return f"{gb:.2f} GB"

def get_static_board_html(board, n=3):
    cells_html = ""
    # Ajustar tamaño de celda según el número de columnas
    cell_size = min(90, 360 // n)  # Máximo 90px, mínimo según fit en 360px
    for val in board:
        if val == 0:
            cells_html += f"<div class='cell empty'></div>"
        else:
            cells_html += f"<div class='cell tile-{val % 9}'>{val}</div>"
            
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@600;700&display=swap" rel="stylesheet">
        <style>
            body {{ background: transparent; margin: 0; padding: 10px; display: flex; flex-direction: column; align-items: center; width: 100%; box-sizing: border-box; }}
            .grid {{
                display: grid; grid-template-columns: repeat({n}, {cell_size}px); gap: 8px;
                background: #ffffff; padding: 12px; border-radius: 16px;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
                border: 1px solid #e2e8f0;
            }}
            .cell {{
                width: {cell_size}px; height: {cell_size}px;
                border-radius: 10px;
                display: flex; align-items: center; justify-content: center;
                font-family: 'JetBrains Mono', monospace; font-size: {cell_size // 3}px; font-weight: 700;
                box-shadow: 0 2px 4px -1px rgb(0 0 0 / 0.1);
            }}
            .cell.empty {{ background: #f8fafc; box-shadow: inset 0 2px 4px 0 rgba(0,0,0,0.06); color: transparent; border: 1px solid #e2e8f0; }}
            .tile-1 {{ background: linear-gradient(135deg, #ef4444, #dc2626); color: white; border: 1px solid #b91c1c; }}
            .tile-2 {{ background: linear-gradient(135deg, #f97316, #ea580c); color: white; border: 1px solid #c2410c; }}
            .tile-3 {{ background: linear-gradient(135deg, #f59e0b, #d97706); color: white; border: 1px solid #b45309; }}
            .tile-4 {{ background: linear-gradient(135deg, #10b981, #059669); color: white; border: 1px solid #047857; }}
            .tile-5 {{ background: linear-gradient(135deg, #06b6d4, #0891b2); color: white; border: 1px solid #0e7490; }}
            .tile-6 {{ background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; border: 1px solid #1d4ed8; }}
            .tile-7 {{ background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: white; border: 1px solid #6d28d9; }}
            .tile-8 {{ background: linear-gradient(135deg, #d946ef, #c026d3); color: white; border: 1px solid #a21caf; }}
            .tile-0 {{ background: linear-gradient(135deg, #ec4899, #db2777); color: white; border: 1px solid #be185d; }}
        </style>
    </head>
    <body>
        <div class="grid">{cells_html}</div>
    </body>
    </html>
    """

# Inicializar componente puzzle
def get_puzzle_builder_component(n=3):
    """Crea o reutiliza un componente de puzzle aislado por tamaño.

    Separar el componente por tamaño evita que Streamlit conserve el iframe
    anterior con el HTML de 3x3 cuando se cambia a 4x4 o 5x5.
    """
    component_dir = os.path.join(os.path.dirname(__file__), f"puzzle_component_{n}")
    os.makedirs(component_dir, exist_ok=True)

    puzzle_html = get_puzzle_builder_html(n)
    with open(os.path.join(component_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(puzzle_html)

    return components.declare_component(f"puzzle_builder_{n}", path=component_dir)

# Inicializar componente tabla de resultados
results_dir = os.path.join(os.path.dirname(__file__), "results_component")
os.makedirs(results_dir, exist_ok=True)
# Placeholder inicial
_placeholder_html = "<!DOCTYPE html><html><body style='margin:0'></body></html>"
if not os.path.exists(os.path.join(results_dir, "index.html")):
    with open(os.path.join(results_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(_placeholder_html)

results_table_component = components.declare_component("results_table", path=results_dir)

def build_results_table_html(resultados):
    """Genera el HTML con CSS Grid para la tabla de resultados."""
    header_row = """
        <div class='cell hdr'>Algoritmo</div>
        <div class='cell hdr'>Tiempo</div>
        <div class='cell hdr'>Memoria</div>
        <div class='cell hdr nodos'>Nodos<br>explorados</div>
        <div class='cell hdr'>Pasos</div>
        <div class='cell hdr'></div>
    """
    data_rows = ""
    for res in resultados:
        algo_safe = res['algoritmo'].replace("'", "\\'")
        data_rows += f"""
        <div class='cell name'>{res['algoritmo']}</div>
        <div class='cell mono'>{res['tiempo']:.3f}s</div>
        <div class='cell mono'>{res['memoria']}</div>
        <div class='cell mono'>{res['nodos']}</div>
        <div class='cell mono'>{res['pasos']}</div>
        <div class='cell action'><button class='btn' onclick="selectAlgo('{algo_safe}')">Resolución</button></div>
        """
    num_rows = len(resultados)
    # header ~46px + each row ~53px + small buffer
    total_h = 46 + num_rows * 53 + 16

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{
      font-family: 'Inter', sans-serif;
      background: transparent;
      margin: 0;
      padding: 0;
      display: flex;
      justify-content: center;
      align-items: flex-start;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(6, max-content);
      width: max-content;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      overflow: hidden;
    }}
    .cell {{
      padding: 0.7rem 1rem;
      border-bottom: 1px solid #f1f5f9;
      word-break: keep-all;
      overflow-wrap: normal;
    }}
    .grid > .cell:nth-last-child(-n+6) {{
      border-bottom: none;
    }}
    .cell.hdr {{
      font-size: 0.75rem;
      font-weight: 700;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      background: #f8fafc;
      border-bottom: 2px solid #e2e8f0 !important;
      white-space: nowrap;
    }}
    .cell.nodos {{
      white-space: normal;
      text-align: center;
      line-height: 1.3;
    }}
    .cell.name {{
      font-weight: 600;
      color: #0f172a;
      word-break: keep-all;
    }}
    .cell.mono {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.88rem;
      color: #334155;
      white-space: nowrap;
    }}
    .cell.action {{
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .btn {{
      font-family: 'Inter', sans-serif;
      font-size: 0.82rem;
      font-weight: 600;
      padding: 0.35rem 0.8rem;
      background: #ffffff;
      color: #0f172a;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }}
    .btn:hover {{
      background: #f1f5f9;
      border-color: #94a3b8;
    }}
    .btn:active {{
      transform: scale(0.97);
    }}
  </style>
</head>
<body>
  <div class="grid">
    {header_row}
    {data_rows}
  </div>
  <script>
    function selectAlgo(name) {{
      window.parent.postMessage({{
        isStreamlitMessage: true,
        type: "streamlit:setComponentValue",
        value: name
      }}, "*");
    }}
    window.addEventListener("load", function() {{
      window.parent.postMessage({{isStreamlitMessage: true, type: "streamlit:componentReady", apiVersion: 1}}, "*");
      setTimeout(function() {{
        var h = document.body.scrollHeight;
        window.parent.postMessage({{isStreamlitMessage: true, type: "streamlit:setFrameHeight", height: h + 8}}, "*");
      }}, 120);
    }});
  </script>
</body>
</html>"""


# --- CABECERA ---
st.markdown("<h1>Rompecabezas Deslizante</h1>", unsafe_allow_html=True)
# --- ESTADO INICIAL ---
if 'board' not in st.session_state:
    st.session_state.board = (1, 2, 3, 4, 5, 6, 7, 8, 0)
if 'board_size' not in st.session_state:
    st.session_state.board_size = 3
if 'reset_key' not in st.session_state:
    st.session_state.reset_key = 0
if 'resultados' not in st.session_state:
    st.session_state.resultados = None

# Generar meta según el tamaño
n = st.session_state.board_size
meta = tuple(range(1, n*n)) + (0,)

# --- LAYOUT PRINCIPAL ---
col_left, col_mid, col_right = st.columns([1, 2, 1])

with col_mid:
    # Selector de tamaño
    st.markdown("<div style='text-align:center; margin-bottom:1.5rem;'>", unsafe_allow_html=True)
    new_size = st.radio("Tamaño del tablero", [3, 4, 5], horizontal=True, label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    # Componente del puzzle para el tamaño actual
    puzzle_builder_component = get_puzzle_builder_component(st.session_state.board_size)
    
    # Si cambió el tamaño, generar nuevo tablero
    if new_size != st.session_state.board_size:
        st.session_state.board_size = new_size
        st.session_state.reset_key += 1
        st.session_state.resultados = None
        
        # Generar nuevo tablero del tamaño correcto
        n_squared = new_size * new_size
        while True:
            nuevo = list(range(n_squared))
            random.shuffle(nuevo)
            if es_soluble(tuple(nuevo), new_size):
                st.session_state.board = tuple(nuevo)
                break
        st.rerun()
    
    # Rompecabezas Interactivo
    board_res = puzzle_builder_component(
        board=st.session_state.board,
        reset_key=st.session_state.reset_key,
        key=f"puzzle_builder_{st.session_state.board_size}"
    )
    if board_res and tuple(board_res) != st.session_state.board:
        st.session_state.board = tuple(board_res)
        st.session_state.resultados = None # Limpiar si cambia

    # Botón de recargar centrado bajo el tablero
    st.markdown("<div style='display:flex; justify-content:center; margin-top:0.5rem;'>", unsafe_allow_html=True)
    if st.button("Generar nuevo rompecabezas", use_container_width=True):
        st.session_state.reset_key += 1
        st.session_state.resultados = None
        n_squared = st.session_state.board_size ** 2
        while True:
            nuevo = list(range(n_squared))
            random.shuffle(nuevo)
            if es_soluble(tuple(nuevo), st.session_state.board_size):
                st.session_state.board = tuple(nuevo)
                break
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Botón Resolver
st.markdown("<div style='max-width:300px; margin: 0 auto; margin-top:2rem;'>", unsafe_allow_html=True)
if st.button("Resolver", type="primary", use_container_width=True):
    n = st.session_state.board_size
    if not es_soluble(st.session_state.board, n):
        st.error("El estado actual no es soluble.")
    else:
        st.session_state.resultados = []
        # Configuración de algoritmos a ejecutar
        algoritmos = [
            ("BFS", ejecutar_bfs, [st.session_state.board, meta, n]),
            ("IDDFS", ejecutar_iddfs, [st.session_state.board, meta, 30, n]),
            ("A* Fuera de lugar", ejecutar_astar_puzzle, [st.session_state.board, meta, "fuera_lugar", n]),
            ("A* Manhattan", ejecutar_astar_puzzle, [st.session_state.board, meta, "manhattan", n])
        ]
        
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        for idx, (nombre, func, args) in enumerate(algoritmos):
            progress_text.text(f"Ejecutando {nombre}...")
            tracemalloc.start()
            start_time = time.time()
            
            res = func(*args)
            
            end_time = time.time()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            if res and res[0] is not None:
                # Normalizar output si es IDDFS que tiene distinto output
                if nombre == "IDDFS":
                    movs, tableros, nodos_arr, prof, arbol = res
                    nodos = sum(nodos_arr) if isinstance(nodos_arr, list) else nodos_arr
                else:
                    movs, tableros, nodos, costo, arbol = res
                    
                st.session_state.resultados.append({
                    "algoritmo": nombre,
                    "tiempo": end_time - start_time,
                    "memoria": format_memory(peak),
                    "nodos": nodos,
                    "pasos": len(movs),
                    "ruta": tableros
                })
            progress_bar.progress((idx + 1) / len(algoritmos))
            
        progress_text.empty()
        progress_bar.empty()
st.markdown("</div>", unsafe_allow_html=True)

# --- RESULTADOS (TABLA MULTIALGORITMO) ---

@st.dialog("Paso a paso de la resolución")
def modal_resolucion(ruta, nombre_algo):
    # Inicializar paso en session_state si no existe o es de otro algoritmo
    key_paso = f"modal_paso_{nombre_algo}"
    if key_paso not in st.session_state:
        st.session_state[key_paso] = 0

    paso = st.session_state[key_paso]
    total = len(ruta) - 1

    # Cabecera: algoritmo + progreso
    st.markdown(f"""
    <div style='text-align:center; margin-bottom:0.75rem;'>
        <div style='font-family:Inter; color:#64748b; font-size:0.95rem; font-weight:600; margin-bottom:0.25rem;'>{nombre_algo}</div>
        <div style='font-family:JetBrains Mono,monospace; font-size:0.85rem; color:#94a3b8;'>Paso {paso} de {total}</div>
    </div>
    """, unsafe_allow_html=True)

    # Tablero
    html_board = get_static_board_html(ruta[paso], st.session_state.board_size)
    st.components.v1.html(html_board, height=290)

    # Botones de navegación
    col1, col2 = st.columns(2)
    if col1.button("Anterior", disabled=(paso == 0), use_container_width=True):
        st.session_state[key_paso] = paso - 1
        st.rerun()
    if col2.button("Siguiente", disabled=(paso == total), use_container_width=True):
        st.session_state[key_paso] = paso + 1
        st.rerun()

    # Slider para navegación rápida
    nuevo_paso = st.slider("Desliza para ver los pasos", 0, total, paso, label_visibility="collapsed")
    if nuevo_paso != paso:
        st.session_state[key_paso] = nuevo_paso
        st.rerun()




if st.session_state.resultados is not None:
    st.markdown("<hr style='margin: 3rem 0; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Escribir HTML actualizado al componente
    results_html = build_results_table_html(st.session_state.resultados)
    with open(os.path.join(results_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(results_html)

    # Renderizar tabla como componente (altura ~ header + filas)
    num_rows = len(st.session_state.resultados)
    component_height = 48 + num_rows * 55 + 20

    clicked_algo = results_table_component(
        key=f"results_table_{len(st.session_state.resultados)}",
        height=component_height
    )

    if clicked_algo:
        for res in st.session_state.resultados:
            if res['algoritmo'] == clicked_algo:
                modal_resolucion(res['ruta'], res['algoritmo'])
                break

