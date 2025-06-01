"""An integrator class that allows to perform integration using different schemes."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from logging import getLogger
from typing import override

import numpy as np

logger = getLogger(__name__)


class IntegrationScheme(ABC):
    """Abstract base class for integration schemes."""

    @abstractmethod
    def integrate(
        self,
        integrand: Callable[[float], float],
        *,
        start: float,
        end: float,
    ) -> float:
        """Abstract method for integrating a function."""


class RectangleScheme(IntegrationScheme):
    """Scheme for rectangle integration."""

    def __init__(
        self,
        steps: int,
    ) -> None:
        """Initialize the rectangle integration config."""
        if steps <= 0:
            msg = "Steps must be greater than 0."
            raise ValueError(msg)
        self.__steps = steps

    @override
    def __str__(self) -> str:
        """Return the string representation of the scheme."""
        return f"Rectangle scheme with {self.__steps} steps"

    @override
    def integrate(
        self,
        integrand: Callable[[float], float],
        *,
        start: float,
        end: float,
    ) -> float:
        """Integrates a function using rectangle integration."""
        x_points = np.linspace(start, end, self.__steps)
        values = integrand(x_points)
        dx = (end - start) / np.float64(self.__steps)
        return np.sum(values) * dx


class MonteCarloScheme(IntegrationScheme):
    """Scheme for Monte Carlo integration."""

    def __init__(
        self,
        random_points: int,
        random_seed: int | None = None,
    ) -> None:
        """Initialize the rectangle integration config."""
        if random_points <= 0:
            msg = "Points must be greater than 0."
            raise ValueError(msg)
        self.__random_points = random_points
        self.__random_seed = random_seed

    @override
    def __str__(self) -> str:
        """Return the string representation of the scheme."""
        points_msg = f"Monte Carlo scheme with {self.__random_points} random points"
        seed_msg = f" and seed {self.__random_seed}" if self.__random_seed else ""
        return f"{points_msg}{seed_msg}"

    @override
    def integrate(
        self,
        integrand: Callable[[float], float],
        *,
        start: float,
        end: float,
    ) -> float:
        """Integrates a function using Monte Carlo integration."""
        rng = np.random.default_rng(2137)
        x_points = rng.uniform(start, end, self.__random_points)
        values = integrand(x_points)
        average_dx = (end - start) / np.float64(self.__random_points)
        return np.sum(values) * average_dx


class Integrator:
    """An integrator class.

    Allows to perform integration using different schemes as strategies.

    """

    def __init__(
        self,
        integrand: Callable[[float], float],
        interval_start: float,
        interval_end: float,
    ) -> None:
        """Initialize the integrator class."""
        if interval_start >= interval_end:
            msg = "Start value must be less than end value."
            raise ValueError(msg)
        self.__integrand = integrand
        self.__interval_start = interval_start
        self.__interval_end = interval_end

    def __call__(
        self,
        scheme: IntegrationScheme,
    ) -> float:
        """Calculate the definite integral value of a function.

        Args:
        ----
            scheme: integration scheme

        """
        logger.info("Using %s.", scheme)
        return scheme.integrate(
            self.__integrand,
            start=self.__interval_start,
            end=self.__interval_end,
        )


if __name__ == "__main__":
    # The example usage of the `Integrator` class.

    from scipy.integrate import quad

    start, end = 0, np.pi / 2.0

    def f(x: float) -> float:  # noqa: D103
        return np.sin(x) + np.cos(x)

    scipy_quad, err = quad(f, start, end)
    logger.info(scipy_quad)

    integrator = Integrator(
        f,
        interval_start=start,
        interval_end=end,
    )

    iterations: list[int] = [2**i for i in range(0, 21, 5)]
    rectangle_results = [integrator(RectangleScheme(steps=i)) for i in iterations]
    mc_results = [integrator(MonteCarloScheme(random_points=i)) for i in iterations]

    logger.info("Rectangle scheme results:\n %s.", rectangle_results)
    logger.info("Monte Carlo scheme results:\n %s.", mc_results)
