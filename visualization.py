import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from graphviz import Digraph
from models import generar_sucesores

def format_estado(tablero):
    """Convierte la tupla en un string con formato de matriz 3x3 para Graphviz"""
    t = [str(x) if x != 0 else ' ' for x in tablero]
    return f"{t[0]} | {t[1]} | {t[2]}\n{t[3]} | {t[4]} | {t[5]}\n{t[6]} | {t[7]} | {t[8]}"

def dibujar_arbol_ejemplo(estado_inicial, profundidad_maxima=2):
    dot = Digraph(comment='Árbol de Expansión 8-Puzzle')

    dot.attr('node', shape='box', fontname='Fira Sans', style='filled',
             fillcolor='#2563eb', fontcolor='#f0f9ff', penwidth='0')

    visitados = set()
    cola = [(estado_inicial, None, "Inicio", 0)]
    nodo_id = 0

    while cola:
        actual, id_padre, mov, nivel = cola.pop(0)
        current_id = str(nodo_id)
        nodo_id += 1

        label = f"[{mov}]\n{format_estado(actual)}"
        dot.node(current_id, label)

        if id_padre is not None:
            dot.edge(id_padre, current_id, color="#475569")

        if nivel < profundidad_maxima:
            for sucesor, nombre_mov in generar_sucesores(actual):
                if sucesor not in visitados:
                    cola.append((sucesor, current_id, nombre_mov, nivel + 1))
            visitados.add(actual)

    return dot

def dibujar_ruta_puzzle(ruta_tableros, movimientos):
    """
    Dibuja la secuencia de tableros desde el inicio hasta la meta usando Matplotlib.
    Estilo de rompecabezas moderno, premium y claro (ui-ux-pro-max).
    """
    n = len(ruta_tableros)
    
    cols = min(n, 5)
    rows = (n - 1) // cols + 1
    
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 2.2, rows * 2.6))
    fig.patch.set_alpha(0.0) # Fondo transparente
    
    if rows == 1 and cols == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
        
    color_marco = '#ffffff'
    color_hueco = '#f8fafc'
    color_texto = '#ffffff'
    
    # Matching the exact colors from app.py interactive puzzle
    color_map = {
        1: ('#ef4444', '#dc2626'), # Red
        2: ('#f97316', '#ea580c'), # Orange
        3: ('#f59e0b', '#d97706'), # Amber
        4: ('#10b981', '#059669'), # Emerald
        5: ('#06b6d4', '#0891b2'), # Cyan
        6: ('#3b82f6', '#2563eb'), # Blue
        7: ('#8b5cf6', '#7c3aed'), # Violet
        8: ('#d946ef', '#c026d3'), # Fuchsia
    }
    
    for i, ax in enumerate(axes):
        if i < n:
            tablero = ruta_tableros[i]
            matriz = np.array(tablero).reshape(3, 3)
            
            ax.set_xlim(-0.2, 3.2)
            ax.set_ylim(3.2, -0.2)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Marco exterior
            marco = FancyBboxPatch((-0.2, -0.2), 3.4, 3.4,
                                   boxstyle="round,pad=0,rounding_size=0.3",
                                   ec="#e2e8f0", fc=color_marco, lw=1, zorder=0)
            ax.add_patch(marco)
            
            # Hueco
            fondo_interno = FancyBboxPatch((0, 0), 3, 3,
                                           boxstyle="round,pad=0,rounding_size=0.2",
                                           ec="none", fc=color_hueco, zorder=1)
            ax.add_patch(fondo_interno)
            
            flecha = None
            if i > 0:
                tablero_prev = ruta_tableros[i - 1]
                idx_hueco_prev = tablero_prev.index(0)
                idx_hueco_curr = tablero.index(0)
                fila_prev, col_prev = divmod(idx_hueco_prev, 3)
                fila_curr, col_curr = divmod(idx_hueco_curr, 3)
                df = fila_prev - fila_curr
                dc = col_prev - col_curr
                flecha = (fila_curr, col_curr, df, dc)

            for (fila, col), val in np.ndenumerate(matriz):
                if val != 0:
                    bg_color, border_color = color_map.get(val, ('#94a3b8', '#64748b'))
                    
                    # Sombra
                    sombra = FancyBboxPatch((col + 0.05, fila + 0.05), 0.9, 0.9,
                                            boxstyle="round,pad=0,rounding_size=0.15",
                                            ec="none", fc=bg_color, alpha=0.2, zorder=2)
                    ax.add_patch(sombra)
                    
                    # Ficha
                    ficha = FancyBboxPatch((col + 0.05, fila + 0.05), 0.9, 0.9,
                                           boxstyle="round,pad=0,rounding_size=0.15",
                                           ec=border_color, fc=bg_color, lw=1.5, zorder=3)
                    ax.add_patch(ficha)
                    
                    # Reflejo
                    reflejo = FancyBboxPatch((col + 0.08, fila + 0.08), 0.84, 0.35,
                                           boxstyle="round,pad=0,rounding_size=0.1",
                                           ec="none", fc='#ffffff', alpha=0.15, zorder=4)
                    ax.add_patch(reflejo)
                    
                    # Número
                    ax.text(col + 0.5, fila + 0.5, str(val),
                            ha='center', va='center',
                            fontsize=24, fontweight='bold', color=color_texto,
                            fontfamily='monospace', zorder=5)

            if flecha is not None:
                fila_h, col_h, df, dc = flecha
                cx = col_h + 0.5
                cy = fila_h + 0.5
                mag = 0.28
                dx = dc * mag
                dy = df * mag
                ax.annotate(
                    "",
                    xy=(cx + dx, cy + dy),
                    xytext=(cx - dx, cy - dy),
                    arrowprops=dict(
                        arrowstyle="->,head_width=0.4,head_length=0.3",
                        color="#94a3b8", # Color neutral para la flecha
                        lw=2.5,
                    ),
                    zorder=6
                )

            if i == 0:
                ax.set_title("Estado Inicial", pad=12, fontweight='bold', fontsize=12, color="#0f172a", fontfamily='sans-serif')
            else:
                ax.set_title(f"Paso {i}: {movimientos[i-1]}", pad=12, fontsize=11, color="#475569", fontweight='semibold', fontfamily='sans-serif')
        else:
            ax.axis('off')

    plt.tight_layout()
    return fig
