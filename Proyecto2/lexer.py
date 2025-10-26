# ---------------------------------------------
# Analizador Léxico - Proyecto Corte 2 (con salto de comentarios)
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


def es_id_start(ch): return ch == "_" or ch.isalpha()


def es_id_part(ch):  return ch == "_" or ch.isalnum()


def leer_cadena(texto, i, col, linea):
    n = len(texto)
    quote = texto[i]
    start_line, start_col = linea, col

    is_triple = i + 2 < n and texto[i + 1] == quote and texto[i + 2] == quote
    if is_triple:
        i += 3;
        col += 3
        lex = []
        while i < n:
            ch = texto[i]
            if ch == quote and i + 2 < n and texto[i + 1] == quote and texto[i + 2] == quote:
                i += 3;
                col += 3
                contenido = "".join(lex)
                return f'<tk_cadena,"{contenido}",{start_line},{start_col}>', i, col, linea
            if ch == "\n":
                i += 1;
                linea += 1;
                col = 1
                lex.append("\n");
                continue
            if ch == "\\" and i + 1 < n:
                lex.append(ch);
                i += 1;
                col += 1
                lex.append(texto[i]);
                i += 1;
                col += 1
                continue
            lex.append(ch);
            i += 1;
            col += 1
        error(start_line, start_col)
    else:
        i += 1;
        col += 1
        lex = []
        while i < n and texto[i] != quote:
            ch = texto[i]
            if ch == "\n": error(start_line, start_col)
            if ch == "\\" and i + 1 < n:
                lex.append(ch);
                i += 1;
                col += 1
                lex.append(texto[i]);
                i += 1;
                col += 1
                continue
            lex.append(ch);
            i += 1;
            col += 1
        if i >= n: error(start_line, start_col)
        i += 1;
        col += 1
        contenido = "".join(lex)
        return f'<tk_cadena,"{contenido}",{start_line},{start_col}>', i, col, linea


def tokenize(texto):
    tokens = []
    i = 0;
    n = len(texto)
    linea = 1;
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
        # BLOQUE CORREGIDO
        # -----------------------------------------------------------------
        # Inicio de línea: medir indentación
        if at_line_start:
            actual_indent = 0
            while i < n and texto[i] in (" ", "\t"):
                if texto[i] == " ":
                    i += 1;
                    col += 1;
                    actual_indent += 1
                else:
                    i += 1
                    adv = TAB_SIZE - ((col - 1) % TAB_SIZE)
                    col += adv;
                    actual_indent += adv

            at_line_start = False  # Ya no estamos al inicio de la línea

            if i < n and texto[i] not in ("\n", "#"):
                # Es una línea con código, emitir INDENT/DEDENT si es necesario
                emitir_indent_dedent(actual_indent, linea)
                # else:
                # Es una línea en blanco (apunta a \n) o
                # es una línea de comentario (apunta a #).
                # No se emite INDENT/DEDENT.
                pass

            # Forzar al bucle a recargar 'ch' con el carácter en la nueva
            # posición 'i' (sea código, '#' o '\n')
            continue
        # -----------------------------------------------------------------
        # FIN DEL BLOQUE CORREGIDO
        # -----------------------------------------------------------------

        if ch == " " or ch == "\r":
            i += 1;
            col += 1;
            continue
        if ch == "\t":
            # Esto no debería ocurrir fuera del inicio de línea, pero por si acaso
            i += 1
            adv = TAB_SIZE - ((col - 1) % TAB_SIZE)
            col += adv;
            continue

        if ch == "\n":
            tokens.append(f"<NEWLINE,\\n,{linea},{col}>")
            i += 1;
            linea += 1;
            col = 1
            at_line_start = True
            continue

        if ch == "#":
            # Se salta todo lo que sigue en la línea para el comentario
            while i < n and texto[i] != "\n":
                i += 1;
                col += 1
            continue  # se salta el comentario sin hacer nada

        if ch == '"' or ch == "'":
            tok, i, col, linea = leer_cadena(texto, i, col, linea)
            tokens.append(tok);
            continue

        if es_id_start(ch):
            start_line, start_col = linea, col
            j = i
            while j < n and es_id_part(texto[j]): j += 1
            lexema = texto[i:j]
            if lexema in RESERVED:
                tokens.append(f"<{lexema},{start_line},{start_col}>")
            else:
                tokens.append(f"<id,{lexema},{start_line},{start_col}>")
            col += (j - i);
            i = j;
            continue

        if ch.isdigit():
            start_line, start_col = linea, col
            j = i
            while j < n and texto[j].isdigit(): j += 1
            lexema = texto[i:j]
            tokens.append(f"<tk_entero,{lexema},{start_line},{start_col}>")
            col += (j - i);
            i = j;
            continue

        if i + 1 < n:
            par = texto[i:i + 2]
            if par in MULTI_OPS:
                start_line, start_col = linea, col
                tokens.append(f"<{MULTI_OPS[par]},{start_line},{start_col}>")
                i += 2;
                col += 2;
                continue

        if ch in SINGLE_OPS:
            start_line, start_col = linea, col
            tokens.append(f"<{SINGLE_OPS[ch]},{start_line},{start_col}>")
            i += 1;
            col += 1;
            continue

        error(linea, col)

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
    print("\n".join(tokens))
    with open("salida_tokens.txt", "w", encoding="utf-8") as out:
        for t in tokens: out.write(t + "\n")
    print("\n Tokens generados correctamente en 'salida_tokens.txt'")


if __name__ == "__main__":
    main()
