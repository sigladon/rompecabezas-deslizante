import streamlit as st
import time
import tracemalloc
import random
import os
from models import es_soluble
from algorithms import ejecutar_astar_puzzle, ejecutar_bfs, ejecutar_iddfs
from visualization import dibujar_ruta_puzzle
from graphviz import Digraph
import streamlit.components.v1 as components

st.set_page_config(layout="centered", page_title="8-Puzzle Solver", initial_sidebar_state="collapsed")

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

h1, h2, h3, h4 {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.02em;
}

h1 {
    font-size: 2.5rem !important;
    margin-bottom: 0.25rem;
}

p {
    color: #475569;
    line-height: 1.6;
}

/* ── Container Cards ── */
[data-testid="stVerticalBlock"] > div.element-container {
    margin-bottom: 1.25rem;
}

.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
}

/* ── Buttons ── */
div.stButton > button,
div[data-testid="stButton"] > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 100% !important;
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05) !important;
    cursor: pointer !important;
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

/* Segmented Control Styling Alignment */
div[data-testid="stSegmentedControl"] {
    display: flex;
    justify-content: center;
    margin-top: 0.5rem;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.25rem;
    box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.05);
    transition: box-shadow 0.2s;
}

[data-testid="stMetric"]:hover {
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -1px rgb(0 0 0 / 0.05);
}

[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif;
    color: #64748b;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
}

[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace;
    color: #0f172a;
    font-weight: 700;
    font-size: 1.875rem;
    line-height: 1.2;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 2rem;
    border-bottom: 1px solid #e2e8f0;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    color: #64748b;
    padding-top: 1rem;
    padding-bottom: 1rem;
    transition: color 0.2s;
    cursor: pointer;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #0f172a;
}

.stTabs [aria-selected="true"] {
    color: #2563eb !important;
    font-weight: 600;
    border-bottom-color: #2563eb !important;
    border-bottom-width: 2px !important;
}

/* Alerts */
.stAlert {
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05) !important;
    background-color: #ffffff !important;
}
.stAlert [data-testid="stMarkdownContainer"] {
    color: #0f172a !important;
}
</style>
""", unsafe_allow_html=True)

# ── Funciones de Visualización Actualizadas ──
def format_estado_html(tablero, is_path=False, tablero_padre=None):
    color_map = {
        1: ("#ef4444", "#ffffff"), # Red
        2: ("#f97316", "#ffffff"), # Orange
        3: ("#f59e0b", "#ffffff"), # Amber
        4: ("#10b981", "#ffffff"), # Emerald
        5: ("#06b6d4", "#ffffff"), # Cyan
        6: ("#3b82f6", "#ffffff"), # Blue
        7: ("#8b5cf6", "#ffffff"), # Violet
        8: ("#d946ef", "#ffffff"), # Fuchsia
        0: ("#f8fafc", "transparent")
    }
    
    color_bg = "#ffffff" if is_path else "#f8fafc"
    border_color = "#2563eb" if is_path else "#cbd5e1"
    border_width = 2 if is_path else 1
    
    idx_movida = -1
    idx_origen = -1
    flecha = ""
    
    if tablero_padre is not None:
        idx_movida = tablero_padre.index(0)
        idx_origen = tablero.index(0)
        
        r_origen, c_origen = divmod(idx_origen, 3)
        r_destino, c_destino = divmod(idx_movida, 3)
        
        if r_destino < r_origen: flecha = "↑"
        elif r_destino > r_origen: flecha = "↓"
        elif c_destino < c_origen: flecha = "←"
        elif c_destino > c_origen: flecha = "→"
    
    html = f'<<TABLE BORDER="{border_width}" COLOR="{border_color}" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8" BGCOLOR="{color_bg}">'
    for i in range(3):
        html += '<TR>'
        for j in range(3):
            idx = i * 3 + j
            val = tablero[idx]
            
            str_val = str(val) if val != 0 else " "
            if idx == idx_origen and flecha:
                str_val = flecha
            
            bg, fg = color_map.get(val, ("#f8fafc", "#0f172a"))
            
            if idx == idx_origen and tablero_padre is not None:
                bg = "#f1f5f9"
                fg = "#94a3b8"
                
            html += f'<TD BGCOLOR="{bg}" WIDTH="35" HEIGHT="35"><FONT COLOR="{fg}" POINT-SIZE="14" FACE="JetBrains Mono"><B>{str_val}</B></FONT></TD>'
        html += '</TR>'
    html += '</TABLE>>'
    return html

def dibujar_arbol_completo(arbol_expansion, ruta_tableros, movimientos):
    dot = Digraph(comment='Procedimiento de Solución 8-Puzzle')
    dot.attr('node', shape='none', margin='0')
    dot.attr(ordering='out')
    dot.attr(bgcolor='transparent')
    dot.attr(pad='0.5')
    dot.attr(ranksep='0.8')
    dot.attr(nodesep='0.4')
    
    ruta_set = set(ruta_tableros)
    
    camino_edges = set()
    for i in range(len(ruta_tableros)-1):
        camino_edges.add((ruta_tableros[i], ruta_tableros[i+1]))
        
    nodos = set()
    padre_dict = {}
    
    for padre, hijo, mov in arbol_expansion:
        nodos.add(padre)
        nodos.add(hijo)
        if hijo not in padre_dict:
            padre_dict[hijo] = padre
            
    for i in range(1, len(ruta_tableros)):
        nodos.add(ruta_tableros[i])
        padre_dict[ruta_tableros[i]] = ruta_tableros[i-1]
    nodos.add(ruta_tableros[0])

    for estado in nodos:
        node_id = "N" + "".join(map(str, estado))
        is_path = estado in ruta_set
        padre = padre_dict.get(estado)
        label = format_estado_html(estado, is_path, padre)
        dot.node(node_id, label)
            
    for padre, hijo, mov in arbol_expansion:
        padre_id = "N" + "".join(map(str, padre))
        hijo_id = "N" + "".join(map(str, hijo))
        
        if (padre, hijo) in camino_edges:
            dot.edge(padre_id, hijo_id, label=mov, color="#2563eb", penwidth="2.5", fontcolor="#1d4ed8", fontname="Inter", fontsize="11")
        else:
            dot.edge(padre_id, hijo_id, label=mov, color="#cbd5e1", style="dashed", penwidth="1", fontcolor="#94a3b8", fontname="Inter", fontsize="10")
            
    for i in range(len(ruta_tableros)-1):
        padre = ruta_tableros[i]
        hijo = ruta_tableros[i+1]
        mov = movimientos[i]
        if (padre, hijo) not in [(p, h) for p, h, m in arbol_expansion]:
            padre_id = "N" + "".join(map(str, padre))
            hijo_id = "N" + "".join(map(str, hijo))
            dot.edge(padre_id, hijo_id, label=mov, color="#2563eb", penwidth="2.5", fontcolor="#1d4ed8", fontname="Inter", fontsize="11")
            
    return dot

# ── Custom HTML Component (Sliding Puzzle) ──
sliding_puzzle_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>8-Puzzle</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background: transparent;
            margin: 0; padding: 20px;
            display: flex; flex-direction: column; align-items: center;
        }
        .grid {
            display: grid; grid-template-columns: repeat(3, 84px); gap: 12px;
            background: #ffffff; padding: 20px; border-radius: 20px;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
            border: 1px solid #e2e8f0;
        }
        .cell {
            width: 84px; height: 84px;
            border-radius: 14px;
            display: flex; align-items: center; justify-content: center;
            font-family: 'JetBrains Mono', monospace; font-size: 32px; font-weight: 700;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            user-select: none;
            box-shadow: 0 2px 4px -1px rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        }
        .cell:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        }
        .cell:active { transform: scale(0.96); box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05); }
        .cell.empty {
            background: #f8fafc; box-shadow: inset 0 2px 4px 0 rgba(0,0,0,0.06); color: transparent; cursor: default; border: 1px solid #e2e8f0;
        }
        .cell.empty:hover { transform: none; box-shadow: inset 0 2px 4px 0 rgba(0,0,0,0.06); }
        
        /* Premium Distinct colors for each tile with gradients and text-shadow */
        .tile-1 { background: linear-gradient(135deg, #ef4444, #dc2626); color: white; border: 1px solid #b91c1c; text-shadow: 0 1px 2px rgba(0,0,0,0.2); }
        .tile-2 { background: linear-gradient(135deg, #f97316, #ea580c); color: white; border: 1px solid #c2410c; text-shadow: 0 1px 2px rgba(0,0,0,0.2); }
        .tile-3 { background: linear-gradient(135deg, #f59e0b, #d97706); color: white; border: 1px solid #b45309; text-shadow: 0 1px 2px rgba(0,0,0,0.2); }
        .tile-4 { background: linear-gradient(135deg, #10b981, #059669); color: white; border: 1px solid #047857; text-shadow: 0 1px 2px rgba(0,0,0,0.2); }
        .tile-5 { background: linear-gradient(135deg, #06b6d4, #0891b2); color: white; border: 1px solid #0e7490; text-shadow: 0 1px 2px rgba(0,0,0,0.2); }
        .tile-6 { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; border: 1px solid #1d4ed8; text-shadow: 0 1px 2px rgba(0,0,0,0.2); }
        .tile-7 { background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: white; border: 1px solid #6d28d9; text-shadow: 0 1px 2px rgba(0,0,0,0.2); }
        .tile-8 { background: linear-gradient(135deg, #d946ef, #c026d3); color: white; border: 1px solid #a21caf; text-shadow: 0 1px 2px rgba(0,0,0,0.2); }
    </style>
</head>
<body>
    <div class="grid" id="main-board"></div>

    <script>
        let currentBoard = [1, 2, 3, 4, 5, 6, 7, 8, 0];
        let currentResetKey = -1;

        function renderBoard() {
            const boardEl = document.getElementById('main-board');
            boardEl.innerHTML = '';
            for (let i = 0; i < 9; i++) {
                const val = currentBoard[i];
                const cell = document.createElement('div');
                cell.innerText = val === 0 ? '' : val;
                cell.className = 'cell ' + (val === 0 ? 'empty' : 'tile-' + val);
                cell.onclick = () => handleTileClick(i);
                boardEl.appendChild(cell);
            }
        }

        function handleTileClick(index) {
            const emptyIndex = currentBoard.indexOf(0);
            const row = Math.floor(index / 3);
            const col = index % 3;
            const emptyRow = Math.floor(emptyIndex / 3);
            const emptyCol = emptyIndex % 3;

            const isAdjacent = (Math.abs(row - emptyRow) === 1 && col === emptyCol) || 
                               (Math.abs(col - emptyCol) === 1 && row === emptyRow);
            
            if (isAdjacent) {
                const temp = currentBoard[index];
                currentBoard[index] = currentBoard[emptyIndex];
                currentBoard[emptyIndex] = temp;
                renderBoard();
                window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:setComponentValue", value: currentBoard }, "*");
            }
        }

        window.addEventListener("message", function(event) {
            if (event.data.type === "streamlit:render") {
                const args = event.data.args;
                if (args && args.board && args.reset_key !== currentResetKey) {
                    currentResetKey = args.reset_key;
                    currentBoard = args.board;
                    renderBoard();
                }
            }
        });

        renderBoard();

        window.addEventListener("load", function() {
            window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:componentReady", apiVersion: 1 }, "*");
            window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:setFrameHeight", height: 350 }, "*");
        });
    </script>
</body>
</html>
"""

# Inicializar componente de Streamlit
component_dir = os.path.join(os.path.dirname(__file__), "puzzle_component")
os.makedirs(component_dir, exist_ok=True)
with open(os.path.join(component_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(sliding_puzzle_html)

puzzle_builder_component = components.declare_component("puzzle_builder", path=component_dir)

# --- CABECERA ---
st.markdown("""
<div style="text-align: center; margin-top: 2rem;">
    <h1>8-Puzzle Solver</h1>
    <p style="font-size: 1.1rem; margin-bottom: 2.5rem; max-width: 600px; margin-left: auto; margin-right: auto;">
        Explora y compara la eficiencia de algoritmos de búsqueda heurística y no informada.
    </p>
</div>
""", unsafe_allow_html=True)

# --- ESTADO INICIAL ---
if 'board' not in st.session_state:
    st.session_state.board = (1, 2, 3, 4, 5, 6, 7, 8, 0)
if 'reset_key' not in st.session_state:
    st.session_state.reset_key = 0
if 'last_modo' not in st.session_state:
    st.session_state.last_modo = "Manual"
if 'resultado' not in st.session_state:
    st.session_state.resultado = None

meta = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# --- LAYOUT VERTICAL ---

# 1. Radio Button (Modo)
st.markdown("<div style='display:flex;justify-content:center;margin-bottom:1rem;'>", unsafe_allow_html=True)
modo = st.radio("Generación del rompecabezas:", ["Aleatorio", "Manual"], horizontal=True, label_visibility="collapsed")
st.markdown("</div>", unsafe_allow_html=True)

# Lógica de Cambio de Modo
if modo != st.session_state.last_modo:
    st.session_state.last_modo = modo
    st.session_state.reset_key += 1
    st.session_state.resultado = None # Limpiar resultados anteriores
    if modo == "Aleatorio":
        while True:
            nuevo = list(range(9))
            random.shuffle(nuevo)
            if es_soluble(tuple(nuevo)):
                st.session_state.board = tuple(nuevo)
                break
    else:
        st.session_state.board = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        
st.markdown("<p style='text-align:center;color:#64748b;font-size:0.875rem;margin-bottom:10px;'>Haz clic en las piezas adyacentes al espacio vacío para moverlas</p>", unsafe_allow_html=True)

# 2. Rompecabezas Interactivo
board_res = puzzle_builder_component(board=st.session_state.board, reset_key=st.session_state.reset_key, key="puzzle_builder")

if board_res and tuple(board_res) != st.session_state.board:
    st.session_state.board = tuple(board_res)
    st.session_state.resultado = None # Limpiar resultado si cambia el tablero

# 3. Control Segmentado (Algoritmos)
st.markdown("<h4 style='text-align:center;margin-top:2rem;font-weight:600;'>Algoritmo de Resolución</h4>", unsafe_allow_html=True)

opciones_algo = ["BFS", "IDDFS", "A* Fuera de Lugar", "A* Manhattan"]
algoritmo_sel = st.segmented_control("Selecciona el algoritmo", options=opciones_algo, selection_mode="single", label_visibility="collapsed")

# 4. Botón Resolver
st.markdown("<div style='max-width:400px; margin: 0 auto; margin-top:1.5rem;'>", unsafe_allow_html=True)
if st.button("Resolver", type="primary", use_container_width=True):
    if not algoritmo_sel:
        st.warning("Por favor, selecciona un algoritmo del menú anterior.")
    elif not es_soluble(st.session_state.board):
        st.error("El estado actual no es soluble.")
    else:
        with st.spinner(f"Calculando con {algoritmo_sel}..."):
            tracemalloc.start()
            start_time = time.time()
            
            if algoritmo_sel == "BFS": res = ejecutar_bfs(st.session_state.board, meta)
            elif algoritmo_sel == "IDDFS": 
                res = ejecutar_iddfs(st.session_state.board, meta)
                if res[0] is not None: res = (res[0], res[1], sum(res[2]), res[3], res[4])
            elif algoritmo_sel == "A* Fuera de Lugar": res = ejecutar_astar_puzzle(st.session_state.board, meta, "fuera_lugar")
            elif algoritmo_sel == "A* Manhattan": res = ejecutar_astar_puzzle(st.session_state.board, meta, "manhattan")
            
            end_time = time.time()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            if res is not None and res[0] is not None:
                st.session_state.resultado = {
                    "algoritmo": algoritmo_sel,
                    "movs": res[0], "ruta": res[1], "nodos": res[2], "costo": res[3], "arbol": res[4],
                    "tiempo": end_time - start_time,
                    "memoria": peak / 1024
                }
            else:
                st.error("No se encontró solución.")
st.markdown("</div>", unsafe_allow_html=True)

# 5. Resumen y Estadísticas
st.markdown("<hr style='margin: 3rem 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
res = st.session_state.resultado

if not res:
    st.markdown("""
    <div style='padding: 4rem 2rem; text-align: center; background: #ffffff; border: 1px dashed #cbd5e1; border-radius: 16px; margin-top: 1rem;'>
        <h4 style='color: #64748b; font-weight: 500; margin-bottom: 0.5rem;'>Aún no hay resultados</h4>
        <p style='color: #94a3b8; margin: 0;'>Selecciona un algoritmo y presiona "Resolver" para ver el análisis y la solución.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"<h3 style='text-align:center; margin-bottom: 2rem;'>Resultados: {res['algoritmo']}</h3>", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Pasos / Costo", len(res['movs']))
    m2.metric("Nodos Expandidos", res['nodos'])
    m3.metric("Tiempo (s)", f"{res['tiempo']:.4f}")
    m4.metric("Memoria Pico", f"{res['memoria']:.1f} KB")
    
    st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Secuencia de Movimientos", "Árbol de Expansión"])
    
    with tab1:
        st.markdown("<p style='font-size:0.875rem;color:#64748b;margin-bottom:1.5rem;'>Representación visual paso a paso desde el estado inicial hasta la meta.</p>", unsafe_allow_html=True)
        fig = dibujar_ruta_puzzle(res['ruta'], res['movs'])
        fig.patch.set_alpha(0.0)
        st.pyplot(fig, transparent=True)
        
    with tab2:
        if res['nodos'] <= 50:
            st.markdown("<p style='font-size:0.875rem;color:#64748b;margin-bottom:1.5rem;'>El grafo muestra el árbol de búsqueda. El camino azul es la ruta óptima encontrada.</p>", unsafe_allow_html=True)
            arbol = dibujar_arbol_completo(res['arbol'], res['ruta'], res['movs'])
            st.graphviz_chart(arbol, use_container_width=True)
        else:
            st.info(f"El árbol de expansión tiene **{res['nodos']} nodos**, lo cual es demasiado grande para renderizar interactivamente. Se recomienda un estado más cercano a la meta para visualizar el árbol completo.")
