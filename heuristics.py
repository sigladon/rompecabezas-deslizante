def heuristica_fuera_lugar(tablero, meta, n=3):
    """H1: Cuenta piezas que no están en su posición final (ignorando el vacío)."""
    count = 0
    for i in range(len(tablero)):
        if tablero[i] != 0 and tablero[i] != meta[i]:
            count += 1
    return count

def heuristica_manhattan(tablero, meta, n=3):
    """H2: Suma de distancias verticales y horizontales de cada pieza a su objetivo."""
    distancia = 0
    for i in range(len(tablero)):
        pieza = tablero[i]
        if pieza != 0:
            # Posición actual
            fila_act, col_act = divmod(i, n)
            # Posición objetivo
            idx_meta = meta.index(pieza)
            fila_meta, col_meta = divmod(idx_meta, n)
            distancia += abs(fila_act - fila_meta) + abs(col_act - col_meta)
    return distancia
