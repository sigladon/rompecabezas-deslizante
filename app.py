import streamlit as st
import time
import tracemalloc
import random
from models import es_soluble
from algorithms import ejecutar_astar_puzzle, ejecutar_bfs, ejecutar_iddfs
from visualization import dibujar_ruta_puzzle
from graphviz import Digraph
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="8-Puzzle Solver — IA", page_icon="🧩")

# ── UI/UX Pro Max: Light Mode + Fira Code/Sans ──
st.markdown("""
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap');

/* ── Reduced Motion Guard ── */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Fira Sans', system-ui, sans-serif;
    font-size: 16px;
    line-height: 1.6;
}

.stApp {
    background: #f8fafc;
    background-image:
        radial-gradient(ellipse 70% 40% at 15% -5%, rgba(59, 130, 246, 0.06) 0%, transparent 60%),
        radial-gradient(ellipse 50% 35% at 85% 105%, rgba(139, 92, 246, 0.04) 0%, transparent 55%);
    color: #0f172a;
    min-height: 100vh;
}

/* ── Hide Streamlit chrome ── */
header, #MainMenu, footer { visibility: hidden; }

/* ── Typography ── */
h1 {
    font-family: 'Fira Code', monospace;
    font-weight: 700;
    font-size: 2.6rem !important;
    background: linear-gradient(135deg, #1d4ed8 0%, #4f46e5 55%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    letter-spacing: -0.5px;
    padding-bottom: 0.5rem;
    text-shadow: none;
    filter: drop-shadow(0 2px 8px rgba(37, 99, 235, 0.15));
}

h2, h3 {
    font-family: 'Fira Code', monospace;
    color: #1e293b;
    font-weight: 600;
    letter-spacing: -0.3px;
}

h4, p, li, span {
    font-family: 'Fira Sans', sans-serif;
    color: #334155;
    line-height: 1.65;
}

/* ── Divider ── */
hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 2rem 0;
}

/* ── Override Streamlit button theme variables ── */
:root {
    --primary-color: #60a5fa !important;
    --background-color: #000000 !important;
    --secondary-background-color: #0f172a !important;
    --text-color: #e2e8f0 !important;
}

/* ── Buttons — max specificity to beat Streamlit's Emotion CSS ── */
div.stButton > button,
div[data-testid="stButton"] > button,
.stButton button {
    font-family: 'Fira Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.3px !important;
    color: #e2e8f0 !important;
    background-color: #0f172a !important;
    background: #0f172a !important;
    border: 1px solid rgba(148, 163, 184, 0.25) !important;
    border-radius: 12px !important;
    padding: 0.7rem 1.1rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: background-color 0.2s ease, border-color 0.2s ease,
                box-shadow 0.2s ease, transform 0.15s ease, color 0.2s ease !important;
    outline: none !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.5) !important;
}

div.stButton > button:hover,
div[data-testid="stButton"] > button:hover,
.stButton button:hover {
    transform: translateY(-2px) !important;
    background-color: #1e2a50 !important;
    background: #1e2a50 !important;
    border-color: rgba(96, 165, 250, 0.55) !important;
    color: #93c5fd !important;
    box-shadow: 0 0 18px rgba(59, 130, 246, 0.22), 0 4px 14px rgba(0,0,0,0.5) !important;
}

div.stButton > button:active,
.stButton button:active {
    transform: translateY(0) scale(0.98) !important;
}

div.stButton > button:focus-visible,
.stButton button:focus-visible {
    outline: 2px solid #60a5fa !important;
    outline-offset: 2px !important;
    box-shadow: 0 0 0 4px rgba(96, 165, 250, 0.2) !important;
}

div.stButton > button:disabled,
.stButton button:disabled {
    opacity: 0.35 !important;
    cursor: not-allowed !important;
    transform: none !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
    color: #475569 !important;
}

/* ── Algorithm buttons — distinct accent colors on hover ── */
[data-testid="column"]:nth-child(1) div.stButton > button:hover { border-color: rgba(96, 165, 250, 0.6) !important; color: #93c5fd !important; }
[data-testid="column"]:nth-child(2) div.stButton > button:hover { border-color: rgba(167, 139, 250, 0.6) !important; color: #c4b5fd !important; }
[data-testid="column"]:nth-child(3) div.stButton > button:hover { border-color: rgba(52, 211, 153, 0.6) !important; color: #6ee7b7 !important; }
[data-testid="column"]:nth-child(4) div.stButton > button:hover { border-color: rgba(251, 146, 60, 0.6) !important; color: #fdba74 !important; }


/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    cursor: default;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: #93c5fd;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.08), 0 6px 20px rgba(0,0,0,0.08);
}

[data-testid="stMetricLabel"] {
    font-family: 'Fira Sans', sans-serif;
    color: #64748b;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
}

[data-testid="stMetricValue"] {
    font-family: 'Fira Code', monospace;
    color: #2563eb;
    font-weight: 700;
    font-size: 2rem;
}

/* ── Alerts ── */
.stAlert {
    border-radius: 12px;
    border-left-width: 3px !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    font-family: 'Fira Sans', sans-serif;
}

/* ── Radio ── */
.stRadio > label {
    font-family: 'Fira Sans', sans-serif;
    color: #475569;
    font-weight: 500;
}

.stRadio [data-testid="stMarkdownContainer"] p {
    font-family: 'Fira Sans', sans-serif;
}

/* ── Section cards ── */
.section-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 1.75rem 2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    margin-bottom: 1.5rem;
}

/* ── Subtitle text ── */
.page-subtitle {
    text-align: center;
    color: #64748b;
    font-size: 1rem;
    font-family: 'Fira Sans', sans-serif;
    margin-bottom: 2.5rem;
    letter-spacing: 0.2px;
}

/* ── Code block ── */
div[data-testid="stCodeBlock"] {
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

/* ── Spinner override ── */
.stSpinner > div {
    border-top-color: #2563eb !important;
}

/* ── Pulse skeleton animation ── */
@keyframes pulse-bg {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
.skeleton {
    background: #e2e8f0;
    border-radius: 8px;
    animation: pulse-bg 1.8s ease-in-out infinite;
}
</style>
""", unsafe_allow_html=True)

def format_estado_html(tablero, is_path=False, tablero_padre=None):
    color_bg = "#1e293b" if is_path else "#0f172a"
    color_cell = "#334155" if is_path else "#1e293b"
    color_text = "#f8fafc" if is_path else "#94a3b8"
    
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
    
    html = f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="2" CELLPADDING="8" BGCOLOR="{color_bg}">'
    for i in range(3):
        html += '<TR>'
        for j in range(3):
            idx = i * 3 + j
            val = tablero[idx]
            
            if idx == idx_origen and flecha:
                str_val = flecha
            else:
                str_val = str(val) if val != 0 else " "
            
            current_bg = color_cell
            current_text = color_text
            
            if idx == idx_movida:
                current_bg = "#38bdf8" if is_path else "#3b82f6"
                current_text = "#0f172a" if is_path else "#ffffff"
            elif idx == idx_origen and tablero_padre is not None:
                current_bg = "#0f172a" if is_path else "#020617"
                current_text = "#818cf8" if is_path else "#475569"
                
            html += f'<TD BGCOLOR="{current_bg}" WIDTH="35" HEIGHT="35"><FONT COLOR="{current_text}" POINT-SIZE="14"><B>{str_val}</B></FONT></TD>'
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
            dot.edge(padre_id, hijo_id, label=mov, color="#38bdf8", penwidth="3", fontcolor="#38bdf8", fontname="Outfit bold", fontsize="12")
        else:
            dot.edge(padre_id, hijo_id, label=mov, color="#475569", style="dashed", penwidth="1", fontcolor="#64748b", fontname="Outfit", fontsize="10")
            
    for i in range(len(ruta_tableros)-1):
        padre = ruta_tableros[i]
        hijo = ruta_tableros[i+1]
        mov = movimientos[i]
        if (padre, hijo) not in [(p, h) for p, h, m in arbol_expansion]:
            padre_id = "N" + "".join(map(str, padre))
            hijo_id = "N" + "".join(map(str, hijo))
            dot.edge(padre_id, hijo_id, label=mov, color="#38bdf8", penwidth="3", fontcolor="#38bdf8", fontname="Outfit bold", fontsize="12")
            
    return dot

drag_and_drop_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@500;700&family=Fira+Sans:wght@400;600&display=swap" rel="stylesheet">
    <style>
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { transition-duration: 0.01ms !important; }
        }
        body {
            font-family: 'Fira Sans', sans-serif;
            color: #e2e8f0; background: transparent;
            margin: 0; padding: 20px;
        }
        .container {
            display: flex; gap: 40px;
            justify-content: center; align-items: flex-start; flex-wrap: wrap;
        }
        .board-container, .loose-tiles-container { text-align: center; }
        .section-label {
            font-family: 'Fira Code', monospace;
            font-size: 0.75rem; font-weight: 600;
            letter-spacing: 1.2px; text-transform: uppercase;
            color: #64748b; margin-bottom: 12px;
        }
        .board {
            display: grid; grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            background: rgba(15, 23, 42, 0.9);
            padding: 14px; border-radius: 16px;
            width: fit-content;
            box-shadow: 0 0 0 1px rgba(148,163,184,0.12), 0 16px 32px rgba(0,0,0,0.6);
            margin: 0 auto;
        }
        .cell {
            width: 80px; height: 80px;
            background: rgba(30, 41, 59, 0.6);
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            border: 1px dashed rgba(148, 163, 184, 0.25);
            transition: border-color 0.15s ease, background 0.15s ease;
        }
        .cell.drag-over {
            border-color: rgba(96, 165, 250, 0.6);
            background: rgba(59, 130, 246, 0.08);
        }
        .tile {
            width: 76px; height: 76px;
            background: linear-gradient(145deg, #1d4ed8, #2563eb);
            color: #f0f9ff; border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-family: 'Fira Code', monospace;
            font-size: 28px; font-weight: 700;
            cursor: grab;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4), 0 0 0 1px rgba(96,165,250,0.3);
            user-select: none;
            transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
        }
        .tile:hover  { transform: scale(1.04); box-shadow: 0 6px 18px rgba(0,0,0,0.5), 0 0 14px rgba(96,165,250,0.25); }
        .tile:active { cursor: grabbing; transform: scale(0.95); opacity: 0.8; }
        .empty-tile {
            background: rgba(30,41,59,0.5);
            box-shadow: inset 0 2px 6px rgba(0,0,0,0.3);
            border: 1px solid rgba(148,163,184,0.15);
            color: #475569; font-size: 20px;
        }
        .loose-tiles-container { text-align: center; }
        .loose-tiles {
            display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;
            width: 280px;
            background: rgba(15, 23, 42, 0.55);
            border: 1px solid rgba(148,163,184,0.10);
            padding: 14px; border-radius: 16px;
            min-height: 270px;
            align-content: flex-start; margin: 0 auto;
        }
        .btn {
            font-family: 'Fira Sans', sans-serif;
            font-weight: 600; font-size: 0.875rem;
            background: #3b82f6; color: #f0f9ff;
            border: none; padding: 11px 24px;
            border-radius: 10px; cursor: pointer;
            margin-top: 18px; display: none;
            transition: background 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
            box-shadow: 0 4px 12px rgba(59,130,246,0.35);
        }
        .btn:hover { background: #2563eb; transform: translateY(-2px); box-shadow: 0 6px 16px rgba(59,130,246,0.45); }
        .btn:active { transform: translateY(0); }
        .btn:focus-visible { outline: 2px solid #93c5fd; outline-offset: 2px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="board-container">
            <p class="section-label">Tablero</p>
            <div class="board" id="board" role="grid" aria-label="Tablero 8-Puzzle">
                <div class="cell" ondrop="drop(event)" ondragover="allowDrop(event)" ondragleave="dragLeave(event)" role="gridcell" aria-label="Posición 1"></div>
                <div class="cell" ondrop="drop(event)" ondragover="allowDrop(event)" ondragleave="dragLeave(event)" role="gridcell" aria-label="Posición 2"></div>
                <div class="cell" ondrop="drop(event)" ondragover="allowDrop(event)" ondragleave="dragLeave(event)" role="gridcell" aria-label="Posición 3"></div>
                <div class="cell" ondrop="drop(event)" ondragover="allowDrop(event)" ondragleave="dragLeave(event)" role="gridcell" aria-label="Posición 4"></div>
                <div class="cell" ondrop="drop(event)" ondragover="allowDrop(event)" ondragleave="dragLeave(event)" role="gridcell" aria-label="Posición 5"></div>
                <div class="cell" ondrop="drop(event)" ondragover="allowDrop(event)" ondragleave="dragLeave(event)" role="gridcell" aria-label="Posición 6"></div>
                <div class="cell" ondrop="drop(event)" ondragover="allowDrop(event)" ondragleave="dragLeave(event)" role="gridcell" aria-label="Posición 7"></div>
                <div class="cell" ondrop="drop(event)" ondragover="allowDrop(event)" ondragleave="dragLeave(event)" role="gridcell" aria-label="Posición 8"></div>
                <div class="cell" ondrop="drop(event)" ondragover="allowDrop(event)" ondragleave="dragLeave(event)" role="gridcell" aria-label="Posición 9"></div>
            </div>
        </div>
        <div class="loose-tiles-container">
            <p class="section-label">Fichas disponibles</p>
            <div class="loose-tiles" id="loose" ondrop="drop(event)" ondragover="allowDrop(event)" ondragleave="dragLeave(event)" role="list" aria-label="Fichas sin colocar">
            </div>
            <button id="submitBtn" class="btn" onclick="submitBoard()" aria-label="Guardar configuración del tablero">Guardar Rompecabezas</button>
        </div>
    </div>

    <script>
        function allowDrop(ev) {
            ev.preventDefault();
            var cell = ev.currentTarget;
            if (cell.classList.contains('cell') || cell.classList.contains('loose-tiles')) {
                cell.classList.add('drag-over');
            }
        }
        function dragLeave(ev) {
            ev.currentTarget.classList.remove('drag-over');
        }
        function drag(ev) {
            ev.dataTransfer.setData("text", ev.target.id);
            ev.target.setAttribute('aria-grabbed', 'true');
        }
        function drop(ev) {
            ev.preventDefault();
            ev.currentTarget.classList.remove('drag-over');
            var data = ev.dataTransfer.getData("text");
            document.getElementById(data).removeAttribute('aria-grabbed');
            var target = ev.target;

            // Drop on cell
            if (target.className.includes("cell")) {
                if (target.children.length === 0) {
                    target.appendChild(document.getElementById(data));
                } else {
                    var existingTile = target.children[0];
                    var source = document.getElementById(data).parentNode;
                    target.appendChild(document.getElementById(data));
                    source.appendChild(existingTile);
                }
            }
            // Drop on tile inside cell (swap)
            else if (target.className.includes("tile") && target.parentNode.className.includes("cell")) {
                var cell = target.parentNode;
                var source = document.getElementById(data).parentNode;
                cell.appendChild(document.getElementById(data));
                source.appendChild(target);
            }
            // Drop back to loose area
            else if (target.className.includes("loose-tiles") || target.parentNode.className.includes("loose-tiles")) {
                var dropZone = target.className.includes("loose-tiles") ? target : target.parentNode;
                dropZone.appendChild(document.getElementById(data));
            }
            checkComplete();
        }

        const loose = document.getElementById('loose');
        for (let i = 0; i <= 8; i++) {
            let tile = document.createElement('div');
            tile.className = 'tile';
            if(i === 0) tile.className += ' empty-tile';
            tile.id = 'tile_' + i;
            tile.draggable = true;
            tile.ondragstart = drag;
            tile.innerText = i === 0 ? "" : i;
            loose.appendChild(tile);
        }

        function checkComplete() {
            const board = document.getElementById('board');
            let isFull = true;
            for(let cell of board.children) {
                if(cell.children.length === 0) isFull = false;
            }
            document.getElementById('submitBtn').style.display = isFull ? 'inline-block' : 'none';
        }

        function sendMessageToStreamlitClient(type, data) {
            var outData = Object.assign({
                isStreamlitMessage: true,
                type: type,
            }, data);
            window.parent.postMessage(outData, "*");
        }

        // Informar a Streamlit que el componente está listo para comunicarse
        sendMessageToStreamlitClient("streamlit:componentReady", {apiVersion: 1});

        function submitBoard() {
            const board = document.getElementById('board');
            let result = [];
            for(let cell of board.children) {
                if(cell.children.length > 0) {
                    let val = cell.children[0].id.replace('tile_', '');
                    result.push(parseInt(val));
                }
            }
            sendMessageToStreamlitClient("streamlit:setComponentValue", {value: result});
        }
        
        window.addEventListener("load", function() {
            sendMessageToStreamlitClient("streamlit:setFrameHeight", {height: 480});
        });
    </script>
</body>
</html>
"""

import os
component_dir = os.path.join(os.path.dirname(__file__), "puzzle_component")
os.makedirs(component_dir, exist_ok=True)
with open(os.path.join(component_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(drag_and_drop_html)

puzzle_builder_component = components.declare_component("puzzle_builder", path=component_dir)


# ── Cabecera ──
st.markdown("""
<h1>8-Puzzle Solver</h1>
<p class="page-subtitle">
    Explora y compara algoritmos de búsqueda —
    <span style="color:#60a5fa">BFS</span>,
    <span style="color:#a78bfa">IDDFS</span> y
    <span style="color:#34d399">A*</span> —
    para resolver el rompecabezas deslizante de 8 piezas.
</p>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN DEL ESTADO ---
if 'inicio' not in st.session_state:
    st.session_state.inicio = (1, 2, 3, 0, 4, 6, 7, 5, 8)

meta = (1, 2, 3, 4, 5, 6, 7, 8, 0)

st.markdown("""
<h3 style="display:flex;align-items:center;gap:0.5rem;">
  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="#60a5fa" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><circle cx="12" cy="12" r="3"/></svg>
  Configuración del Rompecabezas
</h3>
""", unsafe_allow_html=True)
modo_creacion = st.radio("Método de creación:", ["Generar Aleatorio", "Crear Manualmente (Drag & Drop)"], horizontal=True)

st.markdown("<br>", unsafe_allow_html=True)

if modo_creacion == "Generar Aleatorio":
    # Autogenerar si venimos de la creación manual y está en None
    if st.session_state.inicio is None:
        while True:
            nuevo_inicio = list(range(9))
            random.shuffle(nuevo_inicio)
            if es_soluble(tuple(nuevo_inicio)):
                st.session_state.inicio = tuple(nuevo_inicio)
                break

    col1, col_gap, col2 = st.columns([1, 0.1, 1])
    with col1:
        st.markdown("<div style='padding-top:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("Generar puzzle aleatorio soluble", use_container_width=True):
            while True:
                nuevo_inicio = list(range(9))
                random.shuffle(nuevo_inicio)
                if es_soluble(tuple(nuevo_inicio)):
                    st.session_state.inicio = tuple(nuevo_inicio)
                    break

    with col2:
        st.info("Vista previa del estado inicial:", icon="ℹ️")
        fig = dibujar_ruta_puzzle([st.session_state.inicio], ["Estado Inicial"])
        fig.patch.set_alpha(0.0)
        st.pyplot(fig, transparent=True, use_container_width=False)

elif modo_creacion == "Crear Manualmente (Drag & Drop)":
    st.markdown("<p style='color:#94a3b8;'>Arrastra las fichas al tablero. Puedes intercambiarlas soltando una sobre otra. Al completar las 9 celdas, aparecerá el botón <strong style='color:#e2e8f0;'>Guardar Rompecabezas</strong>.</p>", unsafe_allow_html=True)
    
    # Renderizamos el componente custom de Drag & Drop
    board_result = puzzle_builder_component(key="dnd_builder")
    
    if board_result is not None and len(board_result) == 9:
        estado = tuple(board_result)
        if es_soluble(estado):
            st.success(f"✅ ¡Rompecabezas guardado y soluble! Estado: {estado}")
            st.session_state.inicio = estado
            
            st.write("**Visualización previa:**")
            fig = dibujar_ruta_puzzle([st.session_state.inicio], ["Estado Creado"])
            fig.patch.set_alpha(0.0)
            st.pyplot(fig, transparent=True)
            
        else:
            st.error("❌ Rompecabezas guardado, pero **NO ES SOLUBLE**. Intercambia algunas piezas (arrastrando una sobre otra) para cambiar la paridad y vuelve a guardar.")
            st.session_state.inicio = None
    else:
        st.warning("⚠️ Completa el tablero con las 9 fichas y haz clic en 'Guardar Rompecabezas' para poder resolver.")
        st.session_state.inicio = None

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<h3 style="display:flex;align-items:center;gap:0.5rem;">
  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="#a78bfa" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
  Selecciona el algoritmo de búsqueda
</h3>
<p style="color:#64748b;font-size:0.875rem;margin-top:0.25rem;font-family:'Fira Sans',sans-serif;">Cada algoritmo tiene distintas características de completitud, optimalidad y complejidad.</p>
""", unsafe_allow_html=True)

# Layout principal
col_alg1, col_alg2, col_alg3, col_alg4 = st.columns(4)

algoritmo = None

# Solo permitimos ejecutar si el estado inicial está definido y es válido
deshabilitado = st.session_state.inicio is None

if col_alg1.button("BFS — Anchura", use_container_width=True, disabled=deshabilitado, help="Completo y óptimo. Explora nivel por nivel."): algoritmo = "BFS"
if col_alg2.button("IDDFS — Prof. Iterativa", use_container_width=True, disabled=deshabilitado, help="Óptimo en costo uniforme. Bajo uso de memoria."): algoritmo = "IDDFS"
if col_alg3.button("A* — Fuera de lugar", use_container_width=True, disabled=deshabilitado, help="Heurística h1: fichas fuera de posición."): algoritmo = "A_FUERA"
if col_alg4.button("A* — Manhattan", use_container_width=True, disabled=deshabilitado, help="Heurística h2: distancia Manhattan. Más informada."): algoritmo = "A_MANHATTAN"

if algoritmo and st.session_state.inicio is not None:
    if not es_soluble(st.session_state.inicio):
        st.error("Estado inicial sin solución. Genera o configura un puzzle válido.", icon="🚨")
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.spinner(f"Ejecutando {algoritmo}..."):
            tracemalloc.start()
            start_time = time.time()
            
            movs, ruta, nodos_exp, costo, arbol_expansion = None, None, None, None, []
            
            if algoritmo == "BFS":
                movs, ruta, nodos_exp, costo, arbol_expansion = ejecutar_bfs(st.session_state.inicio, meta)
            elif algoritmo == "IDDFS":
                movs, ruta, historial_nodos, costo, arbol_expansion = ejecutar_iddfs(st.session_state.inicio, meta)
                if movs is not None:
                    nodos_exp = sum(historial_nodos)
            elif algoritmo == "A_FUERA":
                movs, ruta, nodos_exp, costo, arbol_expansion = ejecutar_astar_puzzle(st.session_state.inicio, meta, "fuera_lugar")
            elif algoritmo == "A_MANHATTAN":
                movs, ruta, nodos_exp, costo, arbol_expansion = ejecutar_astar_puzzle(st.session_state.inicio, meta, "manhattan")
                
            end_time = time.time()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            tiempo_ejecucion = end_time - start_time
            memoria_usada_kb = peak / 1024
            
            if movs is not None:
                nombres = {"BFS": "Búsqueda en Anchura", "IDDFS": "Profundidad Iterativa",
                           "A_FUERA": "A* Fuera de Lugar", "A_MANHATTAN": "A* Manhattan"}
                st.markdown(f"""
<h3 style='text-align:center;color:#818cf8;display:flex;align-items:center;justify-content:center;gap:0.5rem;'>
  <svg xmlns='http://www.w3.org/2000/svg' width='22' height='22' fill='none' viewBox='0 0 24 24' stroke='#818cf8' stroke-width='2' aria-hidden='true'><path stroke-linecap='round' stroke-linejoin='round' d='M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z'/></svg>
  Resultados &mdash; {nombres.get(algoritmo, algoritmo)}
</h3>
""", unsafe_allow_html=True)

                met_col1, met_col2, met_col3, met_col4 = st.columns(4)
                met_col1.metric(label="Pasos", value=len(movs))
                met_col2.metric(label="Nodos expandidos", value=nodos_exp)
                met_col3.metric(label="Tiempo (s)", value=f"{tiempo_ejecucion:.4f}")
                met_col4.metric(label="Memoria pico", value=f"{memoria_usada_kb:.1f} KB")

                st.markdown("<hr>", unsafe_allow_html=True)
                
                if nodos_exp <= 50:
                    col_left, col_right = st.columns([1, 1])
                    
                    with col_left:
                        st.markdown("""
<h3 style="display:flex;align-items:center;gap:0.5rem;">
  <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' fill='none' viewBox='0 0 24 24' stroke='#60a5fa' stroke-width='2' aria-hidden='true'><path stroke-linecap='round' stroke-linejoin='round' d='M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z'/></svg>
  Árbol de Expansión
</h3>
<p style='color:#64748b;font-size:0.875rem;font-family:"Fira Sans",sans-serif;'>Nodos explorados por el algoritmo. El camino azul indica la solución encontrada.</p>
""", unsafe_allow_html=True)
                        arbol = dibujar_arbol_completo(arbol_expansion, ruta, movs)
                        st.graphviz_chart(arbol, use_container_width=True)

                    with col_right:
                        st.markdown("""
<h3 style="display:flex;align-items:center;gap:0.5rem;">
  <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' fill='none' viewBox='0 0 24 24' stroke='#34d399' stroke-width='2' aria-hidden='true'><path stroke-linecap='round' stroke-linejoin='round' d='M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z'/><path stroke-linecap='round' stroke-linejoin='round' d='M21 12a9 9 0 11-18 0 9 9 0 0118 0z'/></svg>
  Secuencia de Movimientos
</h3>
<p style='color:#64748b;font-size:0.875rem;font-family:"Fira Sans",sans-serif;'>Cada paso muestra el movimiento de la ficha hacia el espacio vacío.</p>
""", unsafe_allow_html=True)
                        fig = dibujar_ruta_puzzle(ruta, movs)
                        fig.patch.set_alpha(0.0)
                        st.pyplot(fig, transparent=True)
                else:
                    st.info(
                        f"Se exploraron **{nodos_exp} nodos**. El árbol se omite para mantener el rendimiento "
                        f"(se muestra solo cuando ≤ 50 nodos).",
                        icon="ℹ️"
                    )
                    st.markdown("""
<h3 style="display:flex;align-items:center;justify-content:center;gap:0.5rem;">
  <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' fill='none' viewBox='0 0 24 24' stroke='#34d399' stroke-width='2' aria-hidden='true'><path stroke-linecap='round' stroke-linejoin='round' d='M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z'/><path stroke-linecap='round' stroke-linejoin='round' d='M21 12a9 9 0 11-18 0 9 9 0 0118 0z'/></svg>
  Secuencia de Movimientos
</h3>
<p style='color:#64748b;font-size:0.875rem;text-align:center;font-family:"Fira Sans",sans-serif;'>Cada paso muestra el movimiento de la ficha hacia el espacio vacío.</p>
""", unsafe_allow_html=True)
                    fig = dibujar_ruta_puzzle(ruta, movs)
                    fig.patch.set_alpha(0.0)
                    st.pyplot(fig, transparent=True)
            else:
                st.warning("No se encontró solución con el algoritmo seleccionado.", icon="⚠️")
