from time import perf_counter

import ql_shim as ql


def black_scholes_price(european_option, bsm_process) -> float:
    european_option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
    return european_option.NPV()


def binomial_price(european_option, bsm_process, steps) -> float:
    start_time = perf_counter()
    binomial_engine = ql.BinomialVanillaEngine(bsm_process, "crr", steps)
    european_option.setPricingEngine(binomial_engine)
    npv = european_option.NPV()
    end_time = perf_counter()
    elapsed_time = end_time - start_time
    print(f"Steps: {steps:6d}, Time taken: {elapsed_time:.6f} seconds")
    return npv
