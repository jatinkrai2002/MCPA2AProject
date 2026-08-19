# kpi_name_reference.py
import pandas as pd
from KPIOperationalEventLoader import KPIOperationalEventLoader

class KPINameReference:
    def __init__(self, data_file: str):
        self.loader = KPIOperationalEventLoader(data_file)
        self.df = self.loader.df

    def validate_intent(self, intent: dict):
        """
        Validate KPI Intent JSON against dataset columns and values.
        """
        errors = []

        # Required fields
        required_fields = ["kpi_name", "metric_type", "filters", "aggregation", "time_period"]
        for field in required_fields:
            if field not in intent:
                errors.append(f"Missing required field: {field}")

        # Validate filters
        if "filters" in intent:
            filter_value = intent["filters"]
            valid_event_types = self.df["event_type"].unique().tolist()
            valid_priorities = self.df["priority"].unique().tolist()

            if filter_value == "Only Issues" and "Issue" not in valid_event_types:
                errors.append("Invalid filter value: Issue not found in event_type column")
            elif filter_value == "Only Near Misses" and "Near Miss" not in valid_event_types:
                errors.append("Invalid filter value: Near Miss not found in event_type column")
            elif filter_value == "High Priority" and "High" not in valid_priorities:
                errors.append("Invalid filter value: High not found in priority column")
            elif filter_value not in ["All Events", "Only Issues", "Only Near Misses", "High Priority", "Near Miss vs Issue"]:
                errors.append(f"Unknown filter value: {filter_value}")

        return errors

    def execute_intent(self, intent: dict):
        """
        Execute KPI calculation programmatically based on intent JSON.
        """
        errors = self.validate_intent(intent)
        if errors:
            return {"Error": errors}

        metric_type = intent["metric_type"]
        filters = intent["filters"]
        aggregation = intent["aggregation"]

        df_filtered = self.df.copy()

        # Apply filters
        if filters == "Only Issues":
            df_filtered = df_filtered[df_filtered["event_type"] == "Issue"]
        elif filters == "Only Near Misses":
            df_filtered = df_filtered[df_filtered["event_type"] == "Near Miss"]
        elif filters == "High Priority":
            df_filtered = df_filtered[df_filtered["priority"] == "High"]

        # Perform aggregation
        result = None
        formula = ""
        numerator = None
        denominator = None

        if metric_type == "Count":
            result = len(df_filtered)
            formula = f"Count of rows with filter = {filters}"
        elif metric_type == "Sum":
            if "cost_amount" not in df_filtered.columns:
                return {"Error": ["Missing column: cost_amount"]}
            result = df_filtered["cost_amount"].sum()
            formula = f"Sum(cost_amount) with filter = {filters}"
        elif metric_type == "Average":
            if "processing_hours" not in df_filtered.columns:
                return {"Error": ["Missing column: processing_hours"]}
            result = df_filtered["processing_hours"].mean()
            formula = f"Average(processing_hours) with filter = {filters}"
        elif metric_type == "Ratio":
            # Example: Near Miss to Issue Ratio
            numerator = len(self.df[self.df["event_type"] == "Near Miss"])
            denominator = len(self.df[self.df["event_type"] == "Issue"])
            result = numerator / denominator if denominator > 0 else None
            formula = "Count(Near Miss) / Count(Issue)"

        return {
            "KPIName": intent.get("kpi_name"),
            "MetricType": metric_type,
            "Filters": filters,
            "Aggregation": aggregation,
            "TimePeriod": intent.get("time_period"),
            "ComputedValue": result,
            "Formula": formula,
            "Numerator": numerator,
            "Denominator": denominator
        }


# Example usage
if __name__ == "__main__":
    reference = KPINameReference("C:\jitendra\JatinKRai-interview\DetectAssignment\KPIAgenticAIBuilder\DataLoader\operations_events.csv")

    # Example intent for Near Miss to Issue Ratio
    intent = {
        "kpi_name": "NearMisstoIssueRatio",
        "metric_type": "Ratio",
        "filters": "Near Miss vs Issue",
        "aggregation": "Total",
        "time_period": "Monthly"
    }

    result = reference.execute_intent(intent)
    print(result)
