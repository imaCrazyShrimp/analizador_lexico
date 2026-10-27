"""Definición de tokens, palabras reservadas y errores léxicos."""
from dataclasses import dataclass
from enum import Enum, auto


class TipoToken(Enum):
    """Tipos de token. El nombre del miembro es el nombre oficial del token."""
    TOKEN_VAR = auto()
    TOKEN_PRINT = auto()
    TOKEN_IF = auto()
    TOKEN_ELSE = auto()
    TOKEN_ID = auto()
    TOKEN_INT = auto()
    TOKEN_FLOAT = auto()
    TOKEN_OP = auto()
    TOKEN_DELIM = auto()


# Descripción en español que se muestra en la interfaz
DESCRIPCIONES = {
    TipoToken.TOKEN_VAR: "Palabra reservada",
    TipoToken.TOKEN_PRINT: "Palabra reservada",
    TipoToken.TOKEN_IF: "Palabra reservada",
    TipoToken.TOKEN_ELSE: "Palabra reservada",
    TipoToken.TOKEN_ID: "Identificador",
    TipoToken.TOKEN_INT: "Número entero",
    TipoToken.TOKEN_FLOAT: "Número decimal",
    TipoToken.TOKEN_OP: "Operador",
    TipoToken.TOKEN_DELIM: "Delimitador",
}

# Palabras reservadas: el AFD las reconoce como identificadores y el
# analizador consulta este diccionario después de aceptar un identificador.
PALABRAS_RESERVADAS = {
    "var": TipoToken.TOKEN_VAR,
    "print": TipoToken.TOKEN_PRINT,
    "if": TipoToken.TOKEN_IF,
    "else": TipoToken.TOKEN_ELSE,
}


@dataclass(frozen=True)
class Token:
    tipo: TipoToken
    lexema: str
    linea: int
    columna: int

    @property
    def nombre(self):
        return self.tipo.name

    @property
    def descripcion(self):
        return DESCRIPCIONES[self.tipo]


@dataclass(frozen=True)
class ErrorLexico:
    mensaje: str
    lexema: str
    linea: int
    columna: int

    def __str__(self):
        return (f"[Línea {self.linea}, Columna {self.columna}] "
                f"{self.mensaje}: '{self.lexema}'")
