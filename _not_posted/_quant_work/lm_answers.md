## Project idea that ilustrate diffference between quant analyst and quant dev

It describes in a bit naive way how to construct 'implied probability distributions' - current market view on what are probabilities of a equity asset to have a given value at a set moment in the future. This touches one of the fundamentals of quant finance - how to make math models work with actual market observables and behaviours.

Let's say you have this procedure implemented in Python, in a notebook or a script. This is fun little exercise on it's own. But for real-life usage it is only the beginning.

For a Quant Analyst the path diverges:

- valuation quant would start thinking about the interpolation assumptions, if this procedure doesn't introduce arbitrage and how the constructed distribution (built using simple and liquid products) can be used to price more exotic, illiquid ones.
- risk quant could try to use it to hedge tail risk of a portfolio using OOTM options in a cheapest and still effective way
- quant researcher could build such distributions for different expiries, compare them and look for statistical inefficiencies to take advantage of for profit
- quant trader would look how to execute a trading strategy they devised in most cost-effective way

The Quant Developer has different considerations. Their role is subservient to the quant, and depends majorly of which of the above he works with. But there are many angles here:

- productionalize the script, make it strucured and reusable (functions, classes, linter, static typing, docstrings, tests)
- make it work with different market data providers (dependency injection, adapter pattern)
- consider the CPU bound performance of a given interpolation scheme or root finding algorithm. There are many choices for both. Usually the more 'quanty' ones are more computationally expensive. Try to optimize, given the use case. Sometimes just using scipy is enough, sometimes dedicated algorithms (like Jaeckel2013) need to be used. If this is really performance critical, the compute might need to be delegated to a compiled extension (rust + pyo3 + maturin)
- maybe it's fetching the market data that is slow. maybe async should be used? What if the vendor API call is blocking (asyncio.to_thread). What if there are restrictions on API calls? should we use a semaphor or a limiter?
- What if the performance of lookup is crucial, but we don't need live view of the market, but only EOD data (risk quant perspective). Then we should use some scheduler or orchestrator to run in batch overnight and put it all the market data and calculation results to a database.
- What if we work for the quant trader, and they need a good visualisation and gui to have open at all times on one of their 6 displays? We need to set up a dashboard. What framework should we use? Is single python process good enough? Or do we need to split it into backend API and frontend dashboard?

In certain projects there might be a rigid technical framwork and practices in place and the quant might be the one implementing the production solution from the start. But the main considarations they think through remain.
