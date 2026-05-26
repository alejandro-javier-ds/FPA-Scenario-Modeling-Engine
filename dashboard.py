import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from core.ml_engine import MarketPredictor
from core.monte_carlo import MonteCarloEngine
from core.optimizer import PricingOptimizer

st.set_page_config(page_title="Financial Risk Dashboard", layout="wide")

@st.cache_resource
def load_ml_model():
    return MarketPredictor()

@st.cache_resource
def load_mc_engine():
    return MonteCarloEngine()

@st.cache_resource
def load_optimizer():
    return PricingOptimizer()

ml_predictor = load_ml_model()
mc_engine = load_mc_engine()
pricing_optimizer = load_optimizer()

st.sidebar.header("Scenario Metadata")
scenario_name = st.sidebar.text_input("Scenario Name", "Q4_LATAM_Base_001")
author = st.sidebar.text_input("Author", "Finance_Team")

st.sidebar.header("Macroeconomic Market Conditions (ML Inputs)")
inflation = st.sidebar.slider("Inflation Rate (%)", 1.0, 15.0, 5.0)
marketing = st.sidebar.number_input("Marketing Budget ($)", min_value=0.0, value=50000.0)
comp_price = st.sidebar.number_input("Competitor Price ($)", min_value=0.0, value=140.0)

ml_predictions = ml_predictor.predict_conditions(inflation, marketing, comp_price)
ai_volume = ml_predictions["PredictedVolume"]
ai_volatility = ml_predictions["PredictedVolatility"]

st.sidebar.markdown("### AI Predicted Baseline")
st.sidebar.metric("Predicted Core Volume", f"{ai_volume:,} units")
st.sidebar.metric("Predicted Market Volatility", f"{ai_volatility*100:.2f}%")

st.sidebar.header("Internal Deterministic Parameters")
unit_price = st.sidebar.number_input("Unit Price ($) [Sim Only]", min_value=0.01, value=150.00)
fixed_costs = st.sidebar.number_input("Fixed Costs ($)", min_value=0.0, value=500000.00)
variable_cost = st.sidebar.number_input("Baseline Variable Cost ($)", min_value=0.0, value=65.00)
cost_volatility = st.sidebar.slider("Variable Cost Volatility (%)", 0.0, 50.0, 5.0) / 100.0

st.title("Financial Risk & Stochastic Simulation Dashboard")

tab_sim, tab_opt, tab_portfolio, tab_audit = st.tabs([
    "Predictive Simulation", 
    "Prescriptive Optimization", 
    "Portfolio Analysis", 
    "Data Audit"
])

with tab_sim:
    st.info("Simulation engine is currently being driven by Machine Learning volume predictions.")
    if st.button("Run Monte Carlo Simulation"):
        try:
            with st.spinner("Executing stochastic vectors..."):
                results = mc_engine.run_simulation(
                    scenario_name=scenario_name,
                    author=author,
                    unit_price=unit_price,
                    volume=ai_volume,
                    volume_volatility=ai_volatility,
                    fixed_costs=fixed_costs,
                    variable_cost=variable_cost,
                    cost_volatility=cost_volatility
                )
            
            st.success("Simulation persisted successfully.")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("P10 Gross Profit", f"${results['GP_P10']:,.2f}")
            col2.metric("P50 Gross Profit", f"${results['GP_P50']:,.2f}")
            col3.metric("P90 Gross Profit", f"${results['GP_P90']:,.2f}")
            col4.metric("Risk of Loss", f"{results['RiskProbability']:.2f}%")
            
            raw_data = [results["RawGrossProfits"]]
            group_labels = ['Simulated Gross Profit']
            
            fig_dist = ff.create_distplot(raw_data, group_labels, bin_size=10000, show_rug=False)
            fig_dist.add_vline(x=0, line_dash="dash", line_color="red")
            fig_dist.add_vline(x=results['GP_P50'], line_dash="dash", line_color="green")
            fig_dist.update_layout(title_text="Probability Density Function")
            
            st.plotly_chart(fig_dist, use_container_width=True)
            
        except Exception as e:
            st.error(f"Execution failed: {str(e)}")

with tab_opt:
    st.markdown("### Autonomous Pricing Optimizer")
    col_opt1, col_opt2, col_opt3 = st.columns(3)
    target_risk = col_opt1.number_input("Max Acceptable Risk (%)", min_value=0.1, max_value=99.9, value=15.0)
    min_price = col_opt2.number_input("Minimum Price Boundary ($)", min_value=1.0, value=100.0)
    max_price = col_opt3.number_input("Maximum Price Boundary ($)", min_value=1.0, value=300.0)
    
    if st.button("Run Prescriptive Optimization"):
        try:
            with st.spinner("Calculating stochastic frontier..."):
                opt_results = pricing_optimizer.optimize(
                    target_risk=target_risk,
                    min_price=min_price,
                    max_price=max_price,
                    volume=ai_volume,
                    volume_volatility=ai_volatility,
                    fixed_costs=fixed_costs,
                    variable_cost=variable_cost,
                    cost_volatility=cost_volatility
                )
            
            if opt_results["Status"] == "OPTIMAL_FOUND":
                st.success("Optimization Converged Successfully.")
                m1, m2, m3 = st.columns(3)
                m1.metric("Optimal Unit Price", f"${opt_results['OptimalPrice']:,.2f}")
                m2.metric("Expected Gross Profit", f"${opt_results['ExpectedP50']:,.2f}")
                m3.metric("Resulting Risk", f"{opt_results['ResultingRisk']:.2f}%")
            else:
                st.error("No feasible price found within acceptable risk limits.")
                st.metric("Lowest Possible Risk", f"{opt_results['ResultingRisk']:.2f}%")
                
            fig_opt = go.Figure()
            fig_opt.add_trace(go.Scatter(
                x=opt_results["FrontierPrices"], 
                y=opt_results["FrontierP50"],
                mode='lines',
                name='Expected Profit',
                line=dict(color='blue')
            ))
            
            fig_opt.add_trace(go.Scatter(
                x=opt_results["FrontierPrices"], 
                y=opt_results["FrontierRisks"],
                mode='lines',
                name='Risk (%)',
                yaxis='y2',
                line=dict(color='red')
            ))
            
            fig_opt.add_vline(x=opt_results["OptimalPrice"], line_dash="dash", line_color="green")
            
            fig_opt.update_layout(
                title="Optimization Frontier: Price vs Profit vs Risk",
                xaxis=dict(title="Unit Price Tested ($)"),
                yaxis=dict(
                    title=dict(text="Expected Profit ($)", font=dict(color="blue")), 
                    tickfont=dict(color="blue")
                ),
                yaxis2=dict(
                    title=dict(text="Risk of Loss (%)", font=dict(color="red")), 
                    tickfont=dict(color="red"), 
                    overlaying='y', 
                    side='right'
                )
            )
            
            st.plotly_chart(fig_opt, use_container_width=True)
            
        except Exception as e:
            st.error(f"Optimization failed: {str(e)}")

with tab_portfolio:
    try:
        history = mc_engine.load_history()
        if history:
            df = pd.DataFrame(history)
            
            def extract_region(name):
                parts = name.split('_')
                if len(parts) > 1:
                    return parts[1]
                return "GLOBAL"
            
            df['Region'] = df['ScenarioName'].apply(extract_region)
            
            regions = df['Region'].unique().tolist()
            selected_regions = st.multiselect("Filter by Region", regions, default=regions)
            
            filtered_df = df[df['Region'].isin(selected_regions)]
            
            if not filtered_df.empty:
                fig_scatter = px.scatter(
                    filtered_df,
                    x="RiskOfLossProbability",
                    y="GrossProfit_P50",
                    color="Region",
                    hover_name="ScenarioName",
                    hover_data=["Author", "CreatedAt"],
                    labels={
                        "RiskOfLossProbability": "Risk of Loss (%)",
                        "GrossProfit_P50": "Expected Gross Profit (P50)"
                    },
                    title="Risk vs Reward Matrix"
                )
                
                fig_scatter.add_hline(y=0, line_dash="solid", line_color="red")
                fig_scatter.add_vline(x=20, line_dash="dash", line_color="orange")
                
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("No data for selected regions.")
        else:
            st.info("No historical data available.")
    except Exception as e:
        st.error(f"Failed to load portfolio: {str(e)}")

with tab_audit:
    try:
        if history:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Database is empty.")
    except Exception as e:
        st.error(f"Failed to load audit data: {str(e)}")