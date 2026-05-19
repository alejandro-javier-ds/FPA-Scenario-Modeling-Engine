import streamlit as st
import plotly.graph_objects as go
import logging
from core.finance_math import FinancialSimulator

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

st.set_page_config(page_title="Financial Scenario Simulator", layout="wide")

def render_waterfall_chart(metrics: dict) -> go.Figure:
    logging.info("RENDER: Generating optimized waterfall chart")
    
    y_max_range = metrics['revenue'] * 1.20

    fig = go.Figure(go.Waterfall(
        name="P&L",
        orientation="v",
        measure=["relative", "relative", "total"],
        x=["Gross Revenue", "Total Costs", "Net Profit"],
        textposition="outside",
        text=[f"${metrics['revenue']:,.0f}", f"-${metrics['total_costs']:,.0f}", f"${metrics['gross_profit']:,.0f}"],
        y=[metrics['revenue'], -metrics['total_costs'], metrics['gross_profit']],
        connector={"line": {"color": "rgb(63, 63, 63)", "width": 2}},
        decreasing={"marker": {"color": "#FF4B4B"}},
        increasing={"marker": {"color": "#00CC96"}},
        totals={"marker": {"color": "#636EFA"}},
        textfont=dict(size=14, color="white")
    ))
    
    fig.update_layout(
        title="Projected P&L Statement (Dynamic)",
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=80, b=40, l=40, r=40),
        yaxis=dict(
            range=[0, y_max_range],
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        )
    )
    
    fig.update_traces(cliponaxis=False)
    
    return fig

def main():
    logging.info("UI: Initializing dashboard components")
    st.title("📈 Financial Scenario Simulator")
    st.markdown("---")

    st.sidebar.header("Scenario Parameters")
    
    unit_price = st.sidebar.slider("Unit Price ($)", min_value=10.0, max_value=500.0, value=120.0, step=5.0)
    volume = st.sidebar.slider("Sales Volume (Units)", min_value=100, max_value=10000, value=1500, step=100)
    fixed_costs = st.sidebar.slider("Fixed Costs ($)", min_value=1000.0, max_value=50000.0, value=25000.0, step=1000.0)
    variable_cost = st.sidebar.slider("Variable Cost per Unit ($)", min_value=5.0, max_value=250.0, value=45.0, step=5.0)

    simulator = FinancialSimulator(
        unit_price=unit_price,
        volume=volume,
        fixed_costs=fixed_costs,
        variable_cost_per_unit=variable_cost
    )
    
    metrics = simulator.get_metrics_report()

    col1, col2, col3 = st.columns(3)
    col1.metric("Projected Revenue", f"${metrics['revenue']:,.2f}")
    col2.metric("Total Costs", f"${metrics['total_costs']:,.2f}")
    
    profit_color = "normal" if metrics['gross_profit'] >= 0 else "inverse"
    col3.metric(
        "Net Profit", 
        f"${metrics['gross_profit']:,.2f}", 
        f"{metrics['margin_percentage']:.1f}% Margin", 
        delta_color=profit_color
    )

    st.plotly_chart(render_waterfall_chart(metrics), use_container_width=True)
    logging.info("UI: Dashboard render sequence completed")

if __name__ == "__main__":
    main()