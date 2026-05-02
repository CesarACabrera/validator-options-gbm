import numpy as np
from scipy.stats import norm
from typing import Tuple, Literal

class QuantEngine:
    """Clase pura de cálculo financiero sin dependencias de GUI."""

    @staticmethod
    def calculate_forward_price(S0: float, r: float, T: float) -> float:
        return S0 * np.exp(r * T)
    
    @staticmethod
    def black_scholes(S0: float, K: float, T: float, r: float, sigma: float, 
                      option_type: Literal['call', 'put']) -> float:
        """Calcula el precio teórico de una opción europea usando BSM."""
        if T <= 0: return max(0.0, S0 - K) if option_type == 'call' else max(0.0, K - S0)
        
        d1 = (np.log(S0 / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == 'call':
            return S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        return K * np.exp(-r * T) * norm.cdf(-d2) - S0 * norm.cdf(-d1)

    @staticmethod
    def simulate_gbm(S0: float, mu: float, sigma: float, T: float, 
                     dt: float = 0.01) -> Tuple[np.ndarray, np.ndarray]:
        """Simula trayectorias mediante Movimiento Browniano Geométrico."""
        n = max(1, int(T / dt))
        t = np.linspace(0, T, n)
        # SDE: dS = mu*S*dt + sigma*S*dW
        W = np.random.standard_normal(size=n - 1)
        W = np.insert(np.cumsum(W), 0, 0) * np.sqrt(dt)
        path = S0 * np.exp((mu - 0.5 * sigma**2) * t + sigma * W)
        return t, path