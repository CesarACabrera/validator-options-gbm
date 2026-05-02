import numpy as np
from scipy.stats import norm
from typing import Tuple
from dataclasses import dataclass

@dataclass
class MarketData:
    """Contenedor de datos para los parámetros del modelo."""
    S0: float  # Precio inicial del activo subyacente (spot price)
    K: float  # Precio de ejercicio de la opción (strike price)
    T: float  # Tiempo al vencimiento en años (time to maturity)
    r: float  # Tasa de interés libre de riesgo (risk-free rate)
    sigma: float  # Volatilidad del activo subyacente (volatility)
    mu: float  # Tasa de retorno esperada (drift)

class QuantEngine:
    """Clase pura de cálculo financiero."""

    @staticmethod
    def calculate_forward_price(data: MarketData) -> float:
        """Calcula el precio forward del activo subyacente."""
        return data.S0 * np.exp(data.r * data.T)
    
    @staticmethod
    def black_scholes(data: MarketData, option_type: str = 'call') -> float:
        """Calcula el precio teórico de una opción europea usando BSM."""

        if data.T < 0:
            raise ValueError("El tiempo al vencimiento no puede ser negativo")
        if data.sigma <= 0:
            raise ValueError("La volatilidad debe ser positiva")
        # Caso vencimiento: devuelve valor intrínseco
        if data.T == 0: 
            if option_type == 'call':
                return max(0.0, data.S0 - data.K)
            return max(0.0, data.K - data.S0)
        
        d1 = (np.log(data.S0 / data.K) + (data.r + 0.5 * data.sigma ** 2) * data.T) / (data.sigma * np.sqrt(data.T))
        d2 = d1 - data.sigma * np.sqrt(data.T)
        
        if option_type == 'call':
            return data.S0 * norm.cdf(d1) - data.K * np.exp(-data.r * data.T) * norm.cdf(d2)
        return data.K * np.exp(-data.r * data.T) * norm.cdf(-d2) - data.S0 * norm.cdf(-d1)

    @staticmethod
    def simulate_gbm(data: MarketData, dt: float = 0.01) -> Tuple[np.ndarray, np.ndarray]:
        """Simula trayectorias mediante Movimiento Browniano Geométrico."""

        n = max(1, int(data.T / dt))
        t = np.linspace(0, data.T, n)
        # SDE: dS = data.mu*S*dt + data.sigma*S*dW
        W = np.random.standard_normal(size=n - 1)
        W = np.insert(np.cumsum(W), 0, 0) * np.sqrt(dt)
        path = data.S0 * np.exp((data.mu - 0.5 * data.sigma**2) * t + data.sigma * W)
        return t, path