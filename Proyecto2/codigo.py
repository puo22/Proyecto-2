def fibonacci_iterativo(n):

    # Casos base de la secuencia (F0=0, F1=1)
    if n <= 0:
        return 0
    elif n == 1:
        return 1

    # Inicializamos los dos primeros números
    a, b = 0, 1

    # Iteramos n-1 veces para llegar al n-ésimo término
    # (ya que el primer término, F1, ya está en 'b')
    for _ in range(n - 1):
        # El nuevo 'a' es el antiguo 'b'
        # El nuevo 'b' es la suma de los dos anteriores (antiguo a + antiguo b)
        a, b = b, a + b

    # 'b' contiene el n-ésimo número de Fibonacci
    return b


# --- Ejemplo de uso ---
n_termino = 10
resultado = fibonacci_iterativo(n_termino)
