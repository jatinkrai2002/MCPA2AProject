# kpi_agent_handler.py
import streamlit as st
from KPIOperationalEventLoader import KPIOperationalEventLoader
from kpiinputhandler import KPIInputHandler

class KPIAgentHandler:
    def __init__(self, data_file: str):
        self.loader = KPIOperationalEventLoader(data_file)
        self.handler = KPIInputHandler(self.loader)
        # Conversation state tracked across steps
        self.conversation_state = {
            "step": 0,
            "kpi_name": None,
            "metric_type": None,
            "filters": None,
            "aggregation": None,
            "time_period": None,
            "intent": None
        }

    def run_flow(self):
        st.title("Agentic KPI Handler")

        # Step 1: User enters KPI name
        if self.conversation_state["step"] == 0:
            kpi_name = st.text_input("Enter KPI Name:")
            if kpi_name:
                self.conversation_state["kpi_name"] = kpi_name
                st.write(f"Agent: You want to compute KPI '{kpi_name}'. Let's refine its definition together.")
                self.conversation_state["step"] = 1

        # Step 2: Contextual multiple-choice questions
        if self.conversation_state["step"] == 1 and self.conversation_state["kpi_name"]:
            st.subheader("Step 2: Define KPI Context")
            self.conversation_state["metric_type"] = st.radio(
                "What type of metric is this KPI?",
                ["Count", "Ratio", "Average", "Sum"]
            )
            self.conversation_state["filters"] = st.radio(
                "Which filter applies?",
                ["All Events", "Only Issues", "Only Near Misses", "High Priority"]
            )
            self.conversation_state["aggregation"] = st.radio(
                "Which aggregation logic?",
                ["Total", "Mean", "Max", "Min"]
            )
            self.conversation_state["time_period"] = st.radio(
                "What time period?",
                ["Daily", "Weekly", "Monthly", "Yearly"]
            )

            if st.button("Submit Definition"):
                # Build structured KPI Intent JSON
                self.conversation_state["intent"] = {
                    "kpi_name": self.conversation_state["kpi_name"],
                    "metric_type": self.conversation_state["metric_type"],
                    "filters": self.conversation_state["filters"],
                    "aggregation": self.conversation_state["aggregation"],
                    "time_period": self.conversation_state["time_period"]
                }
                st.subheader("Structured KPI Intent")
                st.json(self.conversation_state["intent"])
                self.conversation_state["step"] = 2

        # Step 3: Compute KPI result
        if self.conversation_state["step"] == 2:
            result = self.handler.handle_input(self.conversation_state["kpi_name"])
            st.subheader("Final KPI Result")
            st.json(result)

        if st.button("Close"):
            st.stop()


# Example usage with Streamlit
if __name__ == "__main__":
    agent = KPIAgentHandler("C:\jitendra\JatinKRai-interview\DetectAssignment\KPIAgenticAIBuilder\DataLoader\operations_events.csv")
    agent.run_flow()
