from dataclasses import dataclass
from typing import Optional

from tokens import TipoToken, PALABRAS_RESERVADAS, DESCRIPCIONES


@dataclass
class EntradaSimbolo:
    lexema: str
    tipo: TipoToken
    linea: Optional[int] = None      # primera aparición
    columna: Optional[int] = None
    ocurrencias: int = 0

    @property
    def categoria(self):
        return DESCRIPCIONES[self.tipo]


class TablaSimbolos:
    def __init__(self):
        self._entradas = {}
        for lexema, tipo in PALABRAS_RESERVADAS.items():
            self._entradas[lexema] = EntradaSimbolo(lexema, tipo)

    def registrar(self, lexema, tipo, linea, columna):
        entrada = self._entradas.get(lexema)
        if entrada is None:
            entrada = EntradaSimbolo(lexema, tipo)
            self._entradas[lexema] = entrada
        if entrada.linea is None:
            entrada.linea = linea
            entrada.columna = columna
        entrada.ocurrencias += 1

    def entradas(self):
        return list(self._entradas.values())
