from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "charts"
OUT.mkdir(parents=True, exist_ok=True)

# Base financeira transcrita do Anexo A do PDF.
years = ["FY25 (Base)", "FY26", "FY27", "FY28", "FY29", "FY30"]
revenue = np.array([10_688_829, 11_971_488, 13_168_637, 14_222_128, 15_075_456, 15_678_474])
growth = [np.nan, 12, 10, 8, 6, 4]
ebit = np.array([2_390_462, 2_633_727, 2_900_000, 3_128_868, 3_316_600, 3_449_264])
taxes = np.array([-812_757, -895_000, -986_000, -1_063_815, -1_127_644, -1_172_749])
nopat = np.array([1_577_705, 1_738_260, 1_914_000, 2_065_053, 2_188_956, 2_276_515])
d_and_a = np.array([308_538, 340_000, 373_000, 401_000, 422_000, 438_000])
capex = np.array([-958_000, -958_000, -922_000, -853_000, -754_000, -627_000])
working_capital = np.array([-52_336, -26_000, -24_000, -21_000, -17_000, -14_000])
fcff = np.array([1_305_675, 1_095_090, 1_341_514, 1_591_626, 1_840_512, 2_073_674])
discount_factor = np.array([np.nan, 0.870, 0.756, 0.658, 0.572, 0.497])
fcff_discounted = np.array([np.nan, 953_000, 1_014_256, 1_047_234, 1_052_756, 1_030_589])

# Valuation informado no PDF.
wacc, terminal_growth = 0.15, 0.03
pv_explicit = 5_097_562
fcff_terminal = 2_135_884
terminal_value = 17_799_035
pv_terminal = 8_846_120
enterprise_value = 13_943_682
net_debt = 6_800_491  # EV - Equity Value, inferido do quadro do Anexo A.
equity_value = 7_143_191
reported_equity_value = 7.19

# Sensibilidade do Equity Value em R$ bilhões.
NAV = np.array([[9.67, 10.73, 12.01], [6.50, 7.19, 7.99], [4.02, 4.53, 5.12]])
wacc_labels = ["14,0%", "15,0%", "16,0%"]
g_labels = ["2,5%", "3,0%", "3,5%"]

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({
    "font.family": "DejaVu Sans", "axes.titleweight": "bold", "axes.titlesize": 14,
    "axes.labelsize": 10, "figure.dpi": 150, "savefig.dpi": 180,
    "axes.spines.top": False, "axes.spines.right": False,
})
navy, green, orange, red, gray = "#102A43", "#238B66", "#E07A38", "#C94C4C", "#61758A"


def bi(values):
    return values / 1_000_000


def save(fig, name):
    fig.tight_layout(pad=1.0)
    fig.savefig(OUT / name, facecolor="white")
    plt.close(fig)


# 1. Receita, EBIT e crescimento.
fig, ax1 = plt.subplots(figsize=(10, 5.6))
x = np.arange(len(years))
ax1.plot(x, bi(revenue), color=navy, marker="o", linewidth=2.5, label="Receita líquida")
ax1.plot(x, bi(ebit), color=green, marker="o", linewidth=2.5, label="EBIT")
ax1.set_xticks(x, years)
ax1.set_ylabel("R$ bilhões")
ax1.set_title("FS Bioenergia | Evolução da receita e do EBIT")
ax1.legend(loc="upper left", frameon=False, ncols=2)
ax1.set_ylim(0, 17)
for i, value in enumerate(bi(revenue)):
    ax1.annotate(f"{value:.1f}", (i, value), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=8, color=navy)
ax2 = ax1.twinx()
ax2.bar(x, np.nan_to_num(growth), width=0.42, alpha=0.20, color=orange, label="Crescimento da receita")
ax2.set_ylabel("Crescimento da receita (%)")
ax2.set_ylim(0, 16)
ax2.legend(loc="upper right", frameon=False)
save(fig, "01_operacao_receita_ebit.png")

# 2. FCFF, D&A, CAPEX e capital de giro.
fig, ax = plt.subplots(figsize=(11, 5.8))
ax.plot(x, bi(fcff), color=green, marker="o", linewidth=2.7, label="FCFF")
ax.plot(x, bi(d_and_a), color=navy, marker="o", linewidth=2.0, label="Depreciação e amortização")
ax.plot(x, bi(-capex), color=orange, marker="o", linewidth=2.0, label="CAPEX")
ax.plot(x, bi(-working_capital), color=gray, marker="o", linewidth=2.0, label="Variação do capital de giro")
ax.set_xticks(x, years)
ax.set_ylabel("R$ bilhões")
ax.set_title("Geração de caixa e principais usos de capital")
ax.legend(frameon=False, ncols=2)
save(fig, "02_fcff_estrutura_caixa.png")

# 3. FCFF nominal versus descontado.
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.bar(x - 0.20, bi(fcff), width=0.38, color=green, label="FCFF")
ax.bar(x + 0.20, bi(np.nan_to_num(fcff_discounted)), width=0.38, color=orange, label="FCFF descontado")
ax.set_xticks(x, years)
ax.set_ylabel("R$ bilhões")
ax.set_title("Fluxo de caixa livre: nominal versus descontado")
ax.legend(frameon=False, ncols=2)
for i, value in enumerate(bi(fcff)):
    ax.text(i - 0.20, value + 0.04, f"{value:.2f}", ha="center", va="bottom", fontsize=8)
ax.text(0.98, 0.95, "WACC: 15% | g: 3%", transform=ax.transAxes, ha="right", va="top", fontsize=9, color=gray)
save(fig, "03_fcff_descontado.png")

# 4. Bridge do valuation DCF.
labels = ["PV FCFF\nexplícito", "PV valor\nterminal", "Enterprise\nValue", "(-) Dívida\nlíquida", "Equity\nValue"]
values = [pv_explicit / 1e6, pv_terminal / 1e6, enterprise_value / 1e6, -net_debt / 1e6, equity_value / 1e6]
fig, ax = plt.subplots(figsize=(10, 5.4))
colors = [navy, orange, green, red, navy]
bar = ax.bar(labels, values, color=colors)
ax.axhline(0, color="#334E68", linewidth=0.8)
ax.set_ylabel("R$ milhões")
ax.set_title("Valuation DCF | Reconciliação até o Equity Value")
for rect, value in zip(bar, values):
    ax.text(rect.get_x() + rect.get_width() / 2, value + (260 if value >= 0 else -500), f"{value:,.0f}".replace(",", "."), ha="center", va="bottom" if value >= 0 else "top", fontsize=9, fontweight="bold")
ax.text(0.98, 0.95, f"Equity Value reportado: R$ {reported_equity_value:.2f} bi", transform=ax.transAxes, ha="right", va="top", color=gray)
save(fig, "04_valuation_bridge.png")

# 5. Sensibilidade do Equity Value.
cmap = LinearSegmentedColormap.from_list("valuation", ["#F7D6C4", "#FFF4D6", "#A9DCC8"])
fig, ax = plt.subplots(figsize=(8.5, 5.5))
im = ax.imshow(NAV, cmap=cmap, aspect="auto", vmin=NAV.min(), vmax=NAV.max())
ax.set_xticks(range(3), g_labels)
ax.set_yticks(range(3), wacc_labels)
ax.set_xlabel("Crescimento na perpetuidade (g)")
ax.set_ylabel("WACC")
ax.set_title("Sensibilidade do Equity Value | R$ bilhões")
for i in range(3):
    for j in range(3):
        ax.text(j, i, f"R$ {NAV[i, j]:.2f} bi", ha="center", va="center", fontsize=11, fontweight="bold", color=navy)
fig.colorbar(im, ax=ax, shrink=0.82, label="Equity Value (R$ bi)")
save(fig, "05_sensibilidade_equity_value.png")

# 6. Benchmarking e Porter.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5.2), gridspec_kw={"width_ratios": [1.05, 1]})
companies, capacity = ["CerradinhoBio", "FS Bioenergia", "Green Plains"], [1.2, 2.1, 3.1]
ax1.barh(companies, capacity, color=[gray, green, navy])
ax1.set_xlabel("Capacidade anual (bilhões de litros)")
ax1.set_title("Benchmark de escala")
ax1.set_xlim(0, 3.6)
for i, value in enumerate(capacity):
    ax1.text(value + 0.06, i, f"{value:.1f}", va="center", fontsize=10, fontweight="bold")
forces, scores = ["Novos entrantes", "Fornecedores", "Compradores", "Substitutos", "Rivalidade"], [3, 2, 5, 5, 5]
y = np.arange(len(forces))
ax2.barh(y, scores, color=[orange if s >= 5 else green for s in scores])
ax2.set_yticks(y, forces)
ax2.set_xlim(0, 5.6)
ax2.set_xlabel("Intensidade (1–5)")
ax2.set_title("Cinco forças de Porter")
for i, score in enumerate(scores):
    ax2.text(score + 0.08, i, str(score), va="center", fontweight="bold")
fig.suptitle("FS Bioenergia | Posição competitiva e pressão setorial", fontsize=15, fontweight="bold", y=1.02)
save(fig, "06_benchmark_porter.png")

# 7. Mapa de riscos: probabilidade x impacto, conforme riscos descritos no PDF.
risk_names = ["Volatilidade de commodities", "Regulação / RenovaBio", "Intensidade de CAPEX", "Execução de projetos", "Concentração de compradores", "Logística", "Substituição / eletrificação"]
probability = np.array([4, 3, 3, 3, 4, 3, 2])
impact = np.array([5, 4, 4, 4, 4, 3, 3])
fig, ax = plt.subplots(figsize=(9, 6))
colors = [red if p * i >= 16 else orange if p * i >= 9 else green for p, i in zip(probability, impact)]
ax.scatter(probability, impact, s=150, c=colors, edgecolors="white", linewidth=1.2)
risk_offsets = [(8, 8), (8, -18), (8, 20), (8, -32), (8, 8), (8, -18), (8, 8)]
for name, p, i, offset in zip(risk_names, probability, impact, risk_offsets):
    ax.annotate(name, (p, i), xytext=offset, textcoords="offset points", fontsize=8.5)
ax.set_xlim(1, 5.3); ax.set_ylim(1, 5.3)
ax.set_xticks(range(1, 6)); ax.set_yticks(range(1, 6))
ax.set_xlabel("Probabilidade (1 = baixa; 5 = alta)")
ax.set_ylabel("Impacto financeiro/estratégico (1 = baixo; 5 = alto)")
ax.set_title("Matriz de riscos | FS Bioenergia")
ax.grid(True, alpha=0.25)
save(fig, "07_matriz_riscos.png")

# 8. Tabela financeira completa do Anexo A.
full_df = pd.DataFrame({
    "Ano": years, "Receita (R$ mil)": revenue, "Cresc. receita": ["–" if np.isnan(v) else f"{v:.1f}%" for v in growth],
    "EBIT (R$ mil)": ebit, "Margem EBIT": ["22,4%", "22,0%", "22,0%", "22,0%", "22,0%", "22,0%"],
    "Impostos (R$ mil)": taxes, "NOPAT (R$ mil)": nopat, "D&A (R$ mil)": d_and_a,
    "CAPEX (R$ mil)": capex, "Capital de giro (R$ mil)": working_capital,
    "FCFF (R$ mil)": fcff, "Fator desconto": ["–" if np.isnan(v) else f"{v:.3f}" for v in discount_factor],
    "FCFF descontado (R$ mil)": ["–" if np.isnan(v) else f"{v:,.0f}".replace(",", ".") for v in fcff_discounted],
})
full_df.to_csv(OUT / "projecoes_dcf_completas.csv", index=False, encoding="utf-8-sig")
# Tabela resumida legível para README.
summary = full_df[["Ano", "Receita (R$ mil)", "Cresc. receita", "EBIT (R$ mil)", "Margem EBIT", "FCFF (R$ mil)"]].copy()
fig, ax = plt.subplots(figsize=(12, 2.8)); ax.axis("off")
table = ax.table(cellText=summary.values.tolist(), colLabels=summary.columns, loc="center", cellLoc="center")
table.auto_set_font_size(False); table.set_fontsize(8.5); table.scale(1, 1.65)
for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor("#D9E2EC")
    if row == 0: cell.set_facecolor(navy); cell.set_text_props(color="white", weight="bold")
    elif row % 2 == 0: cell.set_facecolor("#F4F7FA")
ax.set_title("Anexo A | Resumo das projeções do DCF (R$ mil, exceto percentuais)", fontweight="bold", pad=18)
save(fig, "08_tabela_projecoes_dcf.png")

# 9. Tabela de premissas para tornar o modelo auditável.
assumptions = pd.DataFrame([
    ["Período explícito", "FY26–FY30", "Projeção de cinco anos"],
    ["Receita FY25 (base)", "R$ 10,69 bi", "Ponto de partida do modelo"],
    ["Crescimento da receita", "12% → 4%", "FY26, FY27, FY28, FY29 e FY30"],
    ["Margem EBIT", "22,0%", "22,4% no FY25 base"],
    ["Alíquota de impostos", "34%", "Aplicada ao EBIT"],
    ["CAPEX", "8% → 4% da receita", "Trajetória decrescente"],
    ["WACC", "15,0%", "Taxa de desconto"],
    ["Crescimento na perpetuidade", "3,0%", "Taxa terminal"],
    ["Equity Value", "R$ 7,19 bi", "Valor reportado no PDF"],
], columns=["Premissa", "Valor", "Interpretação"])
assumptions.to_csv(OUT / "premissas_valuation.csv", index=False, encoding="utf-8-sig")
fig, ax = plt.subplots(figsize=(11, 4.2)); ax.axis("off")
table = ax.table(cellText=assumptions.values.tolist(), colLabels=assumptions.columns, loc="center", cellLoc="left", colWidths=[0.28, 0.20, 0.52])
table.auto_set_font_size(False); table.set_fontsize(9); table.scale(1, 1.5)
for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor("#D9E2EC")
    if row == 0: cell.set_facecolor(navy); cell.set_text_props(color="white", weight="bold")
    elif row % 2 == 0: cell.set_facecolor("#F4F7FA")
ax.set_title("Premissas centrais do valuation DCF", fontweight="bold", pad=18)
save(fig, "09_tabela_premissas.png")

# CSVs adicionais para reprodutibilidade.
pd.DataFrame(NAV, index=wacc_labels, columns=g_labels).to_csv(OUT / "sensibilidade_equity_value.csv", encoding="utf-8-sig")
pd.DataFrame({"Risco": risk_names, "Probabilidade": probability, "Impacto": impact}).to_csv(OUT / "riscos.csv", index=False, encoding="utf-8-sig")
print(f"Visualizações e dados gerados em: {OUT}")
