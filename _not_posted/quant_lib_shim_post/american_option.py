import ql_shim as ql
from price import binomial_price, black_scholes_price

__CALCULATION_DATE = ql.Date(8, 5, 2015)


def european_option():
    maturity_date = ql.Date(15, 1, 2016)
    strike_price = 130
    option_type = ql.Option.Call
    payoff = ql.PlainVanillaPayoff(option_type, strike_price)
    exercise = ql.EuropeanExercise(maturity_date)
    return ql.VanillaOption(payoff, exercise)


def bsm_process():
    spot_price = 127.62
    volatility = 0.20  # the historical vols for a year
    dividend_rate = 0.0163

    risk_free_rate = 0.001
    day_count = ql.Actual365Fixed()
    calendar = ql.NullCalendar()
    spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot_price))
    flat_ts = ql.YieldTermStructureHandle(
        ql.FlatForward(__CALCULATION_DATE, risk_free_rate, day_count)
    )
    dividend_yield = ql.YieldTermStructureHandle(
        ql.FlatForward(__CALCULATION_DATE, dividend_rate, day_count)
    )
    flat_vol_ts = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(__CALCULATION_DATE, calendar, volatility, day_count)
    )
    return ql.BlackScholesMertonProcess(
        spot_handle, dividend_yield, flat_ts, flat_vol_ts
    )


def main():
    ql.Settings.instance().evaluationDate = __CALCULATION_DATE
    european_opt = european_option()
    process = bsm_process()

    bs_price = black_scholes_price(european_opt, process)
    print(f"Black-Scholes Price: {bs_price:.4f}")

    steps = [5, 10, 25, 50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600, 51200]
    prices = [binomial_price(european_opt, process, step) for step in steps]
    for step, price in zip(steps, prices, strict=False):
        print(f"Steps: {step:6d}, Binomial Price: {price:.6f}")
