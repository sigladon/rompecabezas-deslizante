import heapq
import collections
from heuristics import heuristica_manhattan, heuristica_fuera_lugar
from models import generar_sucesores

def ejecutar_bfs(estado_inicial, estado_meta, n=3):
    # Se analiza el nodo inicial
    if estado_inicial == estado_meta:
        return [], [estado_inicial], 0, 0, []

    # La cola guarda: (actual, movs, tableros)
    cola = collections.deque([(estado_inicial, [], [estado_inicial])])
    visitados = set([estado_inicial])
    nodos_expandidos = 0

    while cola:
        # Se analiza el nodo actual (lo sacamos de la cola)
        actual, movs, tableros = cola.popleft()
        nodos_expandidos += 1

        # Expande a sus hijos sin incluir los que ya se hayan analizado
        for vecino_tablero, mov_nombre in generar_sucesores(actual, n):
            if vecino_tablero not in visitados:
                visitados.add(vecino_tablero)
                
                # Se analiza el hijo si es solución o no
                if vecino_tablero == estado_meta:
                    # Si es solución, termina inmediatamente
                    return movs + [mov_nombre], tableros + [vecino_tablero], nodos_expandidos, len(movs) + 1, []
                
                # Y los mete a la cola para seguir buscando
                cola.append((vecino_tablero, movs + [mov_nombre], tableros + [vecino_tablero]))

    return None, None, nodos_expandidos, 0, []

def ejecutar_astar_puzzle(estado_inicial, estado_meta, tipo_heuristica="manhattan", n=3):
    func_h = heuristica_manhattan if tipo_heuristica == "manhattan" else heuristica_fuera_lugar

    # La cola guarda: (f, g, actual, movs, tableros)
    open_list = [(func_h(estado_inicial, estado_meta, n), 0, estado_inicial, [], [estado_inicial])]
    visitados = {}
    nodos_expandidos = 0

    while open_list:
        f, g, actual, movs, tableros = heapq.heappop(open_list)

        if actual in visitados and visitados[actual] <= g:
            continue
        visitados[actual] = g
        nodos_expandidos += 1

        if actual == estado_meta:
            return movs, tableros, nodos_expandidos, g, []

        for vecino_tablero, mov_nombre in generar_sucesores(actual, n):
            nuevo_g = g + 1
            if vecino_tablero not in visitados or nuevo_g < visitados.get(vecino_tablero, float('inf')):
                h_val = func_h(vecino_tablero, estado_meta, n)
                nuevo_f = nuevo_g + h_val
                
                heapq.heappush(open_list, (nuevo_f, nuevo_g, vecino_tablero,
                                           movs + [mov_nombre], tableros + [vecino_tablero]))

    return None, None, nodos_expandidos, 0, []

def ejecutar_iddfs(estado_inicial, estado_meta, max_profundidad=30, n=3):
    """
    IDDFS iterativo sin recursión (O(profundidad) en memoria).
    
    Implementación:
    - Usa una pila explícita para simular la búsqueda en profundidad
    - Mantiene cache de sucesores y índice de procesamiento por nodo
    - Backtracking manual en camino_movs y camino_tableros
    """
    
    historial_nodos_por_nivel = []
    
    for limite in range(max_profundidad):
        visitados_rama = set([estado_inicial])
        camino_movs = []
        camino_tableros = [estado_inicial]
        nodos_expandidos = 0
        encontrado = False
        
        # Pila para DFS iterativo: (nodo, profundidad)
        pila = [(estado_inicial, 0)]
        sucesores_procesados = {}  # nodo -> (sucesores, índice_actual)
        
        while pila and not encontrado:
            nodo_actual, profundidad = pila[-1]
            
            # Primera visita a este nodo en esta rama/límite
            if nodo_actual not in sucesores_procesados:
                nodos_expandidos += 1
                
                if nodo_actual == estado_meta:
                    encontrado = True
                    break
                
                if profundidad < limite:
                    # Generar sucesores
                    sucesores = generar_sucesores(nodo_actual, n)
                    sucesores_procesados[nodo_actual] = (sucesores, 0)
                    
                    # Si no hay sucesores, hacer backtrack inmediatamente
                    if len(sucesores) == 0:
                        pila.pop()
                        sucesores_procesados.pop(nodo_actual, None)
                        # Backtrack en camino (excepto el estado inicial)
                        if nodo_actual != estado_inicial:
                            if camino_tableros and camino_tableros[-1] == nodo_actual:
                                visitados_rama.discard(camino_tableros.pop())
                                if camino_movs:
                                    camino_movs.pop()
                else:
                    # Profundidad máxima alcanzada, hacer backtrack
                    pila.pop()
                    sucesores_procesados.pop(nodo_actual, None)
                    if nodo_actual != estado_inicial:
                        if camino_tableros and camino_tableros[-1] == nodo_actual:
                            visitados_rama.discard(camino_tableros.pop())
                            if camino_movs:
                                camino_movs.pop()
            else:
                # Ya fue visitado, procesar siguiente sucesor
                sucesores, idx = sucesores_procesados[nodo_actual]
                
                if idx < len(sucesores):
                    # Procesar el siguiente sucesor
                    vecino, mov_nombre = sucesores[idx]
                    sucesores_procesados[nodo_actual] = (sucesores, idx + 1)
                    
                    if vecino not in visitados_rama:
                        visitados_rama.add(vecino)
                        camino_movs.append(mov_nombre)
                        camino_tableros.append(vecino)
                        pila.append((vecino, profundidad + 1))
                else:
                    # Todos los sucesores fueron procesados, hacer backtrack
                    pila.pop()
                    sucesores_procesados.pop(nodo_actual, None)
                    if nodo_actual != estado_inicial:
                        if camino_tableros and camino_tableros[-1] == nodo_actual:
                            visitados_rama.discard(camino_tableros.pop())
                            if camino_movs:
                                camino_movs.pop()
        
        historial_nodos_por_nivel.append(nodos_expandidos)
        
        if encontrado:
            total_nodos = sum(historial_nodos_por_nivel)
            return list(camino_movs), list(camino_tableros), total_nodos, len(camino_movs), []
    
    total_nodos = sum(historial_nodos_por_nivel) if historial_nodos_por_nivel else 0
    return None, None, total_nodos, 0, []