import streamlit as st
import plotly.express as px

import data
import plot


st.set_page_config(layout="wide")

@st.cache_data
def carregar_dados():
    return data.ler_dados_fc()


dados_fc = carregar_dados()

st.write("# Análise do fator de capacidade das usinas eólicas e solares do Brasil")

st.write("""O **fator de capacidade** de uma usina, seja eólica ou solar, é uma medida que expressa a relação entre a quantidade real de energia elétrica gerada por essa usina em um determinado período de tempo e a quantidade máxima de energia que ela poderia gerar se operasse continuamente em sua potência nominal durante todo esse período.

A análise da capacidade prática (fator de capacidade real) é fundamental para o planejamento, operação e decisões de investimento no setor elétrico brasileiro. Sendo assim, o objetivo deste trabalho é ajudar no entendimento da capacidade real utilizada pela pelas usinas solares e eólicas, e **embasar empiricamente o planjemanento de expansão da rede, a avaliação econônima, a integação do sisteam e políticas públicas de regulação**, em parceria com um Engenheiro elétrico da ONS.

Os dados são provenientes de dados abertos ONS: https://dados.ons.org.br/dataset/fator-capacidade-2/resource/775048d0-463c-4bdf-9373-4a371cb24a1c
""")

st.write("## Pré-visualização dos dados")

st.dataframe(dados_fc.head(100), hide_index=True)

st.write("## Média mensal do fator de capacidade")
dados_mensais_fc = data.extrair_media_mensal_fc(dados_fc)

st.dataframe(dados_mensais_fc, hide_index=True)

meses_unicos = dados_mensais_fc["Mês"].unique()
estados_unicos = dados_mensais_fc.UF.unique()
anos_unicos = dados_mensais_fc["Ano"].unique()

col_uf, col_ano, col_mes = st.columns(3)

uf_selecionada = col_uf.selectbox('UF', estados_unicos)
ano_selecionado = col_ano.selectbox('Ano', anos_unicos)
mes_selecionado = col_mes.selectbox('Mês', meses_unicos)

if all((uf_selecionada, ano_selecionado, mes_selecionado)):
    df_plot = dados_fc.query(
        "id_estado == @uf_selecionada and ano == @ano_selecionado and mes == @mes_selecionado").copy().reset_index()
    if not len(df_plot):
        st.warning(f"Não há dados do {uf_selecionada} para {mes_selecionado}/{ano_selecionado}")
    else:
        st.write(f"FC do {uf_selecionada} em {mes_selecionado}/{ano_selecionado}")

        df_plot = df_plot.groupby(['hora', 'hora_formatada', 'nom_tipousina'])[
            "val_fatorcapacidade"].mean().reset_index()

        df_plot = df_plot.sort_values(['hora', 'nom_tipousina'])

        df_plot = df_plot.rename(
            columns={"hora_formatada": "Hora", "val_fatorcapacidade": "Fator de capacidade médio",
                     "nom_tipousina": "Tipo"})

        plot.plotar_iterativo(st, df_plot, x="Hora", y="Fator de capacidade médio", color="Tipo",titulo=f"Mensal {uf_selecionada} {ano_selecionado}")


st.write("## Média quadrimestral do fator de capacidade")

dados_quadrimestrais = data.extrair_media_quadrimestral_fc(dados_fc)
st.dataframe(dados_quadrimestrais, hide_index=True)

quadrimestres = dados_quadrimestrais.Quadri.unique()

col_uf, col_ano, col_mes = st.columns(3)

uf_selecionada = col_uf.selectbox('UF', estados_unicos, key="UF Quadrimestral")
ano_selecionado = col_ano.selectbox('Ano', anos_unicos, key="Ano Quadrimestral")
quadrimestre_selecionado = col_mes.selectbox('Quadrimestre', quadrimestres, key="Quadrimestre")

if all((uf_selecionada, ano_selecionado, quadrimestre_selecionado)):
    df_plot = dados_fc.copy()
    df_plot["Quadri"] = df_plot.mes_num.map(lambda mes: f"Quadrimestre {data.get_quadrimestre(mes)}")

    df_plot = dados_fc.query(
        "id_estado == @uf_selecionada and ano == @ano_selecionado and Quadri == @quadrimestre_selecionado").copy().reset_index()

    if not len(df_plot):
        st.warning(f"Não há dados do {uf_selecionada} para o quadrimestre {quadrimestre_selecionado}/{ano_selecionado}")
    else:
        st.write(f"FC do {uf_selecionada} no Quadrimestre {quadrimestre_selecionado}/{ano_selecionado}")

        df_plot = df_plot.groupby(['hora', 'hora_formatada', 'nom_tipousina', 'Quadri', 'ano'])[
            "val_fatorcapacidade"].mean().reset_index()

        df_plot = df_plot.sort_values(['hora', 'nom_tipousina'])

        df_plot = df_plot.rename(
            columns={"hora_formatada": "Hora", "val_fatorcapacidade": "Fator de capacidade médio",
                     "nom_tipousina": "Tipo"})

        plot.plotar_iterativo(st, df_plot, x="Hora", y="Fator de capacidade médio", color="Tipo",titulo=f"Quadrimestral {uf_selecionada} {ano_selecionado}")