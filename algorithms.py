import heapq
import collections
from heuristics import heuristica_manhattan, heuristica_fuera_lugar
from models import generar_sucesores

def ejecutar_bfs(estado_inicial, estado_meta):
    # Se analiza el nodo inicial
    if estado_inicial == estado_meta:
        return [], [estado_inicial], 0, 0, []

    # La cola guarda: (actual, movs, tableros)
    cola = collections.deque([(estado_inicial, [], [estado_inicial])])
    visitados = set([estado_inicial])
    nodos_expandidos = 0
    arbol_expansion = {} # Diccionario para preservar el orden cronológico estricto

    while cola:
        # Se analiza el nodo actual (lo sacamos de la cola)
        actual, movs, tableros = cola.popleft()
        nodos_expandidos += 1

        # Expande a sus hijos sin incluir los que ya se hayan analizado
        for vecino_tablero, mov_nombre in generar_sucesores(actual):
            if vecino_tablero not in visitados:
                visitados.add(vecino_tablero)
                
                # Se analiza el hijo si es solución o no
                if vecino_tablero == estado_meta:
                    # Si es solución, se añade al árbol y termina inmediatamente
                    arbol_expansion[(actual, vecino_tablero, mov_nombre)] = None
                    return movs + [mov_nombre], tableros + [vecino_tablero], nodos_expandidos, len(movs) + 1, list(arbol_expansion.keys())
                
                # De no serlo, se añade al árbol visual como nodo analizado/recorrido
                arbol_expansion[(actual, vecino_tablero, mov_nombre)] = None
                
                # Y los mete a la cola para seguir buscando
                cola.append((vecino_tablero, movs + [mov_nombre], tableros + [vecino_tablero]))

    return None, None, nodos_expandidos, 0, list(arbol_expansion.keys())

def ejecutar_astar_puzzle(estado_inicial, estado_meta, tipo_heuristica="manhattan"):
    func_h = heuristica_manhattan if tipo_heuristica == "manhattan" else heuristica_fuera_lugar

    # La cola guarda: (f, g, actual, movs, tableros)
    open_list = [(func_h(estado_inicial, estado_meta), 0, estado_inicial, [], [estado_inicial])]
    visitados = {}
    nodos_expandidos = 0
    arbol_expansion = {} # Diccionario para preservar el orden cronológico

    while open_list:
        f, g, actual, movs, tableros = heapq.heappop(open_list)

        if actual in visitados and visitados[actual] <= g:
            continue
        visitados[actual] = g
        nodos_expandidos += 1

        if actual == estado_meta:
            return movs, tableros, nodos_expandidos, g, list(arbol_expansion.keys())

        for vecino_tablero, mov_nombre in generar_sucesores(actual):
            nuevo_g = g + 1
            if vecino_tablero not in visitados or nuevo_g < visitados.get(vecino_tablero, float('inf')):
                h_val = func_h(vecino_tablero, estado_meta)
                nuevo_f = nuevo_g + h_val
                
                # Agregamos al árbol visual TODAS las posibilidades en cuanto se generan
                # Incluimos f, g y h en el nombre del movimiento para visualización
                etiqueta_mov = f"{mov_nombre}\n(f={nuevo_f}, g={nuevo_g}, h={h_val})"
                arbol_expansion[(actual, vecino_tablero, etiqueta_mov)] = None
                
                heapq.heappush(open_list, (nuevo_f, nuevo_g, vecino_tablero,
                                           movs + [mov_nombre], tableros + [vecino_tablero]))

    return None, None, nodos_expandidos, 0, list(arbol_expansion.keys())

def ejecutar_iddfs(estado_inicial, estado_meta, max_profundidad=30):
    """Búsqueda de Profundidad Iterativa (Estrictamente Iterativa)"""
    historial_nodos_por_nivel = []
    
    # Diccionario para preservar el orden exacto de exploración
    arbol_expansion = {}

    for limite in range(max_profundidad):
        # Pila guarda: (actual, movs, tableros, prof, visitados_rama)
        pila = [(estado_inicial, [], [estado_inicial], 0, {estado_inicial})]
        nodos_expandidos = 0
        encontrado = False
        resultado = None

        while pila:
            actual, movs, tableros, prof, visitados_rama = pila.pop()
            nodos_expandidos += 1

            if actual == estado_meta:
                resultado = (movs, tableros)
                encontrado = True
                break

            if prof < limite:
                sucesores = generar_sucesores(actual)
                for vecino, mov_nombre in reversed(sucesores):
                    if vecino not in visitados_rama:
                        # Agregamos todas las posibilidades generadas al árbol visual
                        arbol_expansion[(actual, vecino, mov_nombre)] = None
                        
                        nuevos_visitados = visitados_rama.copy()
                        nuevos_visitados.add(vecino)
                        pila.append((vecino, movs + [mov_nombre], tableros + [vecino], prof + 1, nuevos_visitados))
        
        historial_nodos_por_nivel.append(nodos_expandidos)

        if encontrado:
            return resultado[0], resultado[1], historial_nodos_por_nivel, limite, list(arbol_expansion.keys())

    return None, None, historial_nodos_por_nivel, max_profundidad, list(arbol_expansion.keys())
