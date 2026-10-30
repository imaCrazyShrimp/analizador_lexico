
OPERADORES = ("+", "-", "*", "/", "=")
DELIMITADORES = ("(", ")", ";", "{", "}")


def es_letra(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z")


def es_digito(c):
    return "0" <= c <= "9"


class Clasificador:

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
