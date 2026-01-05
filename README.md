# AI-Enabled Content Framework (Virtual Project Manager)

## Project Overview
This project transforms early-stage project discussions (transcripts, emails, notes) into structured, high-quality documentation. It acts as a **Virtual Project Manager (VPM)** that ensures consistency, quality, and speed during project initiation.

## Core Features
- **Intelligent Ingestion**: Processes transcripts, meeting notes, and emails using AI.
- **Automated Documentation**: Generates Scope Documents and Content Frameworks.
- **Reference Validation**: Compares new documents against successful past projects for quality assurance.
- **Feedback Loop**: Incorporates stakeholder reviews to continuously improve AI output.

## Folder Structure
- `backend/`: Core AI processing, validation engine, and utilities.
- `frontend/`: Streamlit interface for user interaction.
- `templates/`: Markdown/HTML/DOCX templates for standard documents.
- `knowledge_base/`: Reference documents for validation.
- `data/`: Temporary storage for raw inputs and generated outputs.

## Tech Stack
- **Language**: Python 3.10+
- **AI Models**: Groq Llama-3.3, Google Gemini 1.5 Pro
- **Backend Framework**: FastAPI
- **Frontend Framework**: Streamlit
- **Database**: ChromaDB (Vector store for validation and learning)

## Setup
1. Create `.env` and set `GROQ_API_KEY`.
   - Optionally set `GOOGLE_API_KEY` for Gemini.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Populate Knowledge Base from examples:
   - `python backend/ingest_examples.py`
4. Run UI:
   - `streamlit run frontend/app.py`

## Features
- Generate Strategic Scope (with gap analysis) and Content Framework.
- Validate against indexed past projects using local embeddings.
- Export Scope and Framework to Markdown via UI.
- Submit feedback; feedback is indexed into the Knowledge Base for continuous improvement.
 - Choose provider in UI: Groq, Gemini, or Hybrid to use both.


 #python backend/evaluate_examples.py --provider hybrid
