def BinomialVanillaEngine(
    process: BlackScholesMertonProcess, type: str, steps: int
) -> BinomialCRRVanillaEngine: ...

class Actual365Fixed:
    def __init__(self, *args) -> None: ...

class AnalyticEuropeanEngine:
    def __init__(self, *args) -> None: ...

class BinomialCRRVanillaEngine:
    def __init__(self, arg2: BlackScholesMertonProcess, steps: int) -> None: ...

class BlackConstantVol:
    def __init__(self, *args) -> None: ...

class BlackScholesMertonProcess:
    def __init__(
        self,
        s0: QuoteHandle,
        dividendTS: YieldTermStructureHandle,
        riskFreeTS: YieldTermStructureHandle,
        volTS: BlackVolTermStructureHandle,
    ) -> None: ...

class BlackVolTermStructureHandle:
    def __init__(self, *args) -> None: ...

class Date:
    def __init__(self, *args) -> None: ...

class EuropeanExercise:
    def __init__(self, date: Date) -> None: ...

class FlatForward:
    def __init__(self, *args) -> None: ...

class Instrument:
    def NPV(self) -> float: ...
    def setPricingEngine(
        self, arg2: AnalyticEuropeanEngine | BinomialCRRVanillaEngine
    ) -> None: ...

class NullCalendar:
    def __init__(self) -> None: ...

class Period:
    def __init__(self, *args) -> None: ...

class PlainVanillaPayoff:
    def __init__(self, type: int, strike: int) -> None: ...

class QuoteHandle:
    def __init__(self, *args) -> None: ...

class Settings:
    @staticmethod
    def instance() -> Settings: ...

class SimpleQuote:
    def __init__(self, *args) -> None: ...

class VanillaOption:
    def __init__(
        self, payoff: PlainVanillaPayoff, exercise: EuropeanExercise
    ) -> None: ...

class YieldTermStructureHandle:
    def __init__(self, *args) -> None: ...
