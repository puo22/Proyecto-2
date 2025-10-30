# Proyecto 2: Analizador Sintáctico en Python


Autores: 
+ Sofía Londoño 
+ Paula Ortiz


---

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


---

## Ejecución del analizador

### 1️. Generar los tokens
Primero, ejecuta el analizador léxico:
```bash
python lexer.py
```
### 2. Ejecutar el analizador sintáctico
```bash
python analisis_gramatica.py
```

-Si todo está corracto, en consola se muestra: 
```bash
Análisis sintáctico finalizado correctamente.
```


---

## Pruebas realizadas

### - [x] Ejemplo uno
```bash
import math

class Circulo:
    def __init__(self, radio):
        self.radio = radio

    def calcular_area(self):
        return math.pi * (self.radio ** 2)

    def mostrar_area(self):
        area = self.calcular_area()
        print("El área del círculo es:", area)

# Ejemplo de uso
c = Circulo(5)
c.mostrar_area()
```
Salida en consola: 
```bash
Análisis sintáctico finalizado correctamente.
```

### - [x] Ejemplo dos:
```bash
for i range(10):
    print(i)
```
Salida en consola: 
```bash
<1,7> Error sintactico: se encontro: “range”; se esperaba: “in”.
```

### - [x] Ejemplo tres:
```bash
x = 0
while x < 5
    print(x)
    x += 1
```
Salida en consola: 
```bash
<2,12> Error sintactico: se encontro: “\n”; se esperaba: “tk_dos_puntos”.
```

### - [x] Ejemplo cuatro:
```bash
# Importaciones
import math
#  Clases
class Contador:
    # Funciones (un método y el constructor)
    def _init_(self, valor_inicial):
        print("bienvenido")


#  Funcion
def es_positivo(numero):
    # Condicionales (if/else)
    # Expresiones (de comparación)
    if numero > 0:
        # Return
        return "Positivo"
    else:
        # Return
        return "No Positivo"
    

print("Inicio del Script")

mi_contador = Contador(3)

# 8. Bucle While
print("Iniciando bucle 'while':")
while mi_contador > 0:
    print("El contador vale:")

    mi_contador = mi_contador - 1 

print("--- Fin del bucle 'while' ---")

lista_numeros = [2, 5, 10]

# 8. Bucle For
print("Iniciando bucle 'for':")
for num in lista_numeros:
    estado = es_positivo(num)
    print("El número")

    potencia = math(num, 2)  
    print("Su cuadrado es:")

print("Fin del Script")
```
Salida en consola:
```bash
Análisis sintáctico finalizado correctamente.
```

### - [x] Ejemplo cinco:
```bash
def sumar a, b:
    return a + b
```
Salida en consola:
```bash
<1,11> Error sintactico: se encontro: “a”; se esperaba: “tk_par_izq”.
```













