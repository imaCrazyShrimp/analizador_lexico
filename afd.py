"""AFD minimizado (7 estados + estado pozo) tal como aparece en el diagrama.

Estados: A (inicial), B (identificador), C (entero), J (tras el punto),
K (decimal), E (operador), F (delimitador) y TR (pozo/trampa).
Finales: B, C, E, F, K.
"""
from tokens import TipoToken

ESTADO_INICIAL = "A"
POZO = "TR"
ESTADOS = ["A", "B", "C", "E", "F", "J", "K", POZO]
ALFABETO = ["L", "D", "_", ".", "O", "DEL"]

# Solo se listan las transiciones dibujadas; toda otra va al pozo TR.
TRANSICIONES = {
    ("A", "L"): "B",
    ("A", "_"): "B",
    ("A", "D"): "C",
    ("A", "O"): "E",
    ("A", "DEL"): "F",

    ("B", "L"): "B",
    ("B", "D"): "B",
    ("B", "_"): "B",

    ("C", "D"): "C",
    ("C", "."): "J",

    ("J", "D"): "K",

    ("K", "D"): "K",
}

# Estado final -> tipo de token que reconoce
FINALES = {
    "B": TipoToken.TOKEN_ID,
    "C": TipoToken.TOKEN_INT,
    "K": TipoToken.TOKEN_FLOAT,
    "E": TipoToken.TOKEN_OP,
    "F": TipoToken.TOKEN_DELIM,
}


class AFD:
    """Motor mínimo: solo sabe moverse entre estados y consultar finales."""

    def __init__(self, transiciones=TRANSICIONES, inicial=ESTADO_INICIAL,
                 finales=FINALES, pozo=POZO):
        self.transiciones = transiciones
        self.inicial = inicial
        self.finales = finales
        self.pozo = pozo

    def mover(self, estado, simbolo):
        return self.transiciones.get((estado, simbolo), self.pozo)

    def es_final(self, estado):
        return estado in self.finales

    def tipo_de(self, estado):
        return self.finales[estado]

    def tabla_transiciones(self):
        """Devuelve (encabezado, filas) de la tabla completa, para mostrarla."""
        encabezado = ["Estado"] + ALFABETO
        filas = []
        for estado in ESTADOS:
            marca = ""
            if estado == self.inicial:
                marca += "→"
            if self.es_final(estado):
                marca += "*"
            fila = [marca + estado]
            for simbolo in ALFABETO:
                fila.append(self.mover(estado, simbolo))
            filas.append(fila)
        return encabezado, filas
