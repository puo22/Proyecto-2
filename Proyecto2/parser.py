# ---------------------------------------------
# Analizador Sintáctico LL(1) - Proyecto Corte 2
# Sin librerías externas
# ---------------------------------------------
# Por: Pau Lenguajes

class ParseError(Exception):
    pass


# ---------------------------------------------
# Cargar tokens del archivo del lexer
# ---------------------------------------------
def cargar_tokens(nombre_archivo):
    tokens = []
    with open(nombre_archivo, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Formato: <tipo,lexema,linea,columna>
            datos = line[1:-1].split(",")
            tipo = datos[0].strip()
            lexema = datos[1].strip() if len(datos) > 3 else ""
            linea = int(datos[-2])
            columna = int(datos[-1])
            tokens.append({
                "type": tipo,
                "lexeme": lexema,
                "line": linea,
                "col": columna
            })
    return tokens


# ---------------------------------------------
# Clase principal del Parser LL(1)
# ---------------------------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def actual(self):
        return self.tokens[self.pos]

    def avanzar(self):
        tok = self.actual()
        self.pos += 1
        return tok

    def coincidir(self, *esperados):
        tok = self.actual()
        if tok["type"] in esperados or tok["lexeme"] in esperados:
            self.avanzar()
        else:
            self.error(tok, esperados)

    def error(self, tok, esperados):
        linea = tok["line"]
        columna = tok["col"]
        encontrado = tok["lexeme"] if tok["lexeme"] else tok["type"]
        esperado = ", ".join(esperados)
        print(f"<{linea},{columna}> Error sintáctico: se encontró '{encontrado}', se esperaba: {esperado}")
        raise ParseError()

    # ---------------------------------------------
    # Reglas gramaticales (LL(1))
    # ---------------------------------------------

    def parse_programa(self):
        """programa -> (sentencia)* EOF"""
        try:
            while self.actual()["type"] != "EOF":
                self.parse_sentencia()
            print("✅ Análisis sintáctico finalizado correctamente.")
        except ParseError:
            pass

    def parse_sentencia(self):
        """sentencia -> import_decl | class_decl | func_decl | if_stmt | print_stmt | assign_stmt"""
        t = self.actual()["type"]
        l = self.actual()["lexeme"]

        if t == "import" or t == "from":
            self.parse_import()
        elif t == "class":
            self.parse_class_decl()
        elif t == "def":
            self.parse_func_decl()
        elif t == "if":
            self.parse_if_stmt()
        elif t == "print":
            self.parse_print_stmt()
        elif t == "id":
            self.parse_assign_stmt()
        elif t == "NEWLINE":
            self.coincidir("NEWLINE")
        else:
            self.error(self.actual(), ["import", "class", "def", "if", "print", "id"])

    # ---------------------------------------------------
    # import ... / from ... import ...
    # ---------------------------------------------------
    def parse_import(self):
        if self.actual()["type"] == "import":
            self.coincidir("import")
            self.coincidir("id")
            while self.actual()["lexeme"] == ",":
                self.coincidir(",")
                self.coincidir("id")
        else:
            self.coincidir("from")
            self.coincidir("id")
            self.coincidir("import")
            self.coincidir("id")
            while self.actual()["lexeme"] == ",":
                self.coincidir(",")
                self.coincidir("id")
        if self.actual()["type"] == "NEWLINE":
            self.coincidir("NEWLINE")

    # ---------------------------------------------------
    # class Nombre([Padre]):
    # ---------------------------------------------------
    def parse_class_decl(self):
        self.coincidir("class")
        self.coincidir("id")
        if self.actual()["lexeme"] == "(":
            self.coincidir("(")
            self.coincidir("id")
            self.coincidir(")")
        self.coincidir("tk_dos_puntos")
        if self.actual()["type"] == "NEWLINE":
            self.coincidir("NEWLINE")
        # Bloque interno de clase
        while self.actual()["type"] not in ("EOF", "class", "def", "id", "if", "print", "return"):
            self.coincidir("NEWLINE")

    # ---------------------------------------------------
    # def nombre(parametros):
    # ---------------------------------------------------
    def parse_func_decl(self):
        self.coincidir("def")
        self.coincidir("id")
        self.coincidir("tk_par_izq")
        if self.actual()["type"] == "id":
            self.coincidir("id")
            while self.actual()["lexeme"] == ",":
                self.coincidir(",")
                self.coincidir("id")
        self.coincidir("tk_par_der")
        self.coincidir("tk_dos_puntos")
        if self.actual()["type"] == "NEWLINE":
            self.coincidir("NEWLINE")

    # ---------------------------------------------------
    # if (expr): ...
    # ---------------------------------------------------
    def parse_if_stmt(self):
        self.coincidir("if")
        if self.actual()["lexeme"] == "(":
            self.coincidir("(")
            self.parse_expresion()
            self.coincidir(")")
        self.coincidir("tk_dos_puntos")
        if self.actual()["type"] == "NEWLINE":
            self.coincidir("NEWLINE")

    # ---------------------------------------------------
    # print("...")
    # ---------------------------------------------------
    def parse_print_stmt(self):
        self.coincidir("print")
        self.coincidir("tk_par_izq")
        self.parse_expresion()
        self.coincidir("tk_par_der")
        if self.actual()["type"] == "NEWLINE":
            self.coincidir("NEWLINE")

    # ---------------------------------------------------
    # id [: tipo] = expr
    # ---------------------------------------------------
    def parse_assign_stmt(self):
        self.coincidir("id")
        if self.actual()["lexeme"] == ":":
            self.coincidir(":")
            self.coincidir("id")
        self.coincidir("tk_asig")
        self.parse_expresion()
        if self.actual()["type"] == "NEWLINE":
            self.coincidir("NEWLINE")

    # ---------------------------------------------------
    # Expresiones simples
    # ---------------------------------------------------
    def parse_expresion(self):
        """expr -> termino (op termino)*"""
        self.parse_termino()
        while self.actual()["lexeme"] in ("+", "-", "*", "/", "==", "!=", ">", "<"):
            self.coincidir(self.actual()["lexeme"])
            self.parse_termino()

    def parse_termino(self):
        t = self.actual()["type"]
        if t == "id":
            self.coincidir("id")
        elif t == "tk_entero" or t == "tk_cadena":
            self.avanzar()
        elif self.actual()["lexeme"] == "(":
            self.coincidir("(")
            self.parse_expresion()
            self.coincidir(")")
        else:
            self.error(self.actual(), ["id", "tk_entero", "tk_cadena", "("])


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
if __name__ == "__main__":
    tokens = cargar_tokens("salida_tokens.txt")
    parser = Parser(tokens)
    parser.parse_programa()

