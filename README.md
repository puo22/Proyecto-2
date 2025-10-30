# Proyecto 2: Analizador Sintáctico en Python

## Descripción

Este proyecto implementa un analizador sintáctico descendente predictivo en Python.  
El analizador toma como entrada una lista de tokens generada por el analizador léxico (`lexer.py`) y valida si el código fuente cumple con la gramática definida.

Soporta estructuras como:
- Declaraciones de funciones y clases.
- Estructuras de control (`if`, `elif`, `else`, `for`, `while`).
- Asignaciones simples, múltiples y con anotaciones de tipo.
- Expresiones aritméticas y lógicas.
- Llamadas a funciones, acceso a atributos (`obj.atributo`) y operadores de potencia (`**`).
- Indentación y dedentación (bloques anidados).

---

## Funcionamiento general

El flujo de análisis se realiza en tres etapas principales:

1. **Análisis Léxico** → Generado por `lexer.py`, produce el archivo `salida_tokens.txt`.
2. **Análisis Sintáctico** → `analisis_gramatica.py` carga los tokens y verifica la estructura del programa.
3. **Resultados** → Los mensajes se muestran en consola y también se guardan en `salida parser.txt`.

El parser está implementado como un analizador descendente predictivo LL(1), que lee de izquierda a derecha y genera derivaciones por la izquierda.  
Cada regla gramatical se implementa como un método `parse_*` dentro de la clase `Parser`.

---

## Características principales

- **Tipo de parser:** LL(1) descendente recursivo.   
- **Manejo de errores:**  
  - Errores sintácticos detallados con línea y columna.  
  - Errores específicos de indentación.  
  - Manejo de tokens inesperados.  

---

## Estructura del proyecto
Proyecto2/
── lexer.py # Analizador léxico
── analisis_gramatica.py # Analizador sintáctico LL(1)
── codigo.py # Código fuente de prueba
── salida_tokens.txt # Salida del analizador léxico
── salida parser.txt # Resultados del analizador sintáctico
── README.md # Este archivo









