# Ciąg Fibonacciego:
# Ciąg liczb naturalnych zdefiniowany rekurencyjnie:
# F_0 = 0
# F_1 = 1
# F_n = F_{n-1} + F_{n-2} dla n >=2
#
# Przykład:
# F_2 = 1
# F_3 = 2
# F_4 = 3
# F_5 = 5
# F_6 = 8
# F_40 = ?

def fibonacci_rekurencja(n):
    # sprawdzamy, że n>=0
    if n < 0:
        msg = (
            "Fibbonaci jest zdefiniowany dla n>0"
            f", dostaliśmy {n}"
        )
        raise ValueError(msg)
    if n==0:
        return 0
    if n==1:
        return 1
    return (fibonacci_rekurencja(n-1)
            + fibonacci_rekurencja(n-2)
        )

def fibonacci_liniowy(n):
    if n < 0:
        msg = (
            "Fibbonaci jest zdefiniowany dla n>0"
            f", dostaliśmy {n}"
        )
        raise ValueError(msg)
    if n==0:
        return 0
    if n==1:
        return 1

    a,b = 0,1
    for _ in range(n-1) :
        a,b = b, a+b
    return b


fibbonaci_pamięć = {}

def fibonacci_słownik(n):
    # sprawdzamy, że n>=0
    if n < 0:
        msg = (
            "Fibbonaci jest zdefiniowany dla n>0"
            f", dostaliśmy {n}"
        )
        raise ValueError(msg)
    if n==0:
        return 0
    if n==1:
        return 1

    if n in fibbonaci_pamięć:
        return fibbonaci_pamięć[n]

    wynik = fibonacci_słownik(n-1) + fibonacci_słownik(n-2)
    fibbonaci_pamięć[n] = wynik
    return wynik

if __name__ == "__main__":
    n = 50
    print(fibonacci_słownik(n))
    # print([fibonacci_rekurencja(n) for n in range(n+1)])
