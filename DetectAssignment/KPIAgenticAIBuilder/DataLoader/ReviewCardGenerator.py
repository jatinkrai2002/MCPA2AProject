# review_card_generator.py
import streamlit as st
from KPIOperationalEventLoader import KPIOperationalEventLoader
from kpiinputhandler import KPIInputHandler
from KPIAgentHandler import KPIAgentHandler
from KPINameReference import KPINameReference

class ReviewCardGenerator:
    def __init__(self, data_file: str):
        self.loader = KPIOperationalEventLoader(data_file)
        self.handler = KPIInputHandler(self.loader)
        self.agent = KPIAgentHandler(data_file)
        self.reference = KPINameReference(data_file)
        self.conversation_state = {}

    def compute_status_badge(self, kpi_name: str, value):
        """
        Simple threshold rules for status badge.
        """
        if value is None:
            return "Critical"
        if "Ratio" in kpi_name:
            if value < 0.5:
                return "Good"
            elif value < 1.0:
                return "Warning"
            else:
                return "Critical"
        elif "Count" in kpi_name:
            if value == 0:
                return "Good"
            elif value < 5:
                return "Warning"
            else:
                return "Critical"
        elif "Average" in kpi_name or "Avg" in kpi_name:
            if value < 10:
                return "Good"
            elif value < 20:
                return "Warning"
            else:
                return "Critical"
        else:
            return "Warning"

    def run_review_card(self):
        st.title("KPI Review Card Generator")

        # Step 1: User enters KPI name
        kpi_name = st.text_input("Enter KPI Name:")
        if kpi_name and st.button("Compute KPI"):
            # Step 2: Build KPI Intent (from agent flow or defaults)
            # For simplicity, we assume the agent has already built an intent.
            # Here we mock a basic intent for demonstration.
            intent = {
                "kpi_name": kpi_name,
                "metric_type": "Ratio" if "Ratio" in kpi_name else "Count",
                "filters": "All Events",
                "aggregation": "Total",
                "time_period": "Monthly"
            }

            # Step 3: Validate and compute KPI using KPINameReference
            result = self.reference.execute_intent(intent)

            if "Error" in result:
                st.error(f"KPI validation failed: {result['Error']}")
                return

            # Step 4: Build Review Card
            st.subheader("KPI Review Card")

            description = f"KPI '{kpi_name}' measures operational performance."
            computed_value = result.get("ComputedValue", None)
            formula = result.get("Formula", "Formula not defined")
            unit = "events" if result["MetricType"] == "Count" else "hours" if result["MetricType"] == "Average" else "ratio"

            # Status badge
            badge = self.compute_status_badge(kpi_name, computed_value)

            # Display card
            st.write(f"**KPI Name:** {kpi_name}")
            st.write(f"**Description:** {description}")
            st.write(f"**Formula:** {formula}")
            st.write(f"**Computed Value:** {computed_value}")
            st.write(f"**Unit:** {unit}")
            st.write(f"**Status:** {badge}")

            # Show numerator/denominator for ratio KPIs
            if result["MetricType"] == "Ratio":
                st.write(f"**Numerator (Near Miss):** {result['Numerator']}")
                st.write(f"**Denominator (Issue):** {result['Denominator']}")

            # Action buttons
            col1, col2, col3 = st.columns(3)
            approve_btn = col1.button("Approve", disabled=(computed_value is None))
            edit_btn = col2.button("Edit")
            regen_btn = col3.button("Regenerate")

            if approve_btn:
                st.success("KPI Approved and validated.")
            if edit_btn:
                st.info("Returning to KPI definition flow...")
                self.agent.run_flow()
            if regen_btn:
                st.warning("Restarting KPI entry...")
                st.experimental_rerun()


# Example usage with Streamlit
if __name__ == "__main__":
    review = ReviewCardGenerator("C:\jitendra\JatinKRai-interview\DetectAssignment\KPIAgenticAIBuilder\DataLoader\operations_events.csv")
    review.run_review_card()
