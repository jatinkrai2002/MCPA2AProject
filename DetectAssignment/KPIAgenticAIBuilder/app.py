# app.py
import streamlit as st
import pandas as pd
from PIL import Image

class ConversationalUI:
    def __init__(self):
        self.run_ui()

    def run_ui(self):
        st.title("Conversational UI")

        # --- Text Input ---
        user_text = st.text_input("Enter your text:")

        # --- Radio Button / Multiple Choice ---
        choice = st.radio(
            "Select an option:",
            options=["Option A", "Option B", "Option C"]
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
            st.subheader("Submitted Inputs and Outputs")
            st.write("**Text Input:**", user_text)
            st.write("**Selected Option:**", choice)

            if uploaded_file is not None:
                if uploaded_file.type.startswith("image"):
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Uploaded Image", use_column_width=True)
                elif uploaded_file.type == "text/plain":
                    content = uploaded_file.read().decode("utf-8")
                    st.text_area("Uploaded Text File Content", content, height=200)

            # Example Output Logic
            st.success("Processing complete! Here are your results.")
            st.write("Echoed Text:", user_text.upper())
            st.write("Choice Mapping:", f"You selected {choice}")

        elif cancel_btn:
            st.warning("Inputs have been cleared. Please try again.")

        elif close_btn:
            st.stop()  # Stops the Streamlit app execution

# Run the app
if __name__ == "__main__":
    ConversationalUI()
