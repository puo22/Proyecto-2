# ---------------------------------------------
# Analizador Sintáctico LL(1) - Proyecto Corte 2 (revisado)
# - INDENT/DEDENT obligatorios para suites
# - Tras ':' salta NEWLINE(s) antes de exigir INDENT
# - Errores de indentación: "<fila,columna>Error sintactico: falla de indentacion"
# - Soporta elif, while, for-in, asignaciones, llamadas, listas, unarios, postfijos
# - Lee tokens de 'salida_tokens.txt' de manera robusta (lexemas con comas)
# - Guarda salida en "salida parser.txt"
# ---------------------------------------------

class ParseError(Exception):
    pass


# ---------------------------- CARGA DE TOKENS ----------------------------

def cargar_tokens(nombre_archivo):
    """
    Lee líneas tipo:
      <TIPO,LEXEMA,LINEA,COL>
      <TIPO,LINEA,COL>  (sin lexema)
    Soporta lexemas que contengan comas.
    """
    tokens = []
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or not (line.startswith("<") and line.endswith(">")):
                continue

            contenido = line[1:-1]  # sin < >
            # Encontrar las dos últimas comas (antes de línea y col)
            i_last = contenido.rfind(",")
            if i_last == -1:
                continue
            i_prev = contenido.rfind(",", 0, i_last)
            if i_prev == -1:
                continue

            linea_str = contenido[i_prev + 1:i_last].strip()
            col_str = contenido[i_last + 1:].strip()
            head = contenido[:i_prev].strip()

            # head puede ser "TIPO" o "TIPO,LEXEMA"
            if "," in head:
                i_first = head.find(",")
                tipo = head[:i_first].strip()
                lexema = head[i_first + 1:].strip()
            else:
                tipo = head
                lexema = ""

            try:
                linea = int(linea_str)
                columna = int(col_str)
            except ValueError:
                # Si por algún motivo no son números, descartar línea
                continue

            tokens.append({"type": tipo, "lexeme": lexema, "line": linea, "col": columna})

    # Asegurar EOF
    if not tokens or tokens[-1]["type"] != "EOF":
        last_line = tokens[-1]["line"] if tokens else 1
        last_col = (tokens[-1]["col"] + 1) if tokens else 1
        tokens.append({"type": "EOF", "lexeme": "", "line": last_line, "col": last_col})
    return tokens


# -------------------------------- PARSER --------------------------------

class Parser:
    # Operadores binarios que este parser reconoce (asociación izquierda, sin precedencia fina)
    OP_TYPES = {
        "tk_suma", "tk_resta", "tk_mult", "tk_div", "tk_mod",
        "tk_igualdad", "tk_distinto", "tk_mayor", "tk_menor", "tk_mayor_igual", "tk_menor_igual",
        # Extras según tu lexer mejorado:
        "tk_potencia",          # **
        "tk_div_entera",        # //
        "tk_shift_izq", "tk_shift_der",  # << >>
        "tk_and_bit", "tk_or_bit", "tk_xor_bit",  # & | ^
        "tk_matmul",            # @
    }

    # Operadores de asignación aumentada (target simple soportado)
    AUG_ASSIGN = {
        "tk_mas_igual", "tk_menos_igual", "tk_mul_igual", "tk_div_igual", "tk_mod_igual",
        "tk_divent_igual", "tk_pot_igual", "tk_andb_igual", "tk_orb_igual", "tk_xorb_igual",
        "tk_shl_igual", "tk_shr_igual"
    }

    TYPE_STARTERS = {"id", "int", "str", "float", "bool", "tk_cor_izq"}

    # Tokens que pueden iniciar una expresión (además de 'id')
    EXPR_STARTERS = {
        "tk_entero", "tk_float", "tk_cadena",
        "True", "False", "None",
        "tk_par_izq", "tk_cor_izq"
    }

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
        tok = self.actual()
        self.pos += 1
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
        elif t == "while":
            self.parse_while_stmt()
        elif t == "return":
            self.parse_return_stmt()
        elif t == "yield":
            self.parse_yield_stmt()
        elif t == "print":
            self.parse_print_stmt()
        elif t == "pass":
            self.avanzar()
            if self.actual()["type"] == "NEWLINE":
                self.coincidir("NEWLINE")
        elif t == "break":
            self.avanzar()
            if self.actual()["type"] == "NEWLINE":
                self.coincidir("NEWLINE")
        elif t == "continue":
            self.avanzar()
            if self.actual()["type"] == "NEWLINE":
                self.coincidir("NEWLINE")

        elif t == "id":
            # Puede ser asignación o expresión que empieza con id
            self.parse_assign_or_expr_stmt()

        elif t in self.EXPR_STARTERS:
            # Expresión-sentencia que NO empieza con id
            self.parse_expresion()
            if self.actual()["type"] == "NEWLINE":
                self.coincidir("NEWLINE")

        elif t == "NEWLINE":
            self.coincidir("NEWLINE")
        else:
            esperados = ["import", "class", "def", "if", "for", "while", "print",
                         "id", "return", "yield", "pass", "break", "continue", "NEWLINE"] + list(self.EXPR_STARTERS)
            self.error(self.actual(), esperados)

    # ---------------------------------------------
    # import / from ... import ...
    # ---------------------------------------------
    def parse_import(self):
        if self.actual()["type"] == "import":
            self.coincidir("import")
            self.coincidir("id")
            while self.actual()["type"] == "tk_coma":
                self.coincidir("tk_coma")
                self.coincidir("id")
        else:
            self.coincidir("from")
            self.coincidir("id")
            self.coincidir("import")
            self.coincidir("id")
            while self.actual()["type"] == "tk_coma":
                self.coincidir("tk_coma")
                self.coincidir("id")
        if self.actual()["type"] == "NEWLINE":
            self.coincidir("NEWLINE")

    # ---------------------------------------------
    # class Nombre([Padre]):
    # ---------------------------------------------
    def parse_class_decl(self):
        self.coincidir("class")
        self.coincidir("id")
        if self.actual()["type"] == "tk_par_izq":
            self.coincidir("tk_par_izq")
            self.coincidir("id")
            self.coincidir("tk_par_der")
        self.coincidir("tk_dos_puntos")
        self.parse_suite()

    # ---------------------------------------------
    # def nombre(params):
    # ---------------------------------------------
    def parse_func_decl(self):
        self.coincidir("def")
        self.coincidir("id")
        self.coincidir("tk_par_izq")
        if self.actual()["type"] not in ("tk_par_der", "EOF"):
            self.parse_param()
            while self.actual()["type"] == "tk_coma":
                self.coincidir("tk_coma")
                if self.actual()["type"] in ("tk_par_der", "EOF"):
                    break
                self.parse_param()
        self.coincidir("tk_par_der")
        self.coincidir("tk_dos_puntos")
        self.parse_suite()

    def parse_param(self):
        self.coincidir("id")
        if self.actual()["type"] == "tk_dos_puntos":
            colon_tok = self.actual()
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
            coma_tok = self.actual()
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
            self.coincidir("tk_par_izq")
            self.parse_expresion()
            self.coincidir("tk_par_der")
        else:
            self.parse_expresion()
        self.coincidir("tk_dos_puntos")
        self.parse_suite()

        while self.actual()["type"] == "elif":
            self.coincidir("elif")
            if self.actual()["type"] == "tk_par_izq":
                self.coincidir("tk_par_izq")
                self.parse_expresion()
                self.coincidir("tk_par_der")
            else:
                self.parse_expresion()
            self.coincidir("tk_dos_puntos")
            self.parse_suite()

        if self.actual()["type"] == "else":
            self.coincidir("else")
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
                self.coincidir("tk_coma")
                self.coincidir("id")
            self.coincidir("tk_par_der")
        else:
            self.coincidir("id")
            while self.actual()["type"] == "tk_coma":
                self.coincidir("tk_coma")
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
    # return / yield
    # ---------------------------------------------
    def parse_return_stmt(self):
        self.coincidir("return")
        if self.actual()["type"] not in ("NEWLINE", "DEDENT", "EOF"):
            self.parse_expresion()
        if self.actual()["type"] == "NEWLINE":
            self.coincidir("NEWLINE")

    def parse_yield_stmt(self):
        self.coincidir("yield")
        if self.actual()["type"] not in ("NEWLINE", "DEDENT", "EOF"):
            self.parse_expresion()
        if self.actual()["type"] == "NEWLINE":
            self.coincidir("NEWLINE")

    # ---------------------------------------------
    # print(...)
    # ---------------------------------------------
    def parse_print_stmt(self):
        self.coincidir("print")
        # Reutilizamos la misma lógica que en llamadas normales: (args)
        self.coincidir("tk_par_izq")
        if self.actual()["type"] != "tk_par_der":
            self.parse_expresion()
            while self.actual()["type"] == "tk_coma":
                self.coincidir("tk_coma")
                # Permitir coma final opcional: print(a, b,)
                if self.actual()["type"] == "tk_par_der":
                    break
                self.parse_expresion()
        self.coincidir("tk_par_der")
        if self.actual()["type"] == "NEWLINE":
            self.coincidir("NEWLINE")

    # ---------------------------------------------
    # Asignación o Expresión (que empieza con 'id')
    # ---------------------------------------------
    def parse_assign_or_expr_stmt(self):
        # Intentar leer un LHS asignable (id, id.attr, id[...]) y opcionalmente una lista de targets
        first_plain = self._parse_assign_target()

        # ¿Anotación de tipo? (solo para id simple)
        if first_plain and self.actual()["type"] == "tk_dos_puntos":
            self.coincidir("tk_dos_puntos")
            self.parse_type()
            if self.actual()["type"] == "tk_asig":
                self.coincidir("tk_asig")
                self.parse_expr_list()
            if self.actual()["type"] == "NEWLINE":
                self.coincidir("NEWLINE")
            return

        # ¿Lista de targets: t1, t2, ... = ... ?
        multiple_targets = False
        while self.actual()["type"] == "tk_coma":
            multiple_targets = True
            self.coincidir("tk_coma")
            self._parse_assign_target()

        # Asignación '=' o aumentada
        if self.actual()["type"] == "tk_asig":
            self.coincidir("tk_asig")
            self.parse_expr_list()
        elif self.actual()["type"] in self.AUG_ASSIGN:
            # t op= expr
            self.avanzar()
            self.parse_expresion()
        else:
            # No era asignación: interpretarlo como EXPRESIÓN que arrancó con un primario.
            # Permite ahora llamadas, más attrs/index y operadores binarios.
            self._parse_postfijos()
            while self.actual()["type"] in self.OP_TYPES or self.actual()["type"] in ("and", "or"):
                self.avanzar()
                self.parse_termino()

        if self.actual()["type"] == "NEWLINE":
            self.coincidir("NEWLINE")


    def parse_expr_list(self):
        self.parse_expresion()
        while self.actual()["type"] == "tk_coma":
            self.coincidir("tk_coma")
            self.parse_expresion()

    # ---------------------------------------------
    # Expresiones (asociación izquierda; precedencia no diferenciada)
    # ---------------------------------------------
    def parse_expresion(self):
        self.parse_termino()
        while self.actual()["type"] in self.OP_TYPES or self.actual()["type"] in ("and", "or"):
            self.avanzar()
            self.parse_termino()

    def parse_termino(self):
        t = self.actual()["type"]

        # Unarios: +x, -x, ~x, not x
        if t in ("tk_suma", "tk_resta", "tk_not_bit") or t == "not":
            self.avanzar()
            self.parse_termino()
            # Permitir postfijos tras unario (p. ej., -(a).f()[i])
            self._parse_postfijos()
            return

        if t == "id":
            self.coincidir("id")
            self._parse_postfijos()
        elif t in ("tk_entero", "tk_float", "tk_cadena"):
            self.avanzar()
            self._parse_postfijos()
        elif t in ("True", "False", "None"):
            self.avanzar()
            self._parse_postfijos()
        elif t == "tk_par_izq":
            # (exp)
            self.coincidir("tk_par_izq")
            # Permitimos tuplas simples: (a, b, c) como una lista de expresiones
            self.parse_expresion()
            while self.actual()["type"] == "tk_coma":
                self.coincidir("tk_coma")
                # Tupla con coma final opcional NO soportada; si quieres, lo ampliamos
                self.parse_expresion()
            self.coincidir("tk_par_der")
            self._parse_postfijos()
        elif t == "tk_cor_izq":
            # Lista literal: [a, b, c]
            self.coincidir("tk_cor_izq")
            if self.actual()["type"] != "tk_cor_der":
                self.parse_expresion()
                while self.actual()["type"] == "tk_coma":
                    self.coincidir("tk_coma")
                    if self.actual()["type"] == "tk_cor_der":
                        break
                    self.parse_expresion()
            self.coincidir("tk_cor_der")
            self._parse_postfijos()
        else:
            self.error(self.actual(),
                       ["id", "tk_entero", "tk_float", "tk_cadena", "True", "False", "None",
                        "tk_par_izq", "tk_cor_izq", "tk_suma", "tk_resta", "tk_not_bit", "not"])

    # ------------------------- Postfijos -------------------------
    def _parse_postfijos(self):
        """
        Consume repetidamente postfijos tras un primario:
          - Llamadas:  (args)
          - Indexación: [expr (',' expr)*]
          - Atributos: .id
        """
        while True:
            t = self.actual()["type"]
            if t == "tk_par_izq":
                self._parse_call_args()
            elif t == "tk_cor_izq":
                self._parse_index_args()
            elif t == "tk_punto":
                self.coincidir("tk_punto")
                self.coincidir("id")
            else:
                break
    def _parse_assign_target(self):
        """
        Target asignable para LHS: id, id.attr, id[...], encadenado.
        Devuelve True si el target fue un id 'simple' (sin postfijos), útil para 'id: Tipo'.
        """
        self.coincidir("id")
        plain = True
        while True:
            t = self.actual()["type"]
            if t == "tk_punto":
                plain = False
                self.coincidir("tk_punto")
                self.coincidir("id")
            elif t == "tk_cor_izq":
                plain = False
                self._parse_index_args()  # ya definida: [expr (, expr)*]
            else:
                break
        return plain

    def _parse_call_args(self):
        self.coincidir("tk_par_izq")
        if self.actual()["type"] != "tk_par_der":
            self.parse_expresion()
            while self.actual()["type"] == "tk_coma":
                self.coincidir("tk_coma")
                if self.actual()["type"] == "tk_par_der":
                    break
                self.parse_expresion()
            if self.actual()["type"] != "tk_par_der":
                self.error(self.actual(), ["tk_coma", "tk_par_der"])
        self.coincidir("tk_par_der")

    def _parse_index_args(self):
        self.coincidir("tk_cor_izq")
        # Soporte básico: una o varias expresiones separadas por coma (no slices 'a:b')
        self.parse_expresion()
        while self.actual()["type"] == "tk_coma":
            self.coincidir("tk_coma")
            self.parse_expresion()
        self.coincidir("tk_cor_der")


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
