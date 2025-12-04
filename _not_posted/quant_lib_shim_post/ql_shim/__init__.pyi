def BinomialVanillaEngine(
    process: BlackScholesMertonProcess, type: str, steps: int
) -> BinomialCRRVanillaEngine: ...

class Actual365Fixed:
    def __init__(self, *args): ...

class AnalyticEuropeanEngine:
    def __init__(self, *args): ...

class BinomialCRRVanillaEngine:
    def __init__(self, arg2: BlackScholesMertonProcess, steps: int): ...

class BlackConstantVol:
    def __init__(self, *args): ...

class BlackScholesMertonProcess:
    def __init__(
        self,
        s0: QuoteHandle,
        dividendTS: YieldTermStructureHandle,
        riskFreeTS: YieldTermStructureHandle,
        volTS: BlackVolTermStructureHandle,
    ): ...

class BlackVolTermStructureHandle:
    def __init__(self, *args): ...

class Date:
    def __init__(self, *args): ...

class EuropeanExercise:
    def __init__(self, date: Date): ...

class FlatForward:
    def __init__(self, *args): ...

class Instrument:
    def NPV(self) -> float: ...
    def setPricingEngine(
        self, arg2: AnalyticEuropeanEngine | BinomialCRRVanillaEngine
    ) -> None: ...

class NullCalendar:
    def __init__(self): ...

class Period:
    def __init__(self, *args): ...

class PlainVanillaPayoff:
    def __init__(self, type: int, strike: int): ...

class QuoteHandle:
    def __init__(self, *args): ...

class Settings:
    @staticmethod
    def instance() -> Settings: ...

class SimpleQuote:
    def __init__(self, *args): ...

class VanillaOption:
    def __init__(self, payoff: PlainVanillaPayoff, exercise: EuropeanExercise): ...

class YieldTermStructureHandle:
    def __init__(self, *args): ...
