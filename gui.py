"""Interfaz gráfica (Tkinter): editor, tabla de tokens y consola de errores."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from analizador_lexer import funcion_lex
from afd import AFD


class AplicacionLexer:
    def __init__(self):
        self.lexer = funcion_lex()
        self.resultado = None
        self.ruta = None

        self.root = tk.Tk()
        self.root.title("Analizador Léxico")
        self.root.geometry("1000x760")
        self.root.minsize(760, 560)

        self._crear_menu()
        self._crear_interfaz()

        self.root.bind("<F5>", lambda e: self.analizar())
        self.root.bind("<Control-o>", lambda e: self.abrir_archivo())
        self.root.bind("<Control-s>", lambda e: self.guardar_como())

    # ------------------------------------------------------------ menú
    def _crear_menu(self):
        barra = tk.Menu(self.root)

        m_archivo = tk.Menu(barra, tearoff=0)
        m_archivo.add_command(label="Nuevo", command=self.nuevo)
        m_archivo.add_command(label="Abrir…", accelerator="Ctrl+O",
                              command=self.abrir_archivo)
        m_archivo.add_command(label="Guardar como…", accelerator="Ctrl+S",
                              command=self.guardar_como)
        m_archivo.add_separator()
        m_archivo.add_command(label="Salir", command=self.root.destroy)
        barra.add_cascade(label="Archivo", menu=m_archivo)

        m_analisis = tk.Menu(barra, tearoff=0)
        m_analisis.add_command(label="Analizar", accelerator="F5",
                               command=self.analizar)
        m_analisis.add_command(label="Limpiar resultados",
                               command=self.limpiar_resultados)
        m_analisis.add_separator()
        m_analisis.add_command(label="Ver tabla de transiciones del AFD",
                               command=self.ver_afd)
        barra.add_cascade(label="Análisis Léxico", menu=m_analisis)

        self.root.config(menu=barra)

    # ------------------------------------------------------- interfaz
    def _crear_interfaz(self):
        # barra de estado (abajo)
        self.estado = tk.StringVar(value="Listo")
        self.posicion = tk.StringVar(value="Línea 1, Columna 1")
        barra = ttk.Frame(self.root)
        barra.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(barra, textvariable=self.estado).pack(side=tk.LEFT, padx=6)
        ttk.Label(barra, textvariable=self.posicion).pack(side=tk.RIGHT, padx=6)

        panel = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        panel.pack(fill=tk.BOTH, expand=True, padx=6, pady=(6, 0))

        # 1) editor
        marco_editor = ttk.LabelFrame(panel, text="Editor (código fuente)")
        self.editor = tk.Text(marco_editor, wrap="none", undo=True, height=10,
                              font=("Consolas", 11))
        sy = ttk.Scrollbar(marco_editor, orient=tk.VERTICAL,
                           command=self.editor.yview)
        sx = ttk.Scrollbar(marco_editor, orient=tk.HORIZONTAL,
                           command=self.editor.xview)
        self.editor.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side=tk.RIGHT, fill=tk.Y)
        sx.pack(side=tk.BOTTOM, fill=tk.X)
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.tag_configure("error", background="#ffd6d6", underline=True)
        self.editor.tag_configure("seleccion", background="#fff3a0")
        self.editor.bind("<KeyRelease>", self._actualizar_posicion)
        self.editor.bind("<ButtonRelease-1>", self._actualizar_posicion)
        panel.add(marco_editor, weight=3)

        # 2) resultados (tokens / tabla de símbolos)
        marco_res = ttk.LabelFrame(panel, text="Resultados del análisis")
        pestanas = ttk.Notebook(marco_res)
        pestanas.pack(fill=tk.BOTH, expand=True)

        self.tabla_tokens = self._crear_tabla(
            pestanas, "Tokens",
            [("n", "#", 45), ("lexema", "Lexema", 170),
             ("token", "Token", 140), ("desc", "Descripción", 170),
             ("linea", "Línea", 70), ("col", "Columna", 70)])
        self.tabla_tokens.bind("<<TreeviewSelect>>", self._seleccionar_token)

        self.tabla_simbolos = self._crear_tabla(
            pestanas, "Tabla de símbolos",
            [("lexema", "Lexema", 170), ("token", "Token", 140),
             ("cat", "Categoría", 170), ("pos", "Primera aparición", 140),
             ("veces", "Ocurrencias", 90)])
        panel.add(marco_res, weight=3)

        # 3) consola de errores
        marco_con = ttk.LabelFrame(panel, text="Consola de errores")
        self.consola = tk.Text(marco_con, height=6, state="disabled",
                               font=("Consolas", 10), wrap="none")
        sc = ttk.Scrollbar(marco_con, orient=tk.VERTICAL,
                           command=self.consola.yview)
        self.consola.configure(yscrollcommand=sc.set)
        sc.pack(side=tk.RIGHT, fill=tk.Y)
        self.consola.pack(fill=tk.BOTH, expand=True)
        self.consola.tag_configure("err", foreground="#b00020")
        self.consola.tag_configure("ok", foreground="#1b5e20")
        self.consola.bind("<Double-Button-1>", self._clic_en_consola)
        panel.add(marco_con, weight=1)

        self._errores_por_linea = {}

    def _crear_tabla(self, pestanas, titulo, columnas):
        marco = ttk.Frame(pestanas)
        pestanas.add(marco, text=titulo)
        tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas],
                             show="headings", height=6)
        for clave, texto, ancho in columnas:
            tabla.heading(clave, text=texto)
            tabla.column(clave, width=ancho, anchor=tk.W)
        sb = ttk.Scrollbar(marco, orient=tk.VERTICAL, command=tabla.yview)
        tabla.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        tabla.pack(fill=tk.BOTH, expand=True)
        return tabla

    # --------------------------------------------------------- acciones
    def nuevo(self):
        self.editor.delete("1.0", tk.END)
        self.ruta = None
        self.limpiar_resultados()
        self.estado.set("Documento nuevo")

    def abrir_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Abrir archivo de código",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            texto = funcion_lex.leer_archivo(ruta)
        except OSError as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")
            return
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", texto)
        self.ruta = ruta
        self.root.title(f"Analizador Léxico - {ruta}")
        self.analizar()

    def guardar_como(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", "end-1c"))
        except OSError as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
            return
        self.ruta = ruta
        self.root.title(f"Analizador Léxico - {ruta}")
        self.estado.set("Archivo guardado")

    def analizar(self):
        texto = self.editor.get("1.0", "end-1c")
        self.limpiar_resultados()
        if not texto.strip():
            self.estado.set("No hay texto para analizar")
            return

        self.resultado = self.lexer.analizar(texto)
        r = self.resultado

        for i, t in enumerate(r.tokens):
            self.tabla_tokens.insert(
                "", tk.END, iid=str(i),
                values=(i + 1, t.lexema, t.nombre, t.descripcion,
                        t.linea, t.columna))

        for e in r.tabla.entradas():
            pos = f"{e.linea}:{e.columna}" if e.linea is not None else "—"
            self.tabla_simbolos.insert(
                "", tk.END,
                values=(e.lexema, e.tipo.name, e.categoria, pos, e.ocurrencias))

        self.consola.configure(state="normal")
        if r.errores:
            for i, e in enumerate(r.errores, 1):
                self.consola.insert(tk.END, str(e) + "\n", "err")
                self._errores_por_linea[i] = e
                inicio = f"{e.linea}.{e.columna - 1}"
                fin = f"{e.linea}.{e.columna - 1 + len(e.lexema)}"
                self.editor.tag_add("error", inicio, fin)
            self.consola.insert(
                tk.END, f"\n{len(r.errores)} error(es) léxico(s). "
                        "Doble clic en un error para ubicarlo.\n", "err")
        else:
            self.consola.insert(tk.END, "Sin errores léxicos.\n", "ok")
        self.consola.configure(state="disabled")

        self.estado.set(
            f"{len(r.tokens)} tokens, {len(r.errores)} errores léxicos")

    def limpiar_resultados(self):
        self.resultado = None
        self._errores_por_linea = {}
        for tabla in (self.tabla_tokens, self.tabla_simbolos):
            tabla.delete(*tabla.get_children())
        self.consola.configure(state="normal")
        self.consola.delete("1.0", tk.END)
        self.consola.configure(state="disabled")
        self.editor.tag_remove("error", "1.0", tk.END)
        self.editor.tag_remove("seleccion", "1.0", tk.END)

    def ver_afd(self):
        encabezado, filas = AFD().tabla_transiciones()
        ventana = tk.Toplevel(self.root)
        ventana.title("Tabla de transiciones del AFD")
        tabla = ttk.Treeview(ventana, columns=encabezado, show="headings",
                             height=len(filas))
        for col in encabezado:
            tabla.heading(col, text=col)
            tabla.column(col, width=80, anchor=tk.CENTER)
        for fila in filas:
            tabla.insert("", tk.END, values=fila)
        tabla.pack(padx=10, pady=10)
        ttk.Label(
            ventana,
            text="→ estado inicial   * estado final   TR = estado pozo\n"
                 "L = letra, D = dígito, O = operador, DEL = delimitador"
        ).pack(pady=(0, 10))

    # ------------------------------------------------------- sincronía
    def _resaltar(self, linea, columna, largo):
        self.editor.tag_remove("seleccion", "1.0", tk.END)
        inicio = f"{linea}.{columna - 1}"
        fin = f"{linea}.{columna - 1 + largo}"
        self.editor.tag_add("seleccion", inicio, fin)
        self.editor.see(inicio)

    def _seleccionar_token(self, _evento):
        seleccion = self.tabla_tokens.selection()
        if not seleccion or self.resultado is None:
            return
        t = self.resultado.tokens[int(seleccion[0])]
        self._resaltar(t.linea, t.columna, len(t.lexema))

    def _clic_en_consola(self, evento):
        indice = self.consola.index(f"@{evento.x},{evento.y}")
        numero = int(indice.split(".")[0])
        e = self._errores_por_linea.get(numero)
        if e is not None:
            self._resaltar(e.linea, e.columna, len(e.lexema))

    def _actualizar_posicion(self, _evento=None):
        linea, col = self.editor.index(tk.INSERT).split(".")
        self.posicion.set(f"Línea {linea}, Columna {int(col) + 1}")

    def ejecutar(self):
        self.root.mainloop()
