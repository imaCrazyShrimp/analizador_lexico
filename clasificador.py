"""Convierte un caracter real en un símbolo del alfabeto del AFD.

No se usan expresiones regulares ni métodos como str.isalpha(), porque
estos aceptan letras con acento (ñ, á) y dígitos no ASCII que NO forman
parte del alfabeto definido.
"""

OPERADORES = ("+", "-", "*", "/", "=")
DELIMITADORES = ("(", ")", ";", "{", "}")


def es_letra(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z")


def es_digito(c):
    return "0" <= c <= "9"


class Clasificador:
    """Alfabeto: L (letra), D (dígito), _, ., O (operador), DEL (delimitador)."""

    def clasificar(self, c):
        if es_letra(c):
            return "L"
        if es_digito(c):
            return "D"
        if c == "_":
            return "_"
        if c == ".":
            return "."
        if c in OPERADORES:
            return "O"
        if c in DELIMITADORES:
            return "DEL"
        return None  # fuera del alfabeto
