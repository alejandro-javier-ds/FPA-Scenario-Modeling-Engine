import numpy as np

class PricingOptimizer:
    def optimize(self, target_risk: float, min_price: float, max_price: float,
                 volume: int, volume_volatility: float,
                 fixed_costs: float, variable_cost: float, cost_volatility: float,
                 simulations: int = 10000) -> dict:
        
        prices = np.linspace(min_price, max_price, 100)
        
        volume_std = volume * volume_volatility
        simulated_volumes = np.random.normal(loc=volume, scale=volume_std, size=simulations)
        simulated_volumes = np.maximum(simulated_volumes, 0)
        
        cost_std = variable_cost * cost_volatility
        simulated_variable_costs = np.random.normal(loc=variable_cost, scale=cost_std, size=simulations)
        simulated_variable_costs = np.maximum(simulated_variable_costs, 0)
        
        simulated_total_costs = fixed_costs + (simulated_volumes * simulated_variable_costs)
        
        revenues = simulated_volumes * prices[:, np.newaxis]
        gross_profits = revenues - simulated_total_costs
        
        p50_profits = np.percentile(gross_profits, 50, axis=1)
        loss_cases = np.sum(gross_profits < 0, axis=1)
        risks = (loss_cases / simulations) * 100
        
        valid_indices = np.where(risks <= target_risk)[0]
        
        if len(valid_indices) == 0:
            best_idx = np.argmin(risks)
            status = "NO_FEASIBLE_SOLUTION"
        else:
            best_idx = valid_indices[np.argmax(p50_profits[valid_indices])]
            status = "OPTIMAL_FOUND"
            
        return {
            "Status": status,
            "OptimalPrice": float(prices[best_idx]),
            "ExpectedP50": float(p50_profits[best_idx]),
            "ResultingRisk": float(risks[best_idx]),
            "FrontierPrices": prices.tolist(),
            "FrontierP50": p50_profits.tolist(),
            "FrontierRisks": risks.tolist()
        }