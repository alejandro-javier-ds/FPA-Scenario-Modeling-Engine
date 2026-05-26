import pyodbc
from config import get_connection_string

class DatabaseManager:
    def __init__(self):
        self.conn_str = get_connection_string()

    def save_quantitative_scenario(self, scenario_name: str, author: str, 
                                   unit_price: float, volume: int, volume_volatility: float,
                                   fixed_costs: float, variable_cost: float, cost_volatility: float,
                                   simulations_run: int, 
                                   gp_p10: float, gp_p50: float, gp_p90: float,
                                   margin_p10: float, margin_p50: float, margin_p90: float,
                                   risk_probability: float) -> int:
        
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO FinancialScenarios (ScenarioName, Author)
                OUTPUT INSERTED.ScenarioID
                VALUES (?, ?)
            """, (scenario_name, author))
            
            scenario_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO ScenarioParameters 
                (ScenarioID, UnitPrice, Volume, VolumeVolatility, FixedCosts, VariableCostPerUnit, CostVolatility)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (scenario_id, unit_price, volume, volume_volatility, fixed_costs, variable_cost, cost_volatility))
            
            cursor.execute("""
                INSERT INTO QuantitativeMetrics 
                (ScenarioID, SimulationsRun, GrossProfit_P10, GrossProfit_P50, GrossProfit_P90, 
                 Margin_P10, Margin_P50, Margin_P90, RiskOfLossProbability)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (scenario_id, simulations_run, gp_p10, gp_p50, gp_p90, margin_p10, margin_p50, margin_p90, risk_probability))
            
            conn.commit()
            return scenario_id
            
        except Exception as e:
            conn.rollback()
            raise e
            
        finally:
            conn.close()

    def get_all_scenarios(self):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT S.ScenarioID, S.ScenarioName, S.Author, S.CreatedAt, 
                   Q.GrossProfit_P50, Q.RiskOfLossProbability
            FROM FinancialScenarios S
            INNER JOIN QuantitativeMetrics Q ON S.ScenarioID = Q.ScenarioID
            ORDER BY S.CreatedAt DESC
        """)
        
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results