# kpi_system.py
import streamlit as st
import pandas as pd

# ------------------------------
# Loader: reads and validates CSV
# ------------------------------
class KPIOperationalEventLoader:
    def __init__(self, csv_file: str):
        self.df = pd.read_csv(csv_file)
        self.validate_data()

    def validate_data(self):
        required_columns = [
            "event_id","event_date","business_unit","location","event_type",
            "event_status","category","priority","impact_type","resolution_status",
            "cost_amount","processing_hours","customer_count"
        ]
        for col in required_columns:
            if col not in self.df.columns:
                raise ValueError(f"Missing required column: {col}")
        self.df["cost_amount"] = pd.to_numeric(self.df["cost_amount"], errors="coerce").fillna(0)
        self.df["processing_hours"] = pd.to_numeric(self.df["processing_hours"], errors="coerce").fillna(0)
        self.df["customer_count"] = pd.to_numeric(self.df["customer_count"], errors="coerce").fillna(0)


# ------------------------------
# Backend: validates and executes KPI intents
# ------------------------------
class KPINameReference:
    def __init__(self, loader_or_file):
        if isinstance(loader_or_file, KPIOperationalEventLoader):
            self.df = loader_or_file.df
        else:
            self.df = KPIOperationalEventLoader(loader_or_file).df

    def validate_intent(self, intent: dict):
        errors = []
        required_fields = ["kpi_name","metric_type","filters","aggregation","time_period"]
        for f in required_fields:
            if f not in intent:
                errors.append(f"Missing required field: {f}")
        valid_event_types = self.df["event_type"].unique().tolist()
        valid_priorities = self.df["priority"].unique().tolist()
        fval = intent.get("filters","")
        if fval == "Only Issues" and "Issue" not in valid_event_types:
            errors.append("Invalid filter: Issue not found")
        if fval == "Only Near Misses" and "Near Miss" not in valid_event_types:
            errors.append("Invalid filter: Near Miss not found")
        if fval == "High Priority" and "High" not in valid_priorities:
            errors.append("Invalid filter: High not found")
        return errors

    def execute_intent(self, intent: dict):
        errors = self.validate_intent(intent)
        if errors:
            return {"Error": errors}
        df_filtered = self.df.copy()
        fval = intent["filters"]
        if fval == "Only Issues":
            df_filtered = df_filtered[df_filtered["event_type"]=="Issue"]
        elif fval == "Only Near Misses":
            df_filtered = df_filtered[df_filtered["event_type"]=="Near Miss"]
        elif fval == "High Priority":
            df_filtered = df_filtered[df_filtered["priority"]=="High"]

        metric_type = intent["metric_type"]
        result, formula, num, den = None, "", None, None
        if metric_type=="Count":
            result = len(df_filtered)
            formula = f"Count of rows with filter={fval}"
        elif metric_type=="Sum":
            result = df_filtered["cost_amount"].sum()
            formula = f"Sum(cost_amount) with filter={fval}"
        elif metric_type=="Average":
            result = df_filtered["processing_hours"].mean()
            formula = f"Average(processing_hours) with filter={fval}"
        elif metric_type=="Ratio":
            num = len(self.df[self.df["event_type"]=="Near Miss"])
            den = len(self.df[self.df["event_type"]=="Issue"])
            result = num/den if den>0 else None
            formula = "Count(Near Miss)/Count(Issue)"
        return {
            "KPIName": intent["kpi_name"],
            "MetricType": metric_type,
            "Filters": fval,
            "Aggregation": intent["aggregation"],
            "TimePeriod": intent["time_period"],
            "ComputedValue": result,
            "Formula": formula,
            "Numerator": num,
            "Denominator": den
        }


class KPIAgentHandler:
    def __init__(self, data_file: str):
        self.reference = KPINameReference(data_file)
        # Conversation state tracks progression and data
        self.state = {
            "step": 0,
            "intent": {
                "kpi_name": None,
                "metric_type": None,
                "filters": None,
                "aggregation": None,
                "time_period": None
            }
        }

    def run_flow(self):
        st.title("Agentic KPI Handler")

        # Step 0: User enters KPI name
        if self.state["step"] == 0:
            kpi_name = st.text_input("Enter KPI Name:")
            if kpi_name:
                st.write(f"Agent: You want to compute KPI '{kpi_name}'. Let's refine its definition together.")
                self.state["intent"]["kpi_name"] = kpi_name
                self.state["step"] = 1

        # Step 1: Dynamic contextual questions
        if self.state["step"] == 1:
            kpi_name = self.state["intent"]["kpi_name"]
            st.subheader("Step 2: Define KPI Context")

            # Adapt questions based on KPI name
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
                metric_type = st.radio("Metric type?", ["Count","Sum","Average","Ratio"])
                filters = st.radio("Filters?", ["All Events","Only Issues","Only Near Misses","High Priority"])
                aggregation = st.radio("Aggregation?", ["Total","Mean"])

            time_period = st.radio("Time period?", ["Daily","Weekly","Monthly","Yearly"])

            if st.button("Submit Definition"):
                # Build structured KPI Intent JSON
                self.state["intent"].update({
                    "metric_type": metric_type,
                    "filters": filters,
                    "aggregation": aggregation,
                    "time_period": time_period
                })
                st.subheader("Structured KPI Intent")
                st.json(self.state["intent"])
                self.state["step"] = 2

        # Step 2: Compute KPI
        if self.state["step"] == 2:
            result = self.reference.execute_intent(self.state["intent"])
            st.subheader("Final KPI Result")
            st.json(result)
            return result

# ------------------------------
# Review Card: displays results
# ------------------------------
class ReviewCardGenerator:
    def __init__(self, data_file: str):
        self.agent=KPIAgentHandler(data_file)

    def compute_status_badge(self,kpi_name,value):
        if value is None: return "Critical"
        if "Ratio" in kpi_name:
            return "Good" if value<0.5 else "Warning" if value<1.0 else "Critical"
        if "Count" in kpi_name:
            return "Good" if value==0 else "Warning" if value<5 else "Critical"
        if "Average" in kpi_name or "Hours" in kpi_name:
            return "Good" if value<10 else "Warning" if value<20 else "Critical"
        return "Warning"

    def run_review_card(self):
        st.title("KPI Review Card")
        result=self.agent.run_flow()
        if result and "Error" not in result:
            kpi_name=result["KPIName"]
            val=result["ComputedValue"]
            formula=result["Formula"]
            unit="events" if result["MetricType"]=="Count" else "hours" if result["MetricType"]=="Average" else "ratio"
            badge=self.compute_status_badge(kpi_name,val)
            st.subheader("KPI Review Card")
            st.write(f"**KPI Name:** {kpi_name}")
            st.write(f"**Description:** KPI '{kpi_name}' measures operational performance.")
            st.write(f"**Formula:** {formula}")
            st.write(f"**Computed Value:** {val}")
            st.write(f"**Unit:** {unit}")
            st.write(f"**Status:** {badge}")
            if result["MetricType"]=="Ratio":
                st.write(f"**Numerator:** {result['Numerator']}")
                st.write(f"**Denominator:** {result['Denominator']}")
            col1,col2,col3=st.columns(3)
            approve_btn=col1.button("Approve",disabled=(val is None))
            edit_btn=col2.button("Edit")
            regen_btn=col3.button("Regenerate")
            if approve_btn: st.success("KPI Approved.")
            if edit_btn: 
                self.agent.state["step"]=1
            if regen_btn: 
                self.agent.state={"step":0,"intent":{}}
                st.experimental_rerun()
        elif result and "Error" in result:
            st.error(f"KPI validation failed: {result['Error']}")


# ------------------------------
# Example usage with Streamlit
# ------------------------------
if __name__=="__main__":
    review=ReviewCardGenerator("C:\jitendra\JatinKRai-interview\DetectAssignment\KPIAgenticAIBuilder\DataLoader\operations_events.csv")
    review.run_review_card()
