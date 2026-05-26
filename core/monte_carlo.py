import numpy as np
from db.database_manager import DatabaseManager

class MonteCarloEngine:
    def __init__(self):
        self.db = DatabaseManager()

    def run_simulation(self, scenario_name: str, author: str,
                       unit_price: float, volume: int, volume_volatility: float,
                       fixed_costs: float, variable_cost: float, cost_volatility: float,
                       simulations: int = 10000) -> dict:
        
        volume_std = volume * volume_volatility
        simulated_volumes = np.random.normal(loc=volume, scale=volume_std, size=simulations)
        simulated_volumes = np.maximum(simulated_volumes, 0)
        
        cost_std = variable_cost * cost_volatility
        simulated_variable_costs = np.random.normal(loc=variable_cost, scale=cost_std, size=simulations)
        simulated_variable_costs = np.maximum(simulated_variable_costs, 0)
        
        simulated_revenues = simulated_volumes * unit_price
        simulated_total_costs = fixed_costs + (simulated_volumes * simulated_variable_costs)
        simulated_gross_profits = simulated_revenues - simulated_total_costs
        
        valid_revenues = np.where(simulated_revenues > 0, simulated_revenues, 1)
        simulated_margins = (simulated_gross_profits / valid_revenues) * 100
        simulated_margins = np.where(simulated_revenues > 0, simulated_margins, 0)
        
        gp_p10 = np.percentile(simulated_gross_profits, 10)
        gp_p50 = np.percentile(simulated_gross_profits, 50)
        gp_p90 = np.percentile(simulated_gross_profits, 90)
        
        margin_p10 = np.percentile(simulated_margins, 10)
        margin_p50 = np.percentile(simulated_margins, 50)
        margin_p90 = np.percentile(simulated_margins, 90)
        
        loss_cases = np.sum(simulated_gross_profits < 0)
        risk_probability = (loss_cases / simulations) * 100
        
        scenario_id = self.db.save_quantitative_scenario(
            scenario_name=scenario_name,
            author=author,
            unit_price=unit_price,
            volume=volume,
            volume_volatility=volume_volatility,
            fixed_costs=fixed_costs,
            variable_cost=variable_cost,
            cost_volatility=cost_volatility,
            simulations_run=simulations,
            gp_p10=float(gp_p10),
            gp_p50=float(gp_p50),
            gp_p90=float(gp_p90),
            margin_p10=float(margin_p10),
            margin_p50=float(margin_p50),
            margin_p90=float(margin_p90),
            risk_probability=float(risk_probability)
        )
        
        return {
            "ScenarioID": scenario_id,
            "Simulations": simulations,
            "GP_P10": gp_p10,
            "GP_P50": gp_p50,
            "GP_P90": gp_p90,
            "Margin_P10": margin_p10,
            "Margin_P50": margin_p50,
            "Margin_P90": margin_p90,
            "RiskProbability": risk_probability,
            "RawGrossProfits": simulated_gross_profits.tolist()
        }

    def load_history(self):
        return self.db.get_all_scenarios()