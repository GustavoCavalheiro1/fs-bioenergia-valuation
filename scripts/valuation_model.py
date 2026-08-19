from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CHARTS = ROOT / "assets" / "charts"

YEARS = ["FY25 (Base)", "FY26", "FY27", "FY28", "FY29", "FY30"]
FORECAST_YEARS = YEARS[1:]
REVENUE = np.array([10_688_829, 11_971_488, 13_168_637, 14_222_128, 15_075_456, 15_678_474], dtype=float)
EBIT = np.array([2_390_462, 2_633_727, 2_900_000, 3_128_868, 3_316_600, 3_449_264], dtype=float)
NOPAT = np.array([1_577_705, 1_738_260, 1_914_000, 2_065_053, 2_188_956, 2_276_515], dtype=float)
D_AND_A = np.array([308_538, 340_000, 373_000, 401_000, 422_000, 438_000], dtype=float)
CAPEX = np.array([-958_000, -958_000, -922_000, -853_000, -754_000, -627_000], dtype=float)
WORKING_CAPITAL = np.array([-52_336, -26_000, -24_000, -21_000, -17_000, -14_000], dtype=float)
FCFF = np.array([1_305_675, 1_095_090, 1_341_514, 1_591_626, 1_840_512, 2_073_674], dtype=float)
NET_DEBT = 6_800_491.0
BASE_WACC = 0.15
BASE_G = 0.03


def calculate_valuation(wacc: float = BASE_WACC, terminal_growth: float = BASE_G) -> dict[str, float]:
    """Calcula o DCF em R$ mil para um par WACC/g."""
    if wacc <= terminal_growth:
        raise ValueError("O WACC deve ser maior que o crescimento na perpetuidade.")
    periods = np.arange(1, len(FORECAST_YEARS) + 1, dtype=float)
    pv_explicit = float(np.sum(FCFF[1:] / (1 + wacc) ** periods))
    terminal_fcff = float(FCFF[-1] * (1 + terminal_growth))
    terminal_value = float(terminal_fcff / (wacc - terminal_growth))
    pv_terminal = float(terminal_value / (1 + wacc) ** len(periods))
    enterprise_value = pv_explicit + pv_terminal
    equity_value = enterprise_value - NET_DEBT
    return {
        "pv_explicit": pv_explicit,
        "terminal_fcff": terminal_fcff,
        "terminal_value": terminal_value,
        "pv_terminal": pv_terminal,
        "enterprise_value": enterprise_value,
        "net_debt": NET_DEBT,
        "equity_value": equity_value,
    }


def advanced_sensitivity(
    wacc_values: np.ndarray | None = None,
    growth_values: np.ndarray | None = None,
) -> pd.DataFrame:
    """Retorna uma matriz de Equity Value em R$ bilhões."""
    wacc_values = np.asarray(wacc_values if wacc_values is not None else np.arange(0.10, 0.201, 0.005))
    growth_values = np.asarray(growth_values if growth_values is not None else np.arange(0.01, 0.051, 0.005))
    rows = []
    for wacc in wacc_values:
        for growth in growth_values:
            if wacc <= growth:
                equity = np.nan
            else:
                equity = calculate_valuation(float(wacc), float(growth))["equity_value"] / 1_000_000
            rows.append({"WACC": wacc, "Crescimento perpétuo": growth, "Equity Value (R$ bi)": equity})
    return pd.DataFrame(rows)


def projections_dataframe() -> pd.DataFrame:
    return pd.DataFrame({
        "Ano": YEARS,
        "Receita (R$ mil)": REVENUE,
        "EBIT (R$ mil)": EBIT,
        "NOPAT (R$ mil)": NOPAT,
        "D&A (R$ mil)": D_AND_A,
        "CAPEX (R$ mil)": CAPEX,
        "Capital de giro (R$ mil)": WORKING_CAPITAL,
        "FCFF (R$ mil)": FCFF,
    })


if __name__ == "__main__":
    CHARTS.mkdir(parents=True, exist_ok=True)
    matrix = advanced_sensitivity()
    matrix.to_csv(CHARTS / "sensibilidade_avancada.csv", index=False, encoding="utf-8-sig")
    print(f"Sensibilidade avançada exportada para {CHARTS / 'sensibilidade_avancada.csv'}")
