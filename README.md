# AI IT Support

An AI-powered IT Support application that uses **Retrieval-Augmented Generation (RAG)** to provide troubleshooting assistance for common IT issues.

## Features

* AI-powered IT troubleshooting
* Retrieval-Augmented Generation (RAG)
* Knowledge base for common IT problems
* Ticket classification
* Ticket priority detection
* Ticket escalation
* Admin functionality
* Automated troubleshooting responses

## Knowledge Base

The current knowledge base contains troubleshooting information for:

* VPN
* Wi-Fi
* Password
* Email
* Printer

## How It Works

```text
User submits an IT issue
        ↓
Ticket Intelligence
        ↓
Category + Priority
        ↓
Knowledge Base Search
        ↓
Relevant Information Retrieved
        ↓
AI-generated Troubleshooting Response
        ↓
Escalation if Required
```

## Project Structure

```text
ai-it-support/
│
├── app.py
├── admin.py
├── rag.py
├── old_rag.py
├── ticket_intelligence.py
├── escalation.py
├── tickets.py
│
├── knowledge/
│   ├── email.md
│   ├── password.md
│   ├── printer.md
│   ├── vpn.md
│   └── wifi.md
│
├── test_rag.py
├── test_ticket.py
├── test_ticket_intelligence.py
├── test_escalation.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Technologies

* Python
* Streamlit
* Retrieval-Augmented Generation (RAG)
* ChromaDB
* Sentence Transformers
* Transformers
* PyTorch

## Installation

Clone the repository:

```bash
git clone https://github.com/Criminals226/ai-it-support.git
cd ai-it-support
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
pip install -r requirements.txt
```

## Environment Variables

If the application requires API keys, create a `.env` file in the project root and add the required credentials.

**Do not upload `.env` or API keys to GitHub.**

## Run the Application

Start the Streamlit application:

```powershell
streamlit run app.py
```

Then open the local URL provided by Streamlit in your browser.

## Testing

The project includes separate test files for different components.

For example:

```powershell
python test_rag.py
```

```powershell
python test_ticket_intelligence.py
```

```powershell
python test_escalation.py
```

## Project Status

This project is currently under development. The system is being expanded with additional ticket intelligence, RAG capabilities, automation, and IT support features.

## Repository

GitHub: https://github.com/Criminals226/ai-it-support
