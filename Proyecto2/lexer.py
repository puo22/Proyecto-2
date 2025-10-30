# ---------------------------------------------
# Analizador Léxico - Proyecto Corte 2 (mejorado)
# - Soporta:
#   * INDENT/DEDENT con tabs a múltiplos de TAB_SIZE
#   * Comentarios con #
#   * Cadenas simples, triples y con prefijos (r, f, b, combinaciones rf/fr)
#   * Números: enteros/float (con _), exponenciales, hex/oct/bin (con _)
#   * Operadores simples, dobles y compuestos (+=, -=, **=, etc.)
# ---------------------------------------------

TAB_SIZE = 4  # tabula a múltiplos de 4 columnas

RESERVED = {
    "False", "None", "True", "and", "as", "assert", "break", "class", "continue", "def",
    "del", "elif", "else", "except", "finally", "for", "from", "global", "if", "import",
    "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
    "while", "with", "yield",
    "print", "object", "str", "bool", "int", "float", "list", "dict", "set", "tuple"
}

MULTI_OPS = {
    "!=": "tk_distinto",
    "==": "tk_igualdad",
    "<=": "tk_menor_igual",
    ">=": "tk_mayor_igual",
    "->": "tk_ejecuta",
    "**": "tk_potencia",
    "//": "tk_div_entera",
    ":=": "tk_walrus",
    "<<": "tk_shift_izq",
    ">>": "tk_shift_der",
    # Asignación compuesta (adicional)
    "+=": "tk_mas_igual",
    "-=": "tk_menos_igual",
    "*=": "tk_mul_igual",
    "/=": "tk_div_igual",
    "%=": "tk_mod_igual",
    "&=": "tk_andb_igual",
    "|=": "tk_orb_igual",
    "^=": "tk_xorb_igual",
    "<<=": "tk_shl_igual",
    ">>=": "tk_shr_igual",
    "//=": "tk_divent_igual",
    "**=": "tk_pot_igual",
}

SINGLE_OPS = {
    "(": "tk_par_izq",
    ")": "tk_par_der",
    "[": "tk_cor_izq",
    "]": "tk_cor_der",
    "{": "tk_llave_izq",
    "}": "tk_llave_der",
    ",": "tk_coma",
    ":": "tk_dos_puntos",
    ".": "tk_punto",
    ";": "tk_pyc",
    "=": "tk_asig",
    "+": "tk_suma",
    "-": "tk_resta",
    "*": "tk_mult",
    "/": "tk_div",
    "%": "tk_mod",
    "<": "tk_menor",
    ">": "tk_mayor",
    "@": "tk_matmul",
    "&": "tk_and_bit",
    "|": "tk_or_bit",
    "^": "tk_xor_bit",
    "~": "tk_not_bit",
}


def error(linea, columna):
    print(f">>> Error léxico(linea:{linea},posicion:{columna})")
    raise SystemExit(1)


def es_id_start(ch):
    return ch == "_" or ch.isalpha()


def es_id_part(ch):
    return ch == "_" or ch.isalnum()


# ---------- Utilidades para cadenas y números mejorados ----------

def escapar_contenido(s: str) -> str:
    """Escapa barras y comillas dobles para imprimir el contenido dentro del token."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def es_prefijo_cadena(texto, i):
    """
    Detecta prefijos de cadena válidos (r, R, f, F, b, B) en uno o dos chars (rf, fr).
    Si encuentra, retorna (j, quote_char, is_triple), donde j es el índice de la comilla.
    Si no aplica, retorna None.
    """
    n = len(texto)
    j = i
    pref = ""
    while j < n and texto[j] in "rRfFbB":
        pref += texto[j]
        j += 1
        if len(pref) == 2:
            break
    if j < n and texto[j] in ("'", '"'):
        q = texto[j]
        is_triple = (j + 2 < n and texto[j + 1] == q and texto[j + 2] == q)
        return j, q, is_triple
    return None


def leer_cadena(texto, i, col, linea):
    """Lector original de cadena (sin prefijos), conservado como fallback."""
    n = len(texto)
    quote = texto[i]
    start_line, start_col = linea, col

    is_triple = i + 2 < n and texto[i + 1] == quote and texto[i + 2] == quote
    if is_triple:
        i += 3; col += 3
        lex = []
        while i < n:
            ch = texto[i]
            if ch == quote and i + 2 < n and texto[i + 1] == quote and texto[i + 2] == quote:
                i += 3; col += 3
                contenido = escapar_contenido("".join(lex))
                return f'<tk_cadena,"{contenido}",{start_line},{start_col}>', i, col, linea
            if ch == "\n":
                i += 1; linea += 1; col = 1
                lex.append("\n"); continue
            if ch == "\\" and i + 1 < n:
                lex.append(ch); i += 1; col += 1
                lex.append(texto[i]); i += 1; col += 1; continue
            lex.append(ch); i += 1; col += 1
        error(start_line, start_col)
    else:
        i += 1; col += 1
        lex = []
        while i < n and texto[i] != quote:
            ch = texto[i]
            if ch == "\n":
                error(start_line, start_col)
            if ch == "\\" and i + 1 < n:
                lex.append(ch); i += 1; col += 1
                lex.append(texto[i]); i += 1; col += 1; continue
            lex.append(ch); i += 1; col += 1
        if i >= n:
            error(start_line, start_col)
        i += 1; col += 1
        contenido = escapar_contenido("".join(lex))
        return f'<tk_cadena,"{contenido}",{start_line},{start_col}>', i, col, linea


def leer_cadena_con_prefijo(texto, i, col, linea):
    """
    Igual a leer_cadena, pero acepta prefijos (r/R, f/F, b/B, combinaciones),
    sin interpretar f-strings ni escapes especiales: solo tokeniza.
    """
    n = len(texto)
    start_line, start_col = linea, col

    pref_info = es_prefijo_cadena(texto, i)
    if pref_info is None:
        return leer_cadena(texto, i, col, linea)

    j, quote, is_triple = pref_info

    # Avanza columna e índice por el prefijo hasta la comilla
    while i < j:
        i += 1
        col += 1

    # Ahora i está en la comilla inicial
    if is_triple:
        i += 3; col += 3
        lex = []
        while i < n:
            ch = texto[i]
            if ch == quote and i + 2 < n and texto[i + 1] == quote and texto[i + 2] == quote:
                i += 3; col += 3
                contenido = escapar_contenido("".join(lex))
                return f'<tk_cadena,"{contenido}",{start_line},{start_col}>', i, col, linea
            if ch == "\n":
                i += 1; linea += 1; col = 1
                lex.append("\n"); continue
            if ch == "\\" and i + 1 < n:
                lex.append(ch); i += 1; col += 1
                lex.append(texto[i]); i += 1; col += 1; continue
            lex.append(ch); i += 1; col += 1
        error(start_line, start_col)
    else:
        i += 1; col += 1
        lex = []
        while i < n and texto[i] != quote:
            ch = texto[i]
            if ch == "\n":
                error(start_line, start_col)
            if ch == "\\" and i + 1 < n:
                lex.append(ch); i += 1; col += 1
                lex.append(texto[i]); i += 1; col += 1; continue
            lex.append(ch); i += 1; col += 1
        if i >= n:
            error(start_line, start_col)
        i += 1; col += 1
        contenido = escapar_contenido("".join(lex))
        return f'<tk_cadena,"{contenido}",{start_line},{start_col}>', i, col, linea


def leer_numero(texto, i, col, linea):
    """
    Reconoce:
      - Enteros con guiones bajos: 1_000
      - Flotantes: 3.14, .5, 1., 1e-3, 2_0.5_0e+1 (se eliminan '_')
      - Hex/Oct/Bin: 0xFF, 0o77, 0b1010 (con '_')
    Devuelve (token, i, col, linea) o None si no hay número en i.
    """
    n = len(texto)
    start_line, start_col = linea, col
    j = i

    def consume_digits_underscore(k, base_digits):
        while k < n and (texto[k] in base_digits or texto[k] == "_"):
            k += 1
        return k

    # Hex/Oct/Bin
    if j + 1 < n and texto[j] == "0" and texto[j + 1] in "xXoObB":
        base = texto[j + 1].lower()
        j += 2
        if base == "x":
            j = consume_digits_underscore(j, "0123456789abcdefABCDEF")
        elif base == "o":
            j = consume_digits_underscore(j, "01234567")
        else:  # b
            j = consume_digits_underscore(j, "01")
        lex = texto[i:j].replace("_", "")
        return (f"<tk_entero,{lex},{start_line},{start_col}>", j, col + (j - i), linea)

    # Parte entera (permite guiones bajos)
    has_int = False
    while j < n and (texto[j].isdigit() or texto[j] == "_"):
        has_int = texto[j].isdigit() or has_int
        j += 1

    k_before_dot = j
    is_float = False

    # Punto decimal:
    # - Si ya hay parte entera, '1.' es válido como float
    # - Si no hay parte entera, se exige al menos un dígito después: '.5'
    if j < n and texto[j] == ".":
        if (has_int) or (j + 1 < n and texto[j + 1].isdigit()):
            is_float = True
            j += 1
            while j < n and (texto[j].isdigit() or texto[j] == "_"):
                j += 1
        else:
            # '.' suelto: no es número (se dejará para tk_punto)
            j = k_before_dot

    # Exponente (si procede)
    if j < n and texto[j] in "eE":
        # Solo consideramos exponente si hay base numérica previa
        if j != i:
            is_float = True
            j += 1
            if j < n and texto[j] in "+-":
                j += 1
            exp_start = j
            while j < n and (texto[j].isdigit() or texto[j] == "_"):
                j += 1
            if j == exp_start:
                # 'e' sin dígitos: retrocede y no cuentes exponente
                j = k_before_dot if is_float else i

    lex = texto[i:j].replace("_", "")

    if j == i:
        return None  # no había número

    if is_float:
        return (f"<tk_float,{lex},{start_line},{start_col}>", j, col + (j - i), linea)
    else:
        return (f"<tk_entero,{lex},{start_line},{start_col}>", j, col + (j - i), linea)


# ---------------------- Tokenizador principal ----------------------

def tokenize(texto):
    tokens = []
    i = 0
    n = len(texto)
    linea = 1
    col = 1

    indent_stack = [0]
    at_line_start = True

    def emitir_indent_dedent(actual_indent, line_no):
        top = indent_stack[-1]
        if actual_indent > top:
            indent_stack.append(actual_indent)
            tokens.append(f"<INDENT, ,{line_no},1>")
        elif actual_indent < top:
            while indent_stack and indent_stack[-1] > actual_indent:
                indent_stack.pop()
                tokens.append(f"<DEDENT, ,{line_no},1>")

    while i < n:
        ch = texto[i]

        # -----------------------------------------------------------------
        # Inicio de línea: medir indentación
        # -----------------------------------------------------------------
        if at_line_start:
            actual_indent = 0
            while i < n and texto[i] in (" ", "\t"):
                if texto[i] == " ":
                    i += 1; col += 1; actual_indent += 1
                else:
                    i += 1
                    adv = TAB_SIZE - ((col - 1) % TAB_SIZE)
                    col += adv; actual_indent += adv

            at_line_start = False  # Ya no estamos al inicio de la línea

            if i < n and texto[i] not in ("\n", "#"):
                # Línea con código real -> emitir INDENT/DEDENT
                emitir_indent_dedent(actual_indent, linea)
            # si es línea en blanco o comentario, no emitir

            # Volver al bucle para recargar ch en nueva posición
            continue
        # -----------------------------------------------------------------

        # Espacios sueltos
        if ch == " " or ch == "\r":
            i += 1; col += 1
            continue

        # Tab fuera del inicio (ajusta columnas igualmente)
        if ch == "\t":
            i += 1
            adv = TAB_SIZE - ((col - 1) % TAB_SIZE)
            col += adv
            continue

        # Salto de línea
        if ch == "\n":
            tokens.append(f"<NEWLINE,\\n,{linea},{col}>")
            i += 1; linea += 1; col = 1
            at_line_start = True
            continue

        # Comentario
        if ch == "#":
            while i < n and texto[i] != "\n":
                i += 1; col += 1
            continue  # se omite

        # Cadenas (con o sin prefijo)
        pref = es_prefijo_cadena(texto, i)
        if ch in ('"', "'") or pref is not None:
            tok, i, col, linea = leer_cadena_con_prefijo(texto, i, col, linea)
            tokens.append(tok)
            continue

        # Identificadores y palabras reservadas
        if es_id_start(ch):
            start_line, start_col = linea, col
            j = i
            while j < n and es_id_part(texto[j]):
                j += 1
            lexema = texto[i:j]
            if lexema in RESERVED:
                tokens.append(f"<{lexema},{start_line},{start_col}>")
            else:
                tokens.append(f"<id,{lexema},{start_line},{start_col}>")
            col += (j - i); i = j
            continue

        # Números (enteros/float/hex/oct/bin con '_')
        num_res = leer_numero(texto, i, col, linea)
        if num_res is not None:
            tok, i, col, linea = num_res
            tokens.append(tok)
            continue

        # Operadores de 3 y 2 caracteres (priorizar el más largo)
        if i + 2 < n:
            tri = texto[i:i + 3]
            if tri in MULTI_OPS:
                start_line, start_col = linea, col
                tokens.append(f"<{MULTI_OPS[tri]},{start_line},{start_col}>")
                i += 3; col += 3
                continue

        if i + 1 < n:
            duo = texto[i:i + 2]
            if duo in MULTI_OPS:
                start_line, start_col = linea, col
                tokens.append(f"<{MULTI_OPS[duo]},{start_line},{start_col}>")
                i += 2; col += 2
                continue

        # Operadores de 1 carácter
        if ch in SINGLE_OPS:
            start_line, start_col = linea, col
            tokens.append(f"<{SINGLE_OPS[ch]},{start_line},{start_col}>")
            i += 1; col += 1
            continue

        # Si nada coincide, error
        error(linea, col)

    # Al finalizar, vaciar indentaciones pendientes
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(f"<DEDENT, ,{linea},{col}>")

    tokens.append(f"<EOF, ,{linea},{col}>")
    return tokens


def main():
    infile = input("Ingrese el nombre del archivo de entrada (.py): ").strip()
    with open(infile, "r", encoding="utf-8") as f:
        src = f.read()
    tokens = tokenize(src)
    #print("\n".join(tokens))
    with open("salida_tokens.txt", "w", encoding="utf-8") as out:
        for t in tokens:
            out.write(t + "\n")
    print("\n Tokens generados correctamente en 'salida_tokens.txt'")


if __name__ == "__main__":
    main()
