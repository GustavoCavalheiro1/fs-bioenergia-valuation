from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from valuation_model import (  # noqa: E402
    BASE_G,
    BASE_WACC,
    CHARTS,
    FCFF,
    FORECAST_YEARS,
    NET_DEBT,
    advanced_sensitivity,
    calculate_valuation,
    projections_dataframe,
)

st.set_page_config(page_title="FS Bioenergia | Valuation Dashboard", page_icon=None, layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
[data-testid="stMetricValue"] {font-size: 1.55rem;}
</style>
""", unsafe_allow_html=True)

st.title("FS Bioenergia — Valuation Dashboard")
st.caption("Modelo DCF, sensibilidade avançada e análise operacional com dados do PDF do projeto.")

with st.sidebar:
    st.header("Premissas interativas")
    selected_wacc = st.slider("WACC", min_value=0.08, max_value=0.25, value=BASE_WACC, step=0.005, format="%.1f%%")
    selected_g = st.slider("Crescimento perpétuo (g)", min_value=0.00, max_value=0.08, value=BASE_G, step=0.005, format="%.1f%%")
    st.divider()
    st.subheader("Faixa da matriz")
    min_wacc, max_wacc = st.slider("Faixa de WACC", 0.08, 0.30, (0.10, 0.20), step=0.005, format="%.1f%%")
    min_g, max_g = st.slider("Faixa de crescimento perpétuo", 0.00, 0.10, (0.01, 0.05), step=0.005, format="%.1f%%")
    grid_step = st.selectbox("Incremento da matriz", [0.005, 0.01, 0.02], index=0, format_func=lambda x: f"{x:.1%}")

valuation = calculate_valuation(selected_wacc, selected_g)
base_valuation = calculate_valuation(BASE_WACC, BASE_G)

st.subheader("Resumo do valuation")
metrics = st.columns(5)
metrics[0].metric("Equity Value", f"R$ {valuation['equity_value'] / 1e6:,.2f} bi".replace(",", "X").replace(".", ",").replace("X", "."), f"{valuation['equity_value'] / base_valuation['equity_value'] - 1:+.1%} vs. base")
metrics[1].metric("Enterprise Value", f"R$ {valuation['enterprise_value'] / 1e6:,.2f} bi".replace(",", "X").replace(".", ",").replace("X", "."))
metrics[2].metric("PV FCFF explícito", f"R$ {valuation['pv_explicit'] / 1e6:,.2f} bi".replace(",", "X").replace(".", ",").replace("X", "."))
metrics[3].metric("PV valor terminal", f"R$ {valuation['pv_terminal'] / 1e6:,.2f} bi".replace(",", "X").replace(".", ",").replace("X", "."))
metrics[4].metric("Valor terminal / EV", f"{valuation['pv_terminal'] / valuation['enterprise_value']:.1%}")

st.info(f"Cenário selecionado: WACC de {selected_wacc:.1%} e crescimento perpétuo de {selected_g:.1%}. A matriz utiliza o mesmo FCFF projetado e a dívida líquida implícita do Anexo A.")

st.subheader("Sensibilidade avançada: WACC × crescimento perpétuo")
# numpy é usado localmente para construir a grade paramétrica da análise.
import numpy as np
wacc_grid = np.arange(min_wacc, max_wacc + grid_step / 2, grid_step)
g_grid = np.arange(min_g, max_g + grid_step / 2, grid_step)
sensitivity = advanced_sensitivity(wacc_grid, g_grid)
pivot = sensitivity.pivot(index="WACC", columns="Crescimento perpétuo", values="Equity Value (R$ bi)")

left, right = st.columns([1.55, 1])
with left:
    heatmap = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"{v:.1%}" for v in pivot.columns],
        y=[f"{v:.1%}" for v in pivot.index],
        colorscale=[[0, "#C94C4C"], [0.5, "#FFF4D6"], [1, "#238B66"]],
        colorbar={"title": "R$ bi"},
        hovertemplate="WACC: %{y}<br>g: %{x}<br>Equity Value: R$ %{z:.2f} bi<extra></extra>",
        text=np.round(pivot.values, 2),
        texttemplate="R$ %{text:.2f}",
    ))
    heatmap.update_layout(height=580, margin=dict(l=20, r=20, t=30, b=20), xaxis_title="Crescimento perpétuo (g)", yaxis_title="WACC")
    st.plotly_chart(heatmap, width="stretch")
with right:
    st.markdown("**Cenários de referência**")
    reference = pd.DataFrame([
        ["Conservador", 0.16, 0.025],
        ["Base", BASE_WACC, BASE_G],
        ["Otimista", 0.14, 0.035],
    ], columns=["Cenário", "WACC", "g"])
    reference["Equity Value (R$ bi)"] = [calculate_valuation(row.WACC, row.g)["equity_value"] / 1e6 for row in reference.itertuples()]
    reference_display = reference.copy()
    reference_display["WACC"] = reference_display["WACC"].map(lambda x: f"{x:.1%}")
    reference_display["g"] = reference_display["g"].map(lambda x: f"{x:.1%}")
    reference_display["Equity Value (R$ bi)"] = reference_display["Equity Value (R$ bi)"].map(lambda x: f"R$ {x:.2f}")
    st.dataframe(reference_display, hide_index=True, width="stretch")
    st.download_button("Baixar matriz CSV", sensitivity.to_csv(index=False).encode("utf-8-sig"), "sensibilidade_avancada.csv", "text/csv")
    st.caption("Valores em R$ bilhões. Células inválidas, quando WACC ≤ g, são exibidas como vazias.")

st.subheader("Projeções financeiras")
projection = projections_dataframe()
projection_plot = projection.iloc[1:].melt(id_vars="Ano", value_vars=["Receita (R$ mil)", "EBIT (R$ mil)", "FCFF (R$ mil)"], var_name="Métrica", value_name="Valor")
projection_plot["Valor (R$ bi)"] = projection_plot["Valor"] / 1e6
fig = px.line(projection_plot, x="Ano", y="Valor (R$ bi)", color="Métrica", markers=True, title="Receita, EBIT e FCFF")
fig.update_layout(height=430, legend_title_text="")
st.plotly_chart(fig, width="stretch")
st.dataframe(projection, hide_index=True, width="stretch")

st.subheader("Gráficos do portfólio")
image_names = [
    ("Operação — receita e EBIT", "01_operacao_receita_ebit.png"),
    ("FCFF e estrutura de caixa", "02_fcff_estrutura_caixa.png"),
    ("Reconciliação do valuation", "04_valuation_bridge.png"),
    ("Matriz de riscos", "07_matriz_riscos.png"),
]
cols = st.columns(2)
for idx, (title, filename) in enumerate(image_names):
    with cols[idx % 2]:
        st.markdown(f"**{title}**")
        st.image(str(CHARTS / filename), width="stretch")

st.caption("Fonte: dados e premissas transcritos do PDF de contexto do repositório. Material acadêmico e de portfólio; não constitui recomendação de investimento.")
