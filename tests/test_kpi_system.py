"""
    Agentic KPI Builder: 
    every function is annotated (@tool, @static, @prompt), orchestrated as nodes, 
    and resilient to errors.
    
    Jatin K Rai -- assignment
"""

import pytest
import pandas as pd
from kpi.kpi_loader import KPIOperationalEventLoader
from kpi.kpi_name_reference import KPINameReference

@pytest.fixture
def sample_loader(tmp_path):
    # Create a temporary CSV file with sample data
    data = pd.DataFrame({
        "event_id": [1,2,3,4],
        "event_date": ["2024-01-01","2024-01-02","2024-01-03","2024-01-04"],
        "business_unit": ["A","A","B","B"],
        "location": ["X","Y","X","Y"],
        "event_type": ["Issue","Near Miss","Issue","Issue"],
        "event_status": ["Open","Closed","Open","Closed"],
        "category": ["Cat1","Cat2","Cat1","Cat2"],
        "priority": ["High","Low","High","Low"],
        "impact_type": ["Minor","Major","Minor","Major"],
        "resolution_status": ["Resolved","Pending","Resolved","Pending"],
        "cost_amount": [100,200,300,400],
        "processing_hours": [5,10,15,20],
        "customer_count": [1,2,3,4]
    })
    csv_file = tmp_path / "operations_events.csv"
    data.to_csv(csv_file, index=False)
    return KPIOperationalEventLoader(csv_file)

def test_issue_count(sample_loader):
    reference = KPINameReference(sample_loader)
    intent = {
        "kpi_name": "IssueCount",
        "metric_type": "Count",
        "filters": "Only Issues",
        "aggregation": "Total",
        "time_period": "Monthly"
    }
    result = reference.execute_intent(intent)
    assert result["ComputedValue"] == 3  # 3 Issue rows
    assert result["Formula"].startswith("Count")

def test_average_processing_hours(sample_loader):
    reference = KPINameReference(sample_loader)
    intent = {
        "kpi_name": "AverageProcessingHours",
        "metric_type": "Average",
        "filters": "All Events",
        "aggregation": "Mean",
        "time_period": "Weekly"
    }
    result = reference.execute_intent(intent)
    expected_mean = sample_loader.df["processing_hours"].mean()
    assert pytest.approx(result["ComputedValue"], 0.01) == expected_mean
    assert "Average" in result["Formula"]

def test_near_miss_to_issue_ratio(sample_loader):
    reference = KPINameReference(sample_loader)
    intent = {
        "kpi_name": "NearMisstoIssueRatio",
        "metric_type": "Ratio",
        "filters": "Near Miss vs Issue",
        "aggregation": "Total",
        "time_period": "Monthly"
    }
    result = reference.execute_intent(intent)
    numerator = len(sample_loader.df[sample_loader.df["event_type"]=="Near Miss"])
    denominator = len(sample_loader.df[sample_loader.df["event_type"]=="Issue"])
    expected_ratio = numerator/denominator
    assert pytest.approx(result["ComputedValue"], 0.01) == expected_ratio
    assert "Count(Near Miss)" in result["Formula"]