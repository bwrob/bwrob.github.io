"""QuantLib callables example."""

import multiprocessing as mp
from dataclasses import dataclass
from itertools import batched, count, takewhile
from typing import TYPE_CHECKING

import QuantLib as ql  # noqa: N813
import tqdm
from tqdm.contrib.concurrent import process_map

if TYPE_CHECKING:
    from collections.abc import Iterable
import marimo

MAX_RATE = 0.15
MAX_WORKERS = 32


@dataclass
class Bond:
    """Callable bond data."""

    rate: float
    id: int


@dataclass
class InputData:
    """Wrapper for bond data."""

    bonds: list[Bond]


def callable_bond(rate: float) -> ql.CallableFixedRateBond:
    """Callable fixed rate bond example.

    The example creates a callable fixed rate bond with the following
    characteristics:

    - Issue date: September 16, 2004
    - Maturity date: September 15, 2012
    - Tenor: Quarterly
    - Accrual convention: Unadjusted
    - Settlement days: 3
    - Face amount: 100
    - Accrual daycount: Actual/Actual (Bond)
    - Coupon rate: 2.5%
    - Callability schedule: 24 call dates with call price of 100.0

    Returns the callable fixed rate bond object.

    """
    callability_schedule = ql.CallabilitySchedule()
    call_price = 100.0
    call_date = ql.Date(15, ql.September, 2006)
    nc = ql.NullCalendar()

    # Number of calldates is 24
    for _i in range(24):
        callability_price = ql.BondPrice(call_price, ql.BondPrice.Clean)
        callability_schedule.append(
            ql.Callability(callability_price, ql.Callability.Call, call_date),
        )
        call_date = nc.advance(call_date, 3, ql.Months)

    issue_date = ql.Date(16, ql.September, 2004)
    maturity_date = ql.Date(15, ql.September, 2012)
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    tenor = ql.Period(ql.Quarterly)
    accrual_convention = ql.Unadjusted
    schedule = ql.Schedule(
        issue_date,
        maturity_date,
        tenor,
        calendar,
        accrual_convention,
        accrual_convention,
        ql.DateGeneration.Backward,
        False,  # noqa: FBT003
    )

    settlement_days = 3
    face_amount = 100
    accrual_daycount = ql.ActualActual(ql.ActualActual.Bond)
    coupon = rate
    return ql.CallableFixedRateBond(
        settlement_days,
        face_amount,
        schedule,
        [coupon],
        accrual_daycount,
        ql.Following,
        face_amount,
        issue_date,
        callability_schedule,
    )


def yield_curve(calc_date: ql.Date) -> ql.YieldTermStructureHandle:
    """Construct a yield curve."""
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    rate = 0.06
    term_structure = ql.FlatForward(
        calc_date,
        rate,
        day_count,
        ql.Compounded,
        ql.Semiannual,
    )
    return ql.RelinkableYieldTermStructureHandle(term_structure)


def hull_white_model(
    a: float,
    s: float,
    term_structure_handle: ql.YieldTermStructureHandle,
) -> ql.HullWhite:
    """Construct a Hull-White model.

    Parameters
    ----------
    a : float
        The mean reversion parameter of the Hull-White model.
    s : float
        The volatility parameter of the Hull-White model.
    term_structure_handle : YieldTermStructureHandle
        The yield curve to use.

    Returns
    -------
    model : HullWhite
        The Hull-White model.

    """
    return ql.HullWhite(term_structure_handle, a, s)


def engine(model: ql.HullWhite, grid_points: int) -> ql.TreeCallableFixedRateBondEngine:
    """Construct a pricing engine.

    Parameters
    ----------
    model : HullWhite
        The Hull-White model to use.
    grid_points : int
        The number of grid points to use in the finite difference method.

    Returns
    -------
    engine : TreeCallableFixedRateBondEngine
        The pricing engine.

    """
    return ql.TreeCallableFixedRateBondEngine(model, grid_points)


def price_bond(
    bond: ql.CallableFixedRateBond,
    pricing_engine: ql.TreeCallableFixedRateBondEngine,
) -> float:
    """Price a callable bond with a given pricing engine.

    Parameters
    ----------
    bond : CallableFixedRateBond
        The callable bond to be priced.
    pricing_engine : TreeCallableFixedRateBondEngine
        The pricing engine to use.

    Returns
    -------
    float
        The clean price of the callable bond.

    """
    bond.setPricingEngine(pricing_engine)
    return float(bond.cleanPrice())


def price_with_setup(
    input_data: InputData,
    *,
    multiprocess: bool = True,
) -> list[float]:
    """Price a list of callable bonds using a Hull-White model.

    Parameters
    ----------
    input_data : InputData
        The input data containing the bonds to be priced.
    multiprocess : bool, optional
        Whether to disable progress bar (default: True).

    Returns
    -------
    list[float]
        A list of clean prices for the callable bonds.

    """
    calc_date = ql.Date(16, 8, 2006)
    ql.Settings.instance().evaluationDate = calc_date

    ql_bonds = [callable_bond(bond.rate) for bond in input_data.bonds]
    term_structure = yield_curve(calc_date)
    model = hull_white_model(0.5, 0.05, term_structure)
    tree_engine = engine(model, 500)
    return [
        round(price_bond(bond, tree_engine), 3)
        for bond in tqdm.tqdm(ql_bonds, disable=multiprocess)
    ]


def main(rates: Iterable[float], *, multiprocess: bool = False) -> None:
    """Price a list of callable bonds using a Hull-White model.

    Parameters
    ----------
    rates : Iterable[float]
        An iterable of interest rates.
    multiprocess : bool, optional
        Whether to run the function in multiprocess mode (default: False).

    """
    bonds = [Bond(rate, i) for i, rate in enumerate(rates)]

    if not multiprocess:
        price_with_setup(InputData(bonds), multiprocess=False)
    else:
        batch_size = 100
        batches = [
            InputData(list(batch))
            for batch in batched(bonds, batch_size)  # noqa: B911
        ]
        process_map(
            price_with_setup,
            batches,
            max_workers=min(MAX_WORKERS, mp.cpu_count() + 4),
        )


if __name__ == "__main__":
    main(
        rates=takewhile(
            lambda x: x < MAX_RATE,
            count(0.03, 0.00001),
        ),
        multiprocess=True,
    )
