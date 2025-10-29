# 1. Importaciones
# Importamos el módulo 'math' (aunque solo lo usamos para un cálculo simple)
import math
# 2. Clases
class Contador:
    # 3. Funciones (un método, el constructor)
    def _init_(self, valor_inicial):
        # 4. Asignaciones
        print("bienvenido")


# 3. Funciones (una función normal)
def es_positivo(numero):
    # 5. Condicionales (if/else)
    # 6. Expresiones (de comparación)
    if numero > 0:
        # 7. Return
        return "Positivo"
    else:
        # 7. Return
        return "No Positivo"


# --- Aquí comienza la ejecución principal ---

print("--- Inicio del Script ---")

# 4. Asignaciones (creamos una instancia de la clase)
mi_contador = Contador(3)

# 8. Bucles (While)
print("Iniciando bucle 'while':")
while mi_contador > 0:
    # 9. Print
    print("El contador vale:")

    # 4. Asignaciones y 6. Expresiones (aritmética)
    mi_contador = mi_contador - 1  # Restamos 1

print("--- Fin del bucle 'while' ---")

# 4. Asignaciones (creamos una lista)
lista_numeros = [2, 5, 10]

# 8. Bucles (For)
print("Iniciando bucle 'for':")
for num in lista_numeros:
    # 4. Asignaciones (guardamos el resultado de una función)
    # 6. Expresiones (llamada a una función)
    estado = es_positivo(num)

    # 9. Print (usando la asignación anterior)
    print("El número")

    # 6. Expresiones (usando el módulo importado 'math')
    potencia = math(num, 2)  # Eleva el número al cuadrado
    print("Su cuadrado es:")

print("--- Fin del Script ---")