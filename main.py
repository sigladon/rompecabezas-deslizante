from models import es_soluble
from algorithms import ejecutar_astar_puzzle, ejecutar_bfs, ejecutar_iddfs
from visualization import dibujar_ruta_puzzle

def main():
    # Definición de estados
    inicio = (1, 2, 3, 0, 4, 6, 7, 5, 8)
    meta = (1, 2, 3, 4, 5, 6, 7, 8, 0)

    if es_soluble(inicio):
        print("El estado inicial es soluble. Ejecutando algoritmos...\n")
        
        # 1. BFS
        print("--- BFS ---")
        movs_bfs, ruta_bfs, nodos_bfs, costo_bfs = ejecutar_bfs(inicio, meta)
        if movs_bfs is not None:
            print(f"Solución encontrada en {costo_bfs} pasos.")
            print(f"Nodos expandidos (BFS): {nodos_bfs}")
        else:
            print("No se encontró solución con BFS.")

        # 2. IDDFS
        print("\n--- IDDFS ---")
        movs_iddfs, ruta_iddfs, historial_nodos, prof_final = ejecutar_iddfs(inicio, meta)
        if movs_iddfs is not None:
            print(f"Solución encontrada en {len(movs_iddfs)} pasos (Profundidad final: {prof_final}).")
            print(f"Nodos expandidos por nivel: {historial_nodos}")
            print(f"Total nodos expandidos (IDDFS): {sum(historial_nodos)}")
        else:
            print("No se encontró solución con IDDFS.")

        # 3. A* Heurística 1 (Fuera de lugar)
        print("\n--- A* (Fuera de lugar) ---")
        movs_a1, ruta_a1, nodos_a1, costo_a1 = ejecutar_astar_puzzle(inicio, meta, "fuera_lugar")
        if movs_a1 is not None:
            print(f"Solución encontrada en {costo_a1} pasos.")
            print(f"Nodos expandidos (A* Fuera de lugar): {nodos_a1}")
        else:
            print("No se encontró solución con A* (Fuera de lugar).")

        # 4. A* Heurística 2 (Manhattan)
        print("\n--- A* (Manhattan) ---")
        movs_a2, ruta_a2, nodos_a2, costo_a2 = ejecutar_astar_puzzle(inicio, meta, "manhattan")
        if movs_a2 is not None:
            print(f"Solución encontrada en {costo_a2} pasos.")
            print(f"Nodos expandidos (A* Manhattan): {nodos_a2}")
        else:
            print("No se encontró solución con A* (Manhattan).")

        print("\nMostrando visualización de la ruta de A* (Manhattan) en pantalla...")
        if movs_a2 is not None:
            dibujar_ruta_puzzle(ruta_a2, movs_a2)
    else:
        print("El estado inicial es insoluble.")

if __name__ == '__main__':
    main()
