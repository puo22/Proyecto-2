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
