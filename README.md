# Enterprise HR Policy & Employee Assistant

## Project Overview

The **Enterprise HR Policy & Employee Assistant** is an AI-powered HR portal designed to help employees access company HR policies and employee-specific information through a user-friendly interface.

The project combines **FastAPI, Streamlit, PostgreSQL, RAG, and LangGraph** to support HR-related queries and employee workflows.

## Features

- **Employee Dashboard:** View employee information and leave balances.
- **Leave Management:** View leave balances, apply for leave, and access leave requests.
- **Leave Request Operations:** Support leave request modification, cancellation, and approval through backend APIs.
- **Payroll Management:** Retrieve payroll information and the latest payroll record.
- **Holiday Calendar:** View company holidays and check holiday dates.
- **AI HR Assistant:** Ask questions about HR policies using Retrieval-Augmented Generation (RAG).
- **Agentic AI:** Use LangGraph orchestration and configured tools for employee-related workflows.
- **Employee Sessions:** Create, track, and close employee sessions.
- **Logging:** Record application events such as login and logout.

## Technology Stack

- Python
- FastAPI
- Streamlit
- PostgreSQL
- pgvector
- LangChain
- LangGraph
- Retrieval-Augmented Generation (RAG)
- Sentence Transformers
- BGE-M3 embeddings
- MCP tools, where configured
- Docker, where configured

## Project Structure

```text
Enterprise HR Policy & Employee Assistant/
│
├── src/
│   ├── API/
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── models.py
│   │   ├── db_models.py
│   │   └── database.py
│   │
│   ├── agents/
│   │   ├── graph.py
│   │   └── tools.py
│   │
│   ├── Rag/
│   │   ├── process.py
│   │   ├── embedding.py
│   │   └── retrieval.py
│   │
│   ├── UI/
│   │   └── app.py
│   │
│   └── app_logging/
│       └── logger.py
│
├── logs/
│   └── app.log
│
├── my-env/
│
└── README.md
```

*Note: The structure may vary depending on the current implementation.*

## Prerequisites

Before running the application, ensure that you have installed:

- Python
- PostgreSQL
- pgvector PostgreSQL extension
- Required Python packages
- HR policy PDF documents
- A configured LLM or model provider for the AI assistant

## Installation and Setup

### 1. Navigate to the Project Directory

Open PowerShell and run:

```powershell
cd "D:\python_dy\Python_Repo\Abhilasha_Ishware\Enterprise HR Policy & Employee Assistant"
```

### 2. Activate the Virtual Environment

If the virtual environment already exists:

```powershell
.\my-env\Scripts\Activate.ps1
```

To create a new virtual environment:

```powershell
python -m venv my-env
.\my-env\Scripts\Activate.ps1
```

### 3. Install Dependencies

If your project contains a `requirements.txt` file, run:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Otherwise, install the dependencies used by the project and maintain a `requirements.txt` file for reproducible setup.

### 4. Configure PostgreSQL

Ensure PostgreSQL is running and that the application is configured to connect to the correct database.

Enable pgvector in the target database:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Configure the database connection and model-provider settings according to the variables used in your application.

Do not commit database passwords, API keys, or other secrets to version control.

### 5. Prepare HR Policy Documents

Place the policy PDF files in the directory expected by `src/Rag/process.py`.

The current policy dataset has included:

- Company Handbook Overview
- Leave and Time-Off Policy
- Public Holiday Calendar
- Remote and Hybrid Work Policy
- Code of Conduct Policy
- Payroll and Compensation Policy
- Grievance and Escalation Policy

Process the documents, generate embeddings, and store them in PostgreSQL with pgvector using the project's RAG pipeline.

## Running the Application

Run the backend and frontend in separate terminals.

### 1. Start the FastAPI Backend

Activate the virtual environment and run:

```powershell
.\my-env\Scripts\Activate.ps1
uvicorn src.API.main:app --reload
```

The API will be available at:

**Base URL:** http://127.0.0.1:8000

**Swagger Documentation:** http://127.0.0.1:8000/docs

### 2. Start the Streamlit Frontend

Open another terminal in the project root and run:

```powershell
.\my-env\Scripts\Activate.ps1
streamlit run src/UI/app.py
```

Open the local URL displayed in the terminal to access the HR portal.

## API Endpoints

The backend currently provides endpoints for the following operations:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/check` | Check API availability |
| GET | `/employees/{employee_id}` | Retrieve employee details |
| GET | `/employees/{employee_id}/leave-balance` | Retrieve leave balances |
| GET | `/employees/{employee_id}/leave-requests` | Retrieve employee leave requests |
| POST | `/employees/{employee_id}/leave-requests` | Apply for leave |
| PUT | `/employees/{employee_id}/leave-requests/{request_id}` | Modify a leave request |
| DELETE | `/employees/{employee_id}/leave-requests/{request_id}` | Cancel a leave request |
| PUT | `/employees/{employee_id}/leave-requests/{request_id}/approve` | Approve a leave request |
| GET | `/employees/{employee_id}/payroll` | Retrieve payroll records |
| GET | `/employees/{employee_id}/payroll/latest` | Retrieve the latest payroll record |
| GET | `/holidays` | Retrieve holiday information |
| GET | `/holidays/{year}` | Retrieve holidays for a specific year |
| POST | `/sessions` | Create an employee session |
| PUT | `/sessions/{session_id}/close` | Close an employee session |
| POST | `/agent` | Submit a query to the AI HR assistant |

For complete request and response schemas, refer to the running Swagger documentation at `/docs`.

## Leave Application Workflow

Employees can submit leave applications through the Streamlit Leave page.

The frontend sends a request to:

```text
POST /employees/{employee_id}/leave-requests
```

Example request body:

```json
{
  "employee_id": "EMP001",
  "leave_type": "Sick Leave",
  "start_date": "2026-10-27",
  "end_date": "2026-10-27",
  "number_of_days": 1,
  "reason": "sick"
}
```

The employee ID should be populated from the logged-in session. The request is expected to be created with a pending status, according to the current backend implementation.

The application validates the date range and number of days in the frontend. Additional server-side validation is important to verify leave eligibility, available balance, overlapping requests, and applicable company policies.

## RAG Workflow

The Retrieval-Augmented Generation workflow follows these steps:

1. Load HR policy PDF documents.
2. Split the documents into smaller text chunks.
3. Generate embeddings using the configured embedding model.
4. Store embeddings and document metadata in PostgreSQL using pgvector.
5. Retrieve relevant chunks when an employee asks a policy question.
6. Use the configured LLM and agent workflow to generate a response based on the retrieved information.

The implementation is maintained in the `src/Rag/` directory.

## Logging

Application logging is configured in `src/app_logging/logger.py`.

The project records events such as employee session creation and closure. Logs can help with debugging and understanding application activity.

Sensitive information, passwords, API keys, and unnecessary payroll or employee details should not be written to logs.


## Troubleshooting

### FastAPI Connection Error

- Ensure the FastAPI server is running.
- Verify that `FASTAPI_URL` in `src/UI/app.py` matches the backend address.

### Leave Application Validation Error

- Check that the request body includes all required fields, including `employee_id`.
- Ensure dates and number of days are valid.
- Verify that the payload matches the `LeaveRequestCreate` model in `src/API/models.py`.

### Database Connection Error

- Ensure PostgreSQL is running.
- Verify the database connection configuration.
- Confirm that the required tables and pgvector extension exist in the target database.

### RAG Retrieval Error

- Confirm that the policy PDFs are available in the expected directory.
- Verify that document processing and embedding completed successfully.
- Ensure the retriever is connected to the correct database and vector table.


## Future Enhancements

- Role-based employee and HR dashboards
- More comprehensive leave eligibility and balance validation
- HR approval workflows and notifications
- Improved conversation memory and session management
- Automated testing and monitoring
- Secure production deployment

