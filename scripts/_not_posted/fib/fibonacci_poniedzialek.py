# Ciąg Fibonaciego
# -- rekurencyjnie zadany
# F_0 = 0
# F_1 = 1
# F_n = F_{n-1} + F_{n-2}
# Przykładowo:
# 3:2
# 4:3
# 5:5
# 6:8

def fibonacci_rekurencyjnie(n):
    if n<0:
        msg = f"Fibonacci ma sens dla liczb dodatnich. Dostaliśmy {n}."
        raise ValueError(msg)
    if n<2:
        return n
    return (
        fibonacci_rekurencyjnie(n-1) +
        fibonacci_rekurencyjnie(n-2)
    )

def fibonacci_iteracyjnie(n):
    if n<0:
        msg = f"Fibonacci ma sens dla liczb dodatnich. Dostaliśmy {n}."
        raise ValueError(msg)
    if n<2:
        return n

    a, b = 0,1
    for _ in range(n-1):
        a, b = b, a+b
    return b


fibonacci_dict ={}
def fibonacci_słownikowo(n):
    if n<0:
        msg = f"Fibonacci ma sens dla liczb dodatnich. Dostaliśmy {n}."
        raise ValueError(msg)
    if n<2:
        return n

    if n in fibonacci_dict:
        return fibonacci_dict[n]

    wynik = (
        fibonacci_słownikowo(n-1) +
        fibonacci_słownikowo(n-2)
    )
    fibonacci_dict[n] = wynik
    return wynik


if __name__ == "__main__":
    n = 100

    print(fibonacci_słownikowo(n))

