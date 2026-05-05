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
    Estilo de rompecabezas moderno, futurista y dark-mode.
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
        
    # Paleta de colores alineada al design system Light Mode
    color_marco = '#f1f5f9'           # Slate 100 — marco exterior
    color_hueco = '#e2e8f0'           # Slate 200 — fondo interno
    color_ficha = '#2563eb'           # Blue 600 — color principal fichas
    color_ficha_highlight = '#3b82f6' # Blue 500 — borde
    color_texto = '#ffffff'           # Blanco — números sobre ficha
    
    for i, ax in enumerate(axes):
        if i < n:
            tablero = ruta_tableros[i]
            matriz = np.array(tablero).reshape(3, 3)
            
            ax.set_xlim(-0.2, 3.2)
            ax.set_ylim(3.2, -0.2)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Marco exterior redondeado estilo glassmorphism
            marco = FancyBboxPatch((-0.2, -0.2), 3.4, 3.4,
                                   boxstyle="round,pad=0,rounding_size=0.25",
                                   ec="#cbd5e1", fc=color_marco, lw=1, zorder=0)
            ax.add_patch(marco)
            
            # Hueco del puzzle
            fondo_interno = FancyBboxPatch((0, 0), 3, 3,
                                           boxstyle="round,pad=0,rounding_size=0.15",
                                           ec="none", fc=color_hueco, zorder=1)
            ax.add_patch(fondo_interno)
            
            # --- Calcular dirección de la flecha para el hueco ---
            flecha = None
            if i > 0:
                tablero_prev = ruta_tableros[i - 1]
                idx_hueco_prev = tablero_prev.index(0)
                idx_hueco_curr = tablero.index(0)
                fila_prev, col_prev = divmod(idx_hueco_prev, 3)
                fila_curr, col_curr = divmod(idx_hueco_curr, 3)
                # La ficha se movió desde hueco_curr hacia hueco_prev
                # La flecha apunta hacia donde fue la ficha (desde el centro del hueco)
                df = fila_prev - fila_curr
                dc = col_prev - col_curr
                flecha = (fila_curr, col_curr, df, dc)

            # Fichas del puzzle
            for (fila, col), val in np.ndenumerate(matriz):
                if val != 0:
                    # Sombra suave (neon glow)
                    sombra = FancyBboxPatch((col + 0.05, fila + 0.05), 0.9, 0.9,
                                            boxstyle="round,pad=0,rounding_size=0.15",
                                            ec="none", fc='#1d4ed8', alpha=0.4, zorder=2)
                    ax.add_patch(sombra)
                    
                    # Ficha vibrante
                    ficha = FancyBboxPatch((col + 0.05, fila + 0.05), 0.9, 0.9,
                                           boxstyle="round,pad=0,rounding_size=0.15",
                                           ec=color_ficha_highlight, fc=color_ficha, lw=1.5, zorder=3)
                    ax.add_patch(ficha)
                    
                    # Reflejo superior (para dar efecto glass/glossy)
                    reflejo = FancyBboxPatch((col + 0.08, fila + 0.08), 0.84, 0.4,
                                           boxstyle="round,pad=0,rounding_size=0.1",
                                           ec="none", fc='#ffffff', alpha=0.15, zorder=4)
                    ax.add_patch(reflejo)
                    
                    # Número de la ficha
                    ax.text(col + 0.5, fila + 0.5, str(val),
                            ha='center', va='center',
                            fontsize=24, fontweight='bold', color=color_texto,
                            fontfamily='monospace', zorder=5)

            # --- Dibujar flecha ámbar en el hueco vacío ---
            if flecha is not None:
                fila_h, col_h, df, dc = flecha
                cx = col_h + 0.5
                cy = fila_h + 0.5
                mag = 0.28
                # El eje Y de matplotlib está invertido (ylim va de 3.2 a -0.2)
                # por eso dy usa df directamente (fila crece hacia abajo en ambos)
                dx = dc * mag
                dy = df * mag
                ax.annotate(
                    "",
                    xy=(cx + dx, cy + dy),      # punta: hacia donde fue la ficha
                    xytext=(cx - dx, cy - dy),  # cola
                    arrowprops=dict(
                        arrowstyle="->,head_width=0.4,head_length=0.3",
                        color="#f59e0b",
                        lw=2.5,
                    ),
                    zorder=6
                )

            # Título de la acción
            if i == 0:
                ax.set_title("Estado Inicial", pad=12, fontweight='bold', fontsize=12, color="#1e293b", fontfamily='monospace')
            else:
                ax.set_title(f"Paso {i}: {movimientos[i-1]}", pad=12, fontsize=10, color="#475569", fontweight='semibold', fontfamily='sans-serif')
        else:
            ax.axis('off')

    plt.tight_layout()
    return fig
