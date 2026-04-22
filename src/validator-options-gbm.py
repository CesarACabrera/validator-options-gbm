# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# Copyright (c) 2023 [Tu Nombre/Empresa]
# MIT License
# -----------------------------------------------------------------------------
# VERSIÓN OPTIMIZADA
# -----------------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk, TclError
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import norm
import io
from PIL import Image, ImageTk

class DerivativesVisualizerApp(tk.Tk):
    FIXED_FONT_SIZE = 14
    FIXED_LATEX_FONTSIZE = 16

    def __init__(self):
        super().__init__()
        self.title("Visualizador de Derivados y Estrategias con Opciones")
        self.geometry("2000x1200")
        self.scaling_factor = 1.0
        self.base_latex_fontsize = self.FIXED_LATEX_FONTSIZE
        self.simulated_final_price = None
        self.latex_images = []

        self._configure_styles()
        self._init_variables()
        self._build_gui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind('<Return>', self.run_simulation_and_valuation)
        self.run_simulation_and_valuation()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.configure("TLabel", font=("Helvetica", self.FIXED_FONT_SIZE))
        style.configure("TButton", font=("Helvetica", self.FIXED_FONT_SIZE))
        style.configure("TLabelframe.Label", font=("Helvetica", self.FIXED_FONT_SIZE, "bold"))
        self.option_add("*TEntry*Font", ("Helvetica", self.FIXED_FONT_SIZE))
        self.option_add("*TCombobox*Font", ("Helvetica", self.FIXED_FONT_SIZE))

    def _init_variables(self):
        self.S0_var = tk.DoubleVar(value=100)
        self.K_var = tk.DoubleVar(value=105)
        self.T_var = tk.DoubleVar(value=1.0)
        self.r_var = tk.DoubleVar(value=0.05)
        self.sigma_var = tk.DoubleVar(value=0.2)
        self.mu_var = tk.DoubleVar(value=0.08)
        self.forward_price_var = tk.StringVar()
        self.call_price_var = tk.StringVar()
        self.put_price_var = tk.StringVar()

    def _build_gui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        params_frame = ttk.LabelFrame(main_frame, text="Parámetros de Simulación y Valoración", padding="10")
        params_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.create_parameter_widgets(params_frame)

        plot_frame = ttk.LabelFrame(main_frame, text="Simulación de Precio del Activo (GBM)", padding="10")
        plot_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        results_strategy_frame = ttk.Frame(main_frame)
        results_strategy_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        results_strategy_frame.rowconfigure(1, weight=1)

        results_frame = ttk.LabelFrame(results_strategy_frame, text="Resultados de Valoración", padding="10")
        results_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
        self.create_results_widgets(results_frame)

        strategy_frame = ttk.LabelFrame(results_strategy_frame, text="Análisis de Estrategias con Opciones", padding="10")
        strategy_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(10, 0))
        self.payoff_fig, self.payoff_ax = plt.subplots()
        self.payoff_canvas = FigureCanvasTkAgg(self.payoff_fig, master=strategy_frame)
        self.payoff_canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.create_strategy_widgets(strategy_frame)

        run_button = ttk.Button(main_frame, text="Simular y Calcular (o presiona Enter)", command=self.run_simulation_and_valuation)
        run_button.grid(row=2, column=0, columnspan=2, pady=10)

    def on_closing(self):
        plt.close('all')
        self.quit()
        self.destroy()

    def create_strategy_widgets(self, parent_frame):
        ttk.Label(parent_frame, text="Seleccione una estrategia:").pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))
        self.strategy_var = tk.StringVar()
        strategies = ["Long Call", "Short Call", "Long Put", "Short Put"]
        strategy_combo = ttk.Combobox(parent_frame, textvariable=self.strategy_var, values=strategies, state="readonly")
        strategy_combo.set(strategies[0])
        strategy_combo.pack(side=tk.TOP, fill=tk.X)
        strategy_combo.bind("<<ComboboxSelected>>", self.update_payoff_plot)

    def update_payoff_plot(self, event=None):
        try:
            S0 = self.S0_var.get()
            K = self.K_var.get()
            mu = self.mu_var.get()
            t = self.T_var.get()
            sigma = self.sigma_var.get()
            strategy = self.strategy_var.get()
            option_price = float(self.call_price_var.get().strip('$')) if "Call" in strategy else float(self.put_price_var.get().strip('$'))
        except (ValueError, TclError):
            self.payoff_ax.clear()
            self.payoff_ax.set_title("Diagrama de P&L\n(Esperando datos válidos...)")
            self.payoff_canvas.draw()
            return

        sigma = self.sigma_var.get()
        z = norm.ppf(1 - 0.05 / 2)
        upper_band = max(S0 * np.exp((mu - 0.5 * sigma**2) * t + sigma * z * np.sqrt(t)), K)
        lower_band = min(S0 * np.exp((mu - 0.5 * sigma**2) * t - sigma * z * np.sqrt(t)), K)
        h = 0.1 * (upper_band - lower_band)

        s_t_range = np.linspace(lower_band - h, upper_band + h, 200)

        if strategy == "Long Call":
            pnl = np.maximum(s_t_range - K, 0) - option_price
            breakeven = K + option_price
        elif strategy == "Short Call":
            pnl = -(np.maximum(s_t_range - K, 0)) + option_price
            breakeven = K + option_price
        elif strategy == "Long Put":
            pnl = np.maximum(K - s_t_range, 0) - option_price
            breakeven = K - option_price
        else:
            pnl = -(np.maximum(K - s_t_range, 0)) + option_price
            breakeven = K - option_price

        self.payoff_ax.clear()
        self.payoff_ax.plot(s_t_range, pnl, label=f"P&L de {strategy}", color='blue', linewidth=2.5)
        self.payoff_ax.axhline(y=0, color='black', linestyle='--', linewidth=1.5)
        self.payoff_ax.axvline(x=K, color='grey', linestyle=':', linewidth=1.5, label=f'Strike K = ${K:.2f}')
        self.payoff_ax.plot(breakeven, 0, 'o', color='purple', markersize=8, label=f'Break-even = ${breakeven:.2f}')
        self.payoff_ax.fill_between(s_t_range, pnl, 0, where=(pnl > 0), color='green', alpha=0.2, label='Zona de Ganancia')
        self.payoff_ax.fill_between(s_t_range, pnl, 0, where=(pnl < 0), color='red', alpha=0.2, label='Zona de Pérdida')
        self.payoff_ax.annotate(f'Break-even\n${breakeven:.2f}', xy=(breakeven, 0), xytext=(breakeven, pnl.mean()*.8), arrowprops=dict(facecolor='purple', shrink=0.05, width=1, headwidth=5), ha='center')
        

        s_t_simulated = self.simulated_final_price
        if s_t_simulated is not None:
            pnl_at_simulated_price = np.interp(s_t_simulated, s_t_range, pnl)
            result_color = 'green' if pnl_at_simulated_price >= 0 else 'red'
            self.payoff_ax.plot([s_t_simulated, s_t_simulated], [0, pnl_at_simulated_price],
                                color=result_color, linewidth=4, alpha=0.7,
                                label=f'Resultado Simulado: ${pnl_at_simulated_price:.2f}')
            self.payoff_ax.plot(s_t_simulated, pnl_at_simulated_price, 'o',
                                color=result_color, markeredgecolor='black', markersize=12)
            ylim = self.payoff_ax.get_ylim()
            self.payoff_ax.annotate(f'Precio Final:\n${s_t_simulated:.2f}',
                                    xy=(s_t_simulated, pnl_at_simulated_price),
                                    xytext=(s_t_simulated, pnl_at_simulated_price + (ylim[1] - ylim[0]) * 0.25),
                                    arrowprops=dict(facecolor='black', arrowstyle="->", connectionstyle="arc3,rad=.3"),
                                    ha='center', va='bottom',
                                    bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="black", lw=1, alpha=0.8))

        self.payoff_ax.set_title(f"Diagrama de Ganancia/Pérdida: {strategy}")
        self.payoff_ax.set_xlabel("Precio del Activo en el Vencimiento ($S_T$)")
        self.payoff_ax.set_ylabel("Ganancia / Pérdida por Acción ($)")
        self.payoff_ax.legend(fontsize=12)
        self.payoff_ax.grid(True, linestyle=':')
        self.payoff_canvas.draw()

    def run_simulation_and_valuation(self, event=None):
        try:
            S0 = self.S0_var.get()
            K = self.K_var.get()
            T = self.T_var.get()
            r = self.r_var.get()
            sigma = self.sigma_var.get()
            mu = self.mu_var.get()
            time, path = self.simulate_gbm(S0, mu, sigma, T)
            self.simulated_final_price = path[-1]
            self.plot_simulation(time, path, S0, K)
            self.forward_price_var.set(f"${self.calculate_forward_price(S0, r, T):.4f}")
            self.call_price_var.set(f"${self.black_scholes(S0, K, T, r, sigma, 'call'):.4f}")
            self.put_price_var.set(f"${self.black_scholes(S0, K, T, r, sigma, 'put'):.4f}")
            self.update_payoff_plot()
        except Exception as e:
            self.forward_price_var.set("Error")
            self.call_price_var.set("Error")
            self.put_price_var.set("Error")
            self.simulated_final_price = None
            self.update_payoff_plot()
            print(f"Error: {e}")

    def create_latex_image(self, latex_string, base_fontsize):
        scaled_fontsize = int(base_fontsize * self.scaling_factor)
        scaled_dpi = int(100 * self.scaling_factor)
        fig = plt.figure(figsize=(1, 0.5), dpi=scaled_dpi)
        fig.text(0, 0, latex_string, fontsize=scaled_fontsize, va="bottom")
        buf = io.BytesIO()
        fig.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        img = Image.open(buf)
        photo_image = ImageTk.PhotoImage(img)
        plt.close(fig)
        return photo_image

    def create_parameter_widgets(self, parent_frame):
        params = [
            (r'Precio Inicial del Subyacente ($S_0$):', self.S0_var),
            (r'Precio Ejercicio (Strike Price) ($K$):', self.K_var),
            (r'Vencimiento ($T$, años):', self.T_var),
            (r'Tasa Libre Riesgo ($r_f$):', self.r_var),
            (r'Volatilidad ($\sigma$):', self.sigma_var),
            (r'Deriva Esperada ($\mu$):', self.mu_var)
        ]
        for idx, (latex_text, var) in enumerate(params):
            img = self.create_latex_image(latex_text, self.base_latex_fontsize)
            self.latex_images.append(img)
            label = ttk.Label(parent_frame, image=img)
            entry = ttk.Entry(parent_frame, textvariable=var, width=10)
            label.grid(row=idx // 3, column=(idx % 3) * 2, sticky=tk.W, padx=5, pady=5)
            entry.grid(row=idx // 3, column=(idx % 3) * 2 + 1, sticky=tk.W, padx=5, pady=5)

    def create_results_widgets(self, parent_frame):
        results = [
            (r'Precio Forward/Futuro ($F$):', self.forward_price_var),
            (r'Precio Opción Call ($C$):', self.call_price_var),
            (r'Precio Opción Put ($P$):', self.put_price_var)
        ]
        value_font = ("Helvetica", 15)
        for latex_text, var in results:
            img = self.create_latex_image(latex_text, self.base_latex_fontsize + 2)
            self.latex_images.append(img)
            ttk.Label(parent_frame, image=img).pack(anchor=tk.W, pady=(10, 0))
            ttk.Label(parent_frame, textvariable=var, font=value_font).pack(anchor=tk.W, pady=(0, 15), padx=5)

    def simulate_gbm(self, S0, mu, sigma, T, dt=0.01):
        n = int(T / dt)
        t = np.linspace(0, T, n)
        W = np.insert(np.cumsum(np.random.standard_normal(size=n - 1)), 0, 0) * np.sqrt(dt)
        X = (mu - 0.5 * sigma ** 2) * t + sigma * W
        return t, S0 * np.exp(X)

    def plot_simulation(self, t, p, S0, K):
        plt.rc('font', size=12)
        self.ax.clear()
        self.ax.plot(t, p, label="Precio de Activo", linewidth = 2)
        self.ax.axhline(y=S0, color='g', ls='--', linewidth = 2, label=rf'$S_0={S0}$')
        self.ax.axhline(y=K, color='r', ls='--', linewidth = 2,label=rf'$K={K}$')
        self.ax.set_title("Evolución del Precio del Activo (Simulación)")
        self.ax.set_xlabel("Tiempo (años)")
        self.ax.set_ylabel("Precio del Activo ($)")
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()

    @staticmethod
    def calculate_forward_price(S0, r, T):
        return S0 * np.exp(r * T)

    @staticmethod
    def black_scholes(S0, K, T, r, sigma, o):
        d1 = (np.log(S0 / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        if o == 'call':
            return S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            return K * np.exp(-r * T) * norm.cdf(-d2) - S0 * norm.cdf(-d1)

if __name__ == "__main__":
    app = DerivativesVisualizerApp()
    app.mainloop()