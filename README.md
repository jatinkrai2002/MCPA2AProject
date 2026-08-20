Agentic KPI Builder Assignment

This repository contains a working agentic AI application that guides users step by step from KPI name entry to computed results and review cards.

 Features
- Agentic Flow: Smooth progression from KPI name → contextual questions → structured intent → computed KPI.
- Dynamic Questions: Options derived dynamically from dataset columns (no hardcoded KPI logic).
- Intent & Schema: KPI definition represented as structured JSON with metric_type, filters, aggregation, and time_period.
- KPI Calculation: Executes count, sum, average, and ratio aggregations programmatically against `operations_events.csv`.
- Review Card UX: Displays KPI name, description, formula, computed value, unit, status badge, and Approve/Edit/Regenerate actions.
- Fallback Mode: If KPI name does not match a loader method, a mock LLM (rule-based text) generates a short description. No paid 



 Setup Instructions
1. 
created zip file using deploy.ps1
download zip file from the email.
Unzip it, and run locally with

Install dependencies:
pip install -r requirements.txt

Ensure data/operations_events.csv exists. A sample file is provided; you may replace it with your own operational events dataset.
API keys required and update into the .env file.
Visualize: In the LangSmith dashboard, you’ll see the workflow graph, node execution order, errors, and self‑healing loops.

Run the application:


python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8080

Opens the Streamlit UI in your browser (default: http://localhost:8501).

or
This file in your repo as tests/test_kpi_Builder Assignment.py and run it with pytest.
Install pytest:
pip install pytest

Run tests:
pytest -v

Expected Results

   Test 1 (IssueCount): Passes if computed value = 3 and formula starts with "Count".

   Test 2 (AverageProcessingHours): Passes if computed value equals mean of processing_hours (12.5 in sample data).

   Test 3 (NearMisstoIssueRatio): Passes if computed value equals 1 / 3 ≈ 0.333 and formula contains "Count(Near Miss)".

Assumptions
    The dataset operations_events.csv contains columns such as event_type, priority, processing_hours, and cost_amount.
    If Groq API is not available, the Builder Assignment falls back to a rule-based description generator.




Deploy. This setup ensures  app runs consistently across local Docker, multi‑container Compose, and scalable Kubernetes clusters.

1. Docker
docker build -t agentic-kpi-app -f docker/Dockerfile .
docker run --env-file .env -p 8501:8501 agentic-kpi-app

2. Docker Compose:
cd dockerCompose
docker-compose up --build -d


3. Kubernetes:
kubectl apply -f ak8/configmap.yaml
kubectl apply -f ak8/deployment.yaml
kubectl apply -f ak8/service.yaml


python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8080

 Instruction to run the code.
  1. Extract the agentic-kpi-app.zip into local folder e.g. agentic-kpi-app
  2. Update the env file with required keys.
  3. run the requirement.txt (python -r requirement.txt) to install all required library.
  4. Ensure the folder structure like below
     agentic-kpi-app/
			│
			├── app.py                  # Main entry point (run with `python app.py`)
			| -- appagentic.py
			| -- appstategraph.py
			├── requirements.txt        # Python dependencies
			├── README.md               # Setup instructions, assumptions, usage
			├── .env                    # environment variables such as GROQ_API_KEY, LANGSMITH_API_KEY, model
			│
			|-- deployment/
			|    └── deploy.ps1   # Deployment script for Agentic KPI Builder
			├── data/
			│   └── operations_events.csv   # Bundled dataset (or instructions to add)
			│
			├── kpi/
			│   ├── kpi_loader.py           # KPIOperationalEventLoader
			│   ├── kpi_input_handler.py    # KPIInputHandler
			│   ├── kpi_name_reference.py   # KPINameReference backend
			│   ├── kpi_agent_handler.py    # KPIAgentHandler agent flow
				|--- kpi_agentic_tools_handler # kpi_agentic_tools_handler
			│   └── review_card_generator.py # ReviewCardGenerator UX
				/tools
				  |-- kpinamefinder.py #Search api
			│
			├── assets/
			│   └── styles.css              # Optional styling for Streamlit
			│
			└── images/
				└── output1.png     # Example screenshot for README
				└── output2.png 
				
			|-- docker/
			|    └── 
			|-- dockerCompose/
			|    └── 
			|-- ak8/
			|    └── 
	5. run the application as below commmand from the current folder.
	   python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8080
	   
	6. Ensure the browser open with http://127.0.0.1:8080/
	
	7. Enter the KPIName such as "OpenIssueCount" and press enter key.
	
	8. Select options such as metric_type, filters, aggregation and time_period option value.
	
	9. Click submit definition.
	
	10. Ensure review_card_generator shows the data.
	
	11. Enter some other kpiname such as  "OpenIssueCountDetect" and select default options and click submit definition.
	
	12. Rule based flow will call LLM models with datasets, definition and provide output.
	
	13. I am getting data based on LLM models size and token input. (Known issue)
	
	Challenges: 
	"Request too large for model `llama-3.1-8b-instant` in organization `org_01jm77wbzsfzds2zxb43n6rc1g` service tier `on_demand` on tokens per minute (TPM): Limit 6000, Requested 36036, please reduce your message size and try again. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}'"




