# ---------------------------------------------
# Analizador Sintáctico LL(1) - Proyecto Corte 2
# - INDENT/DEDENT obligatorios (def/if/elif/else/class/for)
# - Tras ':' salta NEWLINE(s) antes de exigir INDENT (maneja comentarios/blank lines)
# - Errores de indentación: "<fila,columna>Error sintactico: falla de indentacion"
# - Soporta elif, for-in, asignaciones múltiples, llamadas a función, listas, etc.
# - Guarda salida también en "salida parser.txt"
# ---------------------------------------------

class ParseError(Exception):
    pass


def cargar_tokens(nombre_archivo):
    tokens = []
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            datos = line[1:-1].split(",")
            tipo = datos[0].strip()
            lexema = datos[1].strip() if len(datos) > 3 else ""
            linea = int(datos[-2]);
            columna = int(datos[-1])
            tokens.append({"type": tipo, "lexeme": lexema, "line": linea, "col": columna})
    if not tokens or tokens[-1]["type"] != "EOF":
        last_line = tokens[-1]["line"] if tokens else 1
        last_col = (tokens[-1]["col"] + 1) if tokens else 1
        tokens.append({"type": "EOF", "lexeme": "", "line": last_line, "col": last_col})
    return tokens


class Parser:
    OP_TYPES = {
        "tk_suma", "tk_resta", "tk_mult", "tk_div", "tk_mod",
        "tk_igualdad", "tk_distinto", "tk_mayor", "tk_menor", "tk_mayor_igual", "tk_menor_igual"
    }
    TYPE_STARTERS = {"id", "int", "str", "float", "bool", "tk_cor_izq"}

    # --- NUEVO ---
    # Define qué tokens pueden iniciar una expresión (excepto 'id', que se maneja por separado)
    EXPR_STARTERS = {"tk_entero", "tk_cadena", "True", "False", "None", "tk_par_izq", "tk_cor_izq"}

    # --- FIN NUEVO ---

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.logs = []

    def emit(self, msg: str):
        print(msg)
        self.logs.append(msg)

    def actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]

    def avanzar(self):
        tok = self.actual();
        self.pos += 1;
        return tok

    def coincidir(self, *esperados):
        tok = self.actual()
        if tok["type"] in esperados or tok["lexeme"] in esperados:
            return self.avanzar()
        self.error(tok, esperados)

    # --------- Errores ----------
    def error(self, tok, esperados):
        linea, columna = tok["line"], tok["col"]
        enc = tok["lexeme"] if tok["lexeme"] else tok["type"]
        esp = ", ".join(esperados)
        self.emit(f"<{linea},{columna}> Error sintactico: se encontro: “{enc}”; se esperaba: “{esp}”.")
        raise ParseError()

    def error_custom(self, linea, columna, encontrado, esperado):
        self.emit(f"<{linea},{columna}> Error sintactico: se encontro: “{encontrado}”; se esperaba: “{esperado}”.")
        raise ParseError()

    def indent_error(self, tok):
        self.emit(f"<{tok['line']},{tok['col']}>Error sintactico: falla de indentacion")
        raise ParseError()

    # ---------------------------------------------
    # Programa
    # ---------------------------------------------
    def parse_programa(self):
        try:
            while self.actual()["type"] != "EOF":
                self.parse_sentencia()
            self.coincidir("EOF")
            self.emit(" Análisis sintáctico finalizado correctamente.")
        except ParseError:
            pass

    def parse_sentencia(self):
        t = self.actual()["type"]

        if t in ("INDENT", "DEDENT"):
            self.indent_error(self.actual())

        if t in ("import", "from"):
            self.parse_import()
        elif t == "class":
            self.parse_class_decl()
        elif t == "def":
            self.parse_func_decl()
        elif t == "if":
            self.parse_if_stmt()
        elif t == "else":
            self.parse_else_stmt_error()
        elif t == "elif":
            self.error(self.actual(), ["if"])
        elif t == "for":
            self.parse_for_stmt()
        # --- NUEVO ---
        elif t == "while":
            self.parse_while_stmt()
        # --- FIN NUEVO ---
        elif t == "return":
            self.parse_return_stmt()
        # --- NUEVO ---
        elif t == "yield":
            self.parse_yield_stmt()
        # --- FIN NUEVO ---
        elif t == "print":
            self.parse_print_stmt()

        # --- MODIFICADO ---
        elif t == "id":
            # 'id' puede ser el inicio de una asignación O de una expresión (ej. llamada de función)
            self.parse_assign_or_expr_stmt()

        elif t in self.EXPR_STARTERS:
            # Es una expresión-sentencia que no empieza con 'id'
            # (ej. un docstring 'tk_cadena', o una lista '[1,2]')
            self.parse_expresion()
            if self.actual()["type"] == "NEWLINE": self.coincidir("NEWLINE")
        # --- FIN MODIFICADO ---

        elif t == "NEWLINE":
            self.coincidir("NEWLINE")
        else:
            # --- MODIFICADO ---
            # Añadir los nuevos 'esperados' al mensaje de error
            esperados = ["import", "class", "def", "if", "for", "while", "print", "id", "return", "yield",
                         "NEWLINE"] + list(self.EXPR_STARTERS)
            self.error(self.actual(), esperados)

    # ---------------------------------------------
    # import / from ... import ...
    # ---------------------------------------------
    def parse_import(self):
        if self.actual()["type"] == "import":
            self.coincidir("import");
            self.coincidir("id")
            while self.actual()["type"] == "tk_coma":
                self.coincidir("tk_coma");
                self.coincidir("id")
        else:
            self.coincidir("from");
            self.coincidir("id");
            self.coincidir("import");
            self.coincidir("id")
            while self.actual()["type"] == "tk_coma":
                self.coincidir("tk_coma");
                self.coincidir("id")
        if self.actual()["type"] == "NEWLINE": self.coincidir("NEWLINE")

    # ---------------------------------------------
    # class Nombre([Padre]):
    # ---------------------------------------------
    def parse_class_decl(self):
        self.coincidir("class");
        self.coincidir("id")
        if self.actual()["type"] == "tk_par_izq":
            self.coincidir("tk_par_izq");
            self.coincidir("id");
            self.coincidir("tk_par_der")
        self.coincidir("tk_dos_puntos")
        self.parse_suite()

    # ---------------------------------------------
    # def nombre(params):
    # ---------------------------------------------
    def parse_func_decl(self):
        self.coincidir("def");
        self.coincidir("id");
        self.coincidir("tk_par_izq")
        if self.actual()["type"] not in ("tk_par_der", "EOF"):
            self.parse_param()
            while self.actual()["type"] == "tk_coma":
                self.coincidir("tk_coma")
                if self.actual()["type"] in ("tk_par_der", "EOF"): break
                self.parse_param()
        self.coincidir("tk_par_der")
        self.coincidir("tk_dos_puntos")
        self.parse_suite()

    def parse_param(self):
        self.coincidir("id")
        if self.actual()["type"] == "tk_dos_puntos":
            colon_tok = self.actual();
            self.coincidir("tk_dos_puntos")
            if self.actual()["type"] not in self.TYPE_STARTERS:
                self.error_custom(colon_tok["line"], colon_tok["col"], "tk_dos_puntos", "tk_par_der")
            self.parse_type()

    # ---------------------------------------------
    # Tipos (con [] y sin coma final)
    # ---------------------------------------------
    def parse_type(self):
        t = self.actual()["type"]
        if t in ("id", "int", "str", "float", "bool"):
            self.avanzar()
            if self.actual()["type"] == "tk_cor_izq":
                self._parse_brackets_no_trailing_comma()
        elif t == "tk_cor_izq":
            self._parse_brackets_no_trailing_comma()
        else:
            self.error(self.actual(), ["id", "int", "str", "float", "bool", "tk_cor_izq"])

    def _parse_brackets_no_trailing_comma(self):
        self.coincidir("tk_cor_izq")
        self.parse_type()
        while self.actual()["type"] == "tk_coma":
            coma_tok = self.actual();
            self.coincidir("tk_coma")
            if self.actual()["type"] == "tk_cor_der":
                self.error_custom(coma_tok["line"], max(1, coma_tok["col"] - 1), ",", "]")
            self.parse_type()
        self.coincidir("tk_cor_der")

    # ---------------------------------------------
    # suite -> NEWLINE (NEWLINE)* INDENT (sentencia)+ DEDENT
    # ---------------------------------------------
    def parse_suite(self):
        self.coincidir("NEWLINE")
        # SALTAR líneas en blanco o SOLO comentario (tu lexer emite NEWLINE)
        while self.actual()["type"] == "NEWLINE":
            self.coincidir("NEWLINE")

        if self.actual()["type"] != "INDENT":
            self.indent_error(self.actual())
        self.coincidir("INDENT")

        if self.actual()["type"] in ("DEDENT", "EOF"):
            self.indent_error(self.actual())

        self.parse_sentencia()
        while self.actual()["type"] not in ("DEDENT", "EOF"):
            self.parse_sentencia()

        if self.actual()["type"] == "EOF":
            self.indent_error(self.actual())
        self.coincidir("DEDENT")

    # ---------------------------------------------
    # if / elif* / else?
    # ---------------------------------------------
    def parse_if_stmt(self):
        self.coincidir("if")
        if self.actual()["type"] == "tk_par_izq":
            self.coincidir("tk_par_izq");
            self.parse_expresion();
            self.coincidir("tk_par_der")
        else:
            self.parse_expresion()
        self.coincidir("tk_dos_puntos")
        self.parse_suite()

        while self.actual()["type"] == "elif":
            self.coincidir("elif")
            if self.actual()["type"] == "tk_par_izq":
                self.coincidir("tk_par_izq");
                self.parse_expresion();
                self.coincidir("tk_par_der")
            else:
                self.parse_expresion()
            self.coincidir("tk_dos_puntos")
            self.parse_suite()

        if self.actual()["type"] == "else":
            self.coincidir("else");
            self.coincidir("tk_dos_puntos")
            self.parse_suite()

    def parse_else_stmt_error(self):
        self.error(self.actual(), ["if"])

    # ---------------------------------------------
    # for target_list in expr : suite
    # ---------------------------------------------
    def parse_for_stmt(self):
        self.coincidir("for")
        self.parse_target_list()
        self.coincidir("in")
        self.parse_expresion()
        self.coincidir("tk_dos_puntos")
        self.parse_suite()

    def parse_target_list(self):
        if self.actual()["type"] == "tk_par_izq":
            self.coincidir("tk_par_izq")
            self.coincidir("id")
            while self.actual()["type"] == "tk_coma":
                self.coincidir("tk_coma");
                self.coincidir("id")
            self.coincidir("tk_par_der")
        else:
            self.coincidir("id")
            while self.actual()["type"] == "tk_coma":
                self.coincidir("tk_coma");
                self.coincidir("id")

    # ---------------------------------------------
    # while expr : suite
    # ---------------------------------------------
    def parse_while_stmt(self):
        self.coincidir("while")
        self.parse_expresion()
        self.coincidir("tk_dos_puntos")
        self.parse_suite()

    # ---------------------------------------------
    # return
    # ---------------------------------------------
    def parse_return_stmt(self):
        self.coincidir("return")
        if self.actual()["type"] not in ("NEWLINE", "DEDENT", "EOF"):
            self.parse_expresion()
        if self.actual()["type"] == "NEWLINE": self.coincidir("NEWLINE")

    # ---------------------------------------------
    # yield <expr>
    # ---------------------------------------------
    def parse_yield_stmt(self):
        self.coincidir("yield")
        if self.actual()["type"] not in ("NEWLINE", "DEDENT", "EOF"):
            self.parse_expresion()
        if self.actual()["type"] == "NEWLINE": self.coincidir("NEWLINE")

    # ---------------------------------------------
    # print(...)
    # ---------------------------------------------
    def parse_print_stmt(self):
        self.coincidir("print");
        self.coincidir("tk_par_izq");
        self.parse_expresion();
        self.coincidir("tk_par_der")
        if self.actual()["type"] == "NEWLINE": self.coincidir("NEWLINE")

    # ---------------------------------------------
    # Asignación o Sentencia de Expresión (que empieza con 'id')
    # ---------------------------------------------

    # --- MODIFICADO ---
    # Renombrada de 'parse_assign_stmt'
    def parse_assign_or_expr_stmt(self):
        self.coincidir("id")  # Consume el primer 'id'

        if self.actual()["type"] == "tk_dos_puntos":
            # Asignación con type hint: id: type = ...
            self.coincidir("tk_dos_puntos");
            self.parse_type()
            self.coincidir("tk_asig");
            self.parse_expr_list()
        elif self.actual()["type"] == "tk_coma":
            # Asignación múltiple: id, id, ... = ...
            while self.actual()["type"] == "tk_coma":
                self.coincidir("tk_coma");
                self.coincidir("id")
            self.coincidir("tk_asig");
            self.parse_expr_list()
        elif self.actual()["type"] == "tk_asig":
            # Asignación simple: id = ...
            self.coincidir("tk_asig");
            self.parse_expr_list()
        else:
            # NO es una asignación. Es una EXPRESIÓN que empezó con 'id'.
            # El 'id' ya fue consumido.

            # Replicar la cola de parse_termino (para llamadas de función)
            while self.actual()["type"] == "tk_par_izq":  # id(...)
                self._parse_call_args()

            # Replicar la cola de parse_expresion (para operadores)
            while self.actual()["type"] in self.OP_TYPES:  # id(...) + ...
                self.avanzar()
                self.parse_termino()
        # --- FIN MODIFICADO ---

        if self.actual()["type"] == "NEWLINE": self.coincidir("NEWLINE")

    def parse_expr_list(self):
        self.parse_expresion()
        while self.actual()["type"] == "tk_coma":
            self.coincidir("tk_coma");
            self.parse_expresion()

    # ---------------------------------------------
    # Expresiones (asociación izquierda)
    # ---------------------------------------------
    def parse_expresion(self):
        self.parse_termino()
        while self.actual()["type"] in self.OP_TYPES:
            self.avanzar()
            self.parse_termino()

    def parse_termino(self):
        t = self.actual()["type"]
        if t == "id":
            self.coincidir("id")
            while self.actual()["type"] == "tk_par_izq":
                self._parse_call_args()
        elif t in ("tk_entero", "tk_cadena"):
            self.avanzar()
        elif t in ("True", "False", "None"):
            self.avanzar()
        elif t == "tk_par_izq":
            self.coincidir("tk_par_izq");
            self.parse_expresion();
            self.coincidir("tk_par_der")
        elif t == "tk_cor_izq":
            self.coincidir("tk_cor_izq")
            if self.actual()["type"] != "tk_cor_der":
                self.parse_expresion()
                while self.actual()["type"] == "tk_coma":
                    self.coincidir("tk_coma")
                    if self.actual()["type"] == "tk_cor_der": break
                    self.parse_expresion()
            self.coincidir("tk_cor_der")
        else:
            self.error(self.actual(),
                       ["id", "tk_entero", "tk_cadena", "True", "False", "None", "tk_par_izq", "tk_cor_izq"])

    def _parse_call_args(self):
        self.coincidir("tk_par_izq")
        if self.actual()["type"] != "tk_par_der":
            self.parse_expresion()
            while self.actual()["type"] == "tk_coma":
                self.coincidir("tk_coma")
                if self.actual()["type"] == "tk_par_der": break
                self.parse_expresion()
            if self.actual()["type"] != "tk_par_der":
                self.error(self.actual(), ["tk_coma", "tk_par_der"])
        self.coincidir("tk_par_der")


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
if __name__ == "__main__":
    tokens = cargar_tokens("salida_tokens.txt")
    parser = Parser(tokens)
    try:
        parser.parse_programa()
    finally:
        with open("salida parser.txt", "w", encoding="utf-8") as out:
            if parser.logs:
                out.write("\n".join(parser.logs) + "\n")
            else:
                out.write("")

