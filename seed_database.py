import uuid
import random
from datetime import datetime, timedelta
from core.monte_carlo import MonteCarloEngine

def generate_realistic_seed_data(total_scenarios: int = 100000):
    engine = MonteCarloEngine()
    
    regions = ["LATAM", "NA", "EU", "APAC", "GLOBAL"]
    strategies = ["Aggressive_Growth", "Conservative_Defense", "Market_Penetration", "Premium_Pricing", "StressTest"]
    authors = ["Finance_Lead", "Risk_Director", "Quant_Analyst", "CFO_Office", "Strategic_Planner"]
    
    base_date = datetime.now() - timedelta(days=365)
    
    print(f"Starting seed process for {total_scenarios} scenarios...")
    
    for i in range(total_scenarios):
        region = random.choice(regions)
        strategy = random.choice(strategies)
        author = random.choice(authors)
        
        unique_hash = str(uuid.uuid4())[:6]
        scenario_name = f"Q{random.randint(1,4)}_{region}_{strategy}_{unique_hash}"
        
        unit_price = round(random.uniform(90.0, 350.0), 2)
        volume = random.randint(3000, 25000)
        volume_volatility = round(random.uniform(0.08, 0.35), 4)
        fixed_costs = round(random.uniform(200000.0, 900000.0), 2)
        variable_cost = round(random.uniform(40.0, 110.0), 2)
        cost_volatility = round(random.uniform(0.03, 0.15), 4)
        
        if variable_cost >= unit_price:
            unit_price = variable_cost + round(random.uniform(10.0, 50.0), 2)
            
        if "StressTest" in scenario_name:
            volume_volatility = round(random.uniform(0.30, 0.50), 4)
            fixed_costs = round(random.uniform(800000.0, 1200000.0), 2)
            volume = random.randint(1000, 5000)
            
        try:
            engine.run_simulation(
                scenario_name=scenario_name,
                author=author,
                unit_price=unit_price,
                volume=volume,
                volume_volatility=volume_volatility,
                fixed_costs=fixed_costs,
                variable_cost=variable_cost,
                cost_volatility=cost_volatility,
                simulations=10000
            )
            
            if (i + 1) % 100 == 0 or (i + 1) == total_scenarios:
                print(f"Progress: {i + 1}/{total_scenarios} scenarios persisted.")
                
        except Exception as e:
            print(f"Error persisting scenario index {i}: {str(e)}")
            continue

if __name__ == "__main__":
    generate_realistic_seed_data(100000)