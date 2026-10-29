"""Punto de entrada.

  python main.py              -> abre la interfaz gráfica
  python main.py archivo.txt  -> analiza el archivo e imprime en consola
"""
import sys

from analizador_lexer import funcion_lex


def modo_consola(ruta):
    resultado = funcion_lex().analizar_archivo(ruta)
    print(f"{'Lexema':<16}{'Token':<14}{'Descripción':<20}{'Línea':>6}{'Col':>5}")
    print("-" * 61)
    for t in resultado.tokens:
        print(f"{t.lexema:<16}{t.nombre:<14}{t.descripcion:<20}"
              f"{t.linea:>6}{t.columna:>5}")
    print()
    for e in resultado.errores:
        print(e)
    print(f"\n{len(resultado.tokens)} tokens, {len(resultado.errores)} errores")


def main():
    if len(sys.argv) > 1:
        modo_consola(sys.argv[1])
    else:
        from gui import AplicacionLexer
        AplicacionLexer().ejecutar()


if __name__ == "__main__":
    main()
