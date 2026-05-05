from dataclasses import dataclass, field

@dataclass(frozen=True, order=True)
class EstadoPuzzle:
    tablero: tuple  # Tupla de 9 elementos (0 para el espacio vacío)
    g: int = 0      # Costo acumulado
    h: int = 0      # Valor heurístico
    padre: 'EstadoPuzzle' = field(default=None, compare=False)
    movimiento: str = field(default="", compare=False)

    @property
    def f(self):
        return self.g + self.h

    def __post_init__(self):
        # El tablero debe ser una tupla para ser "hasheable" en el set de visitados
        pass

def generar_sucesores(tablero, n=3):
    """Genera sucesores intercambiando el vacío (0) con piezas adyacentes.
    
    Args:
        tablero: Tupla de n*n elementos representando el puzzle
        n: Tamaño del puzzle (3 para 3x3, 4 para 4x4, 5 para 5x5, etc.)
    """
    sucesores = []
    vacio = tablero.index(0)
    fila, col = divmod(vacio, n)

    movimientos = {
        "Arriba": (-1, 0), "Abajo": (1, 0),
        "Izquierda": (0, -1), "Derecha": (0, 1)
    }

    for nombre, (df, dc) in movimientos.items():
        n_fila, n_col = fila + df, col + dc
        if 0 <= n_fila < n and 0 <= n_col < n:
            nuevo_idx = n_fila * n + n_col
            # Crear nuevo tablero (tupla inmutable)
            lista_tablero = list(tablero)
            lista_tablero[vacio], lista_tablero[nuevo_idx] = lista_tablero[nuevo_idx], lista_tablero[vacio]
            sucesores.append((tuple(lista_tablero), nombre))

    return sucesores

def es_soluble(tablero, n=3):
    """
    Verifica si un puzzle n×n es soluble.
    Para n impar: soluble si inversiones es par
    Para n par: soluble si (inversiones + fila_vacío contando desde abajo) es impar
    """
    piezas = [p for p in tablero if p != 0]
    inversiones = 0
    for i in range(len(piezas)):
        for j in range(i + 1, len(piezas)):
            if piezas[i] > piezas[j]:
                inversiones += 1

    # Para tableros con n par, suma inversiones + fila de vacío
    if n % 2 == 0:
        vacio = tablero.index(0)
        fila_vacio = divmod(vacio, n)[0]
        return (inversiones + fila_vacio) % 2 == 1
    else:
        return inversiones % 2 == 0
