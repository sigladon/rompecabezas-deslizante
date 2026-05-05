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

def generar_sucesores(tablero):
    sucesores = []
    vacio = tablero.index(0)
    fila, col = divmod(vacio, 3)

    movimientos = {
        "Arriba": (-1, 0), "Abajo": (1, 0),
        "Izquierda": (0, -1), "Derecha": (0, 1)
    }

    for nombre, (df, dc) in movimientos.items():
        n_fila, n_col = fila + df, col + dc
        if 0 <= n_fila < 3 and 0 <= n_col < 3:
            nuevo_idx = n_fila * 3 + n_col
            # Crear nuevo tablero (tupla inmutable)
            lista_tablero = list(tablero)
            lista_tablero[vacio], lista_tablero[nuevo_idx] = lista_tablero[nuevo_idx], lista_tablero[vacio]
            sucesores.append((tuple(lista_tablero), nombre))

    return sucesores

def es_soluble(tablero):
    """
    Cuenta las inversiones en el tablero.
    Un 8-puzzle es soluble si el número de inversiones es par.
    """
    # Convertimos a lista y eliminamos el 0 para contar inversiones
    piezas = [p for p in tablero if p != 0]
    inversiones = 0
    for i in range(len(piezas)):
        for j in range(i + 1, len(piezas)):
            if piezas[i] > piezas[j]:
                inversiones += 1

    return inversiones % 2 == 0
