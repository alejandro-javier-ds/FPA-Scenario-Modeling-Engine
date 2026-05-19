import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

class FinancialSimulator:
    """
    Core mathematical engine for financial scenario simulations.
    Handles projections for revenue, costs, and profit margins.
    """
    def __init__(self, unit_price: float, volume: int, fixed_costs: float, variable_cost_per_unit: float):
        self.unit_price = unit_price
        self.volume = volume
        self.fixed_costs = fixed_costs
        self.variable_cost_per_unit = variable_cost_per_unit
        logging.info(f"INIT: FinancialSimulator instantiated | Vol={self.volume} | Price=${self.unit_price:,.2f}")

    def calculate_revenue(self) -> float:
        """Calculates total projected gross revenue."""
        return self.unit_price * self.volume

    def calculate_total_variable_costs(self) -> float:
        """Calculates total variable costs based on volume."""
        return self.variable_cost_per_unit * self.volume

    def calculate_total_costs(self) -> float:
        """Aggregates fixed and variable costs."""
        return self.fixed_costs + self.calculate_total_variable_costs()

    def calculate_gross_profit(self) -> float:
        """Calculates net profit (Revenue - Total Costs)."""
        return self.calculate_revenue() - self.calculate_total_costs()

    def calculate_margin_percentage(self) -> float:
        """Calculates the profit margin percentage."""
        revenue = self.calculate_revenue()
        if revenue == 0:
            return 0.0
        return (self.calculate_gross_profit() / revenue) * 100

    def get_metrics_report(self) -> dict:
        """
        Compiles all financial metrics into a standardized dictionary
        for downstream ingestion by the UI/Dashboard layer.
        """
        logging.info("PROCESS: Executing financial metrics compilation")
        return {
            "revenue": self.calculate_revenue(),
            "total_costs": self.calculate_total_costs(),
            "gross_profit": self.calculate_gross_profit(),
            "margin_percentage": self.calculate_margin_percentage()
        }