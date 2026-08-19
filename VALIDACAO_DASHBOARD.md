# Validação do dashboard

O aplicativo Streamlit foi iniciado localmente em `http://localhost:8501` e carregou corretamente. A interface apresentou os controles laterais de WACC, crescimento perpétuo, faixa da matriz e incremento da grade.

A tela exibiu os KPIs de Equity Value, Enterprise Value, PV dos FCFF explícitos, PV do valor terminal e participação do valor terminal no Enterprise Value. A matriz avançada WACC × crescimento perpétuo foi renderizada como heatmap interativo com valores em R$ bilhões, download CSV e tabela de cenários conservador, base e otimista.

A tabela de projeções financeiras, o gráfico interativo de Receita/EBIT/FCFF e os gráficos PNG existentes também foram carregados. A matriz, no cenário-base do app, produz Equity Value aproximado de R$ 7,15 bilhões pela fórmula recalculada com FCFF e dívida líquida, próximo do R$ 7,19 bilhões arredondado no PDF.
