## Mathematical Background
The underlying asset price is modeled using a Geometric Brownian Motion (GBM):

$$dS_t = \mu S_t dt + \sigma S_t dW_t$$

Where:
* $S_t$: Asset price at time $t$.
* $\mu$: Expected return (drift).
* $\sigma$: Volatility.
* $W_t$: Wiener process (Standard Brownian Motion).

The option pricing follows the **Black-Scholes-Merton** model for European-style derivatives.