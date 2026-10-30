from dataclasses import dataclass, field
from typing import List

from afd import AFD
from clasificador import Clasificador, es_digito
from tabla_simbolos import TablaSimbolos
from tokens import (ErrorLexico, PALABRAS_RESERVADAS, Token, TipoToken)


@dataclass
class Resultado:
    tokens: List[Token] = field(default_factory=list)
    errores: List[ErrorLexico] = field(default_factory=list)
    tabla: TablaSimbolos = field(default_factory=TablaSimbolos)


class funcion_lex:
    def __init__(self, afd=None, clasificador=None):
        self.afd = afd or AFD()
        self.clasificador = clasificador or Clasificador()

    # ---------- entrada de archivos ----------
    @staticmethod
    def leer_archivo(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(ruta, "r", encoding="latin-1") as f:
                return f.read()

    def analizar_archivo(self, ruta):
        return self.analizar(self.leer_archivo(ruta))

    # ---------- análisis ----------
    def analizar(self, texto):
        resultado = Resultado()
        n = len(texto)
        pos = 0
        linea = 1
        col = 1

        while pos < n:
            c = texto[pos]

            # --- ignorables: los maneja el lexer, no el autómata ---
            if c == "\n":
                linea += 1
                col = 1
                pos += 1
                continue
            if c == " " or c == "\t" or c == "\r":
                pos += 1
                col += 1
                continue
            if c == "/" and pos + 1 < n and texto[pos + 1] == "/":
                while pos < n and texto[pos] != "\n":
                    pos += 1
                    col += 1
                continue

            # --- caracter fuera del alfabeto ---
            if self.clasificador.clasificar(c) is None:
                resultado.errores.append(
                    ErrorLexico("Carácter no reconocido", c, linea, col))
                pos += 1
                col += 1
                continue

            # --- reconocimiento con el AFD (máxima coincidencia) ---
            fin, estado = self._leer_mas_largo(texto, pos)
            tipo = self.afd.tipo_de(estado) if estado is not None else None

            # --- números mal formados ---
            es_numero = tipo in (TipoToken.TOKEN_INT, TipoToken.TOKEN_FLOAT)
            punto_sobrante = es_numero and fin < n and texto[fin] == "."
            if fin is None or punto_sobrante:
                fin_numero = self._fin_de_numero(texto, pos)
                lexema = texto[pos:fin_numero]
                if any(es_digito(x) for x in lexema):
                    mensaje = "Número mal formado"
                else:
                    mensaje = "Punto '.' fuera de un número"
                resultado.errores.append(
                    ErrorLexico(mensaje, lexema, linea, col))
                col += len(lexema)
                pos = fin_numero
                continue

            # --- token válido ---
            lexema = texto[pos:fin]
            if tipo == TipoToken.TOKEN_ID and lexema in PALABRAS_RESERVADAS:
                tipo = PALABRAS_RESERVADAS[lexema]
            if tipo == TipoToken.TOKEN_ID or lexema in PALABRAS_RESERVADAS:
                resultado.tabla.registrar(lexema, tipo, linea, col)
            resultado.tokens.append(Token(tipo, lexema, linea, col))
            col += len(lexema)
            pos = fin

        return resultado

    def _leer_mas_largo(self, texto, inicio):
        estado = self.afd.inicial
        ultimo_fin = None
        ultimo_estado = None
        i = inicio
        while i < len(texto):
            simbolo = self.clasificador.clasificar(texto[i])
            if simbolo is None:
                break
            estado = self.afd.mover(estado, simbolo)
            if estado == self.afd.pozo:
                break
            i += 1
            if self.afd.es_final(estado):
                ultimo_fin = i
                ultimo_estado = estado
        return ultimo_fin, ultimo_estado

    @staticmethod
    def _fin_de_numero(texto, inicio):
        j = inicio
        while j < len(texto) and (es_digito(texto[j]) or texto[j] == "."):
            j += 1
        return j
