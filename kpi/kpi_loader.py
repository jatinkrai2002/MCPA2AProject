"""
    Agentic KPI Builder: 
    every function is annotated (@tool, @static, @prompt), orchestrated as nodes, 
    and resilient to errors.
    
    Jatin K Rai -- assignment
"""

import pandas as pd

class KPIOperationalEventLoader:
    """
    Loads and validates the operations_events.csv dataset.
    Provides dynamic access to KPI methods defined here.
    """

    def __init__(self, csv_file: str):
        self.df = pd.read_csv(csv_file)
        self.validate_data()

   
    def validate_data(self):
        """Basic validation to ensure required columns exist and data types are consistent."""
        required_columns = [
            "event_id","event_date","business_unit","location","event_type",
            "event_status","category","priority","impact_type","resolution_status",
            "cost_amount","processing_hours","customer_count"
        ]
        for col in required_columns:
            if col not in self.df.columns:
                raise ValueError(f"Missing required column: {col}")

        # Convert numeric fields to proper types
        self.df["cost_amount"] = pd.to_numeric(self.df["cost_amount"], errors="coerce").fillna(0)
        self.df["processing_hours"] = pd.to_numeric(self.df["processing_hours"], errors="coerce").fillna(0)
        self.df["customer_count"] = pd.to_numeric(self.df["customer_count"], errors="coerce").fillna(0)

    # --- KPI Methods ---
    def IssueCount(self):
        return len(self.df[self.df["event_type"] == "Issue"])

    def NearMissCount(self):
        return len(self.df[self.df["event_type"] == "Near Miss"])

    def OpenIssueCount(self):
        return len(self.df[(self.df["event_type"] == "Issue") & (self.df["event_status"] == "Open")])

    def HighPriorityIssueCount(self):
        return len(self.df[(self.df["event_type"] == "Issue") & (self.df["priority"] == "High")])

    def NearMisstoIssueRatio(self):
        issue_count = self.IssueCount()
        near_miss_count = self.NearMissCount()
        return (near_miss_count / issue_count) if issue_count > 0 else None

    def AverageProcessingHours(self):
        issues = self.df[self.df["event_type"] == "Issue"]
        return issues["processing_hours"].mean() if not issues.empty else None

    def TotalCostImpact(self):
        issues = self.df[self.df["event_type"] == "Issue"]
        return issues["cost_amount"].sum()

    def ResolutionRate(self):
        issues = self.df[self.df["event_type"] == "Issue"]
        if issues.empty:
            return None
        resolved_count = len(issues[issues["resolution_status"] == "Resolved"])
        return resolved_count / len(issues)

    def CriticalIssueCount(self):
        return len(self.df[(self.df["event_type"] == "Issue") & (self.df["priority"] == "Critical")])

    def AvgCustomerImpact(self):
        issues = self.df[(self.df["event_type"] == "Issue") & (self.df["impact_type"] == "Customer")]
        return issues["customer_count"].mean() if not issues.empty else None