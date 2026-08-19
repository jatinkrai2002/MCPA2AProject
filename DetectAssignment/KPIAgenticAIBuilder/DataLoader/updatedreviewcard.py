# kpi_agent_handler.py

import streamlit as st
from KPINameReference import KPINameReference

class KPIAgentHandler:
    def __init__(self, data_file: str):
        self.reference = KPINameReference(data_file)
        self.conversation_state = {
            "step": 0,
            "intent": {}
        }

    def ask_dynamic_questions(self, kpi_name: str):
        """
        Generate contextual questions based on KPI name.
        """
        st.subheader("Step 2: Define KPI Context")

        if "Ratio" in kpi_name:
            metric_type = st.radio("Metric type?", ["Ratio"])
            filters = st.radio("Filters?", ["Near Miss vs Issue"])
            aggregation = st.radio("Aggregation?", ["Total"])
        elif "Count" in kpi_name:
            metric_type = st.radio("Metric type?", ["Count"])
            filters = st.radio("Filters?", ["All Events", "Only Issues", "Only Near Misses", "High Priority"])
            aggregation = st.radio("Aggregation?", ["Total"])
        elif "Average" in kpi_name or "Hours" in kpi_name:
            metric_type = st.radio("Metric type?", ["Average"])
            filters = st.radio("Filters?", ["Only Issues"])
            aggregation = st.radio("Aggregation?", ["Mean"])
        elif "Sum" in kpi_name or "Cost" in kpi_name:
            metric_type = st.radio("Metric type?", ["Sum"])
            filters = st.radio("Filters?", ["Only Issues"])
            aggregation = st.radio("Aggregation?", ["Total"])
        else:
            metric_type = st.radio("Metric type?", ["Count", "Sum", "Average", "Ratio"])
            filters = st.radio("Filters?", ["All Events", "Only Issues", "Only Near Misses", "High Priority"])
            aggregation = st.radio("Aggregation?", ["Total", "Mean"])

        time_period = st.radio("Time period?", ["Daily", "Weekly", "Monthly", "Yearly"])

        if st.button("Submit Definition"):
            self.conversation_state["intent"] = {
                "kpi_name": kpi_name,
                "metric_type": metric_type,
                "filters": filters,
                "aggregation": aggregation,
                "time_period": time_period
            }
            self.conversation_state["step"] = 2

    def run_flow(self):
        st.title("Agentic KPI Handler")

        # Step 1: KPI name entry
        if self.conversation_state["step"] == 0:
            kpi_name = st.text_input("Enter KPI Name:")
            if kpi_name:
                st.write(f"Agent: You want to compute KPI '{kpi_name}'. Let's refine its definition.")
                self.conversation_state["intent"]["kpi_name"] = kpi_name
                self.conversation_state["step"] = 1

        # Step 2: Dynamic questions
        if self.conversation_state["step"] == 1:
            self.ask_dynamic_questions(self.conversation_state["intent"]["kpi_name"])

        # Step 3: Compute KPI
        if self.conversation_state["step"] == 2:
            result = self.reference.execute_intent(self.conversation_state["intent"])
            return result


# review_card_generator.py
import streamlit as st
from KPIAgentHandler import KPIAgentHandler

class ReviewCardGenerator:
    def __init__(self, data_file: str):
        self.agent = KPIAgentHandler(data_file)

    def compute_status_badge(self, kpi_name: str, value):
        if value is None:
            return "Critical"
        if "Ratio" in kpi_name:
            return "Good" if value < 0.5 else "Warning" if value < 1.0 else "Critical"
        elif "Count" in kpi_name:
            return "Good" if value == 0 else "Warning" if value < 5 else "Critical"
        elif "Average" in kpi_name or "Hours" in kpi_name:
            return "Good" if value < 10 else "Warning" if value < 20 else "Critical"
        else:
            return "Warning"

    def run_review_card(self):
        st.title("KPI Review Card")

        result = self.agent.run_flow()
        if result and "Error" not in result:
            kpi_name = result["KPIName"]
            computed_value = result["ComputedValue"]
            formula = result["Formula"]
            unit = "events" if result["MetricType"] == "Count" else "hours" if result["MetricType"] == "Average" else "ratio"
            badge = self.compute_status_badge(kpi_name, computed_value)

            st.subheader("KPI Review Card")
            st.write(f"**KPI Name:** {kpi_name}")
            st.write(f"**Description:** KPI '{kpi_name}' measures operational performance.")
            st.write(f"**Formula:** {formula}")
            st.write(f"**Computed Value:** {computed_value}")
            st.write(f"**Unit:** {unit}")
            st.write(f"**Status:** {badge}")

            if result["MetricType"] == "Ratio":
                st.write(f"**Numerator:** {result['Numerator']}")
                st.write(f"**Denominator:** {result['Denominator']}")

            col1, col2, col3 = st.columns(3)
            approve_btn = col1.button("Approve", disabled=(computed_value is None))
            edit_btn = col2.button("Edit")
            regen_btn = col3.button("Regenerate")

            if approve_btn:
                st.success("KPI Approved and validated.")
            if edit_btn:
                st.info("Returning to KPI definition flow...")
                self.agent.conversation_state["step"] = 1
            if regen_btn:
                st.warning("Restarting KPI entry...")
                self.agent.conversation_state = {"step": 0, "intent": {}}
                st.experimental_rerun()
        elif result and "Error" in result:
            st.error(f"KPI validation failed: {result['Error']}")


# Example usage with Streamlit
if __name__ == "__main__":
    review = ReviewCardGenerator("events.csv")
    review.run_review_card()
