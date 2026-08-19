# app.py
import streamlit as st
from KPIOperationalEventLoader import KPIOperationalEventLoader
from kpiinputhandler import KPIInputHandler

class ConversationalUI:
    def __init__(self, data_file: str):
        # Initialize loader and handler
        self.loader = KPIOperationalEventLoader(data_file)
        self.handler = KPIInputHandler(self.loader)

    def run_ui(self):
        st.title("Conversational KPI UI")

        # --- Text Input for KPI Name ---
        kpi_name = st.text_input("Enter KPI Name:")

        # --- Radio Button Example ---
        choice = st.radio(
            "Select a business unit:",
            options=["Logistics", "Manufacturing", "Sales", "Support"]
        )

        # --- File Upload (Image or Text File) ---
        uploaded_file = st.file_uploader("Upload an image or text file", type=["png", "jpg", "jpeg", "txt"])

        # --- Buttons ---
        col1, col2, col3 = st.columns(3)
        submit_btn = col1.button("Submit")
        cancel_btn = col2.button("Cancel")
        close_btn = col3.button("Close")

        # --- Logic for Buttons ---
        if submit_btn:
            st.subheader("Submitted Inputs")
            st.write("**KPI Name:**", kpi_name)
            st.write("**Selected Business Unit:**", choice)

            if uploaded_file is not None:
                if uploaded_file.type.startswith("image"):
                    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
                elif uploaded_file.type == "text/plain":
                    content = uploaded_file.read().decode("utf-8")
                    st.text_area("Uploaded Text File Content", content, height=200)

            # Call KPIInputHandler with user KPI name
            if kpi_name:
                result = self.handler.handle_input(kpi_name)
                st.subheader("KPI Output")
                st.json(result)

        elif cancel_btn:
            st.warning("Inputs have been cleared. Please try again.")

        elif close_btn:
            st.stop()  # Stops the Streamlit app execution


# Run the app
if __name__ == "__main__":
    ui = ConversationalUI("C:\jitendra\JatinKRai-interview\DetectAssignment\KPIAgenticAIBuilder\DataLoader\operations_events.csv")
    ui.run_ui()
