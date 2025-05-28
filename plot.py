import plotly.express as px

def plotar_iterativo(st, df, x, y, color, titulo, use_container_width=True):
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color,
        title=titulo
    )
    st.plotly_chart(fig, use_container_width=use_container_width)