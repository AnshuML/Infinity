#  Infinity: AI-Enabled Virtual Project Manager (VPM)

**Infinity** is a premium, AI-driven strategic initiation framework designed to transform messy project discussions into professional, structured documentation. It acts as a **Virtual Project Manager**, bridging the gap between raw client requirements and technical execution.

---

##  Key "Interviewer-Happy" Features

### 🌐 **1. Dynamic Visual Architecture (Sitemap)**
Don't just read the structure—see it! The VPM generates a **live hierarchical graph** of your project's architecture using Graphviz. 
- Visualizes Page Hierarchy
- Identifies Navigation Flows
- Provides a high-level architectural view at a glance.

###  **2. Project Maturity Index & Confidence Score**
A built-in **Risk Assessment Engine** that evaluates the "readiness" of your project.
- **Score Calculation:** Automatically deducts points for identified gaps.
- **Status Indicators:** 🟢 Ready for Development | 🟡 Needs More Detail | 🔴 High Risk.
- **Business Value:** Prevents project failure by identifying missing dependencies early.

###  **3. VPM Intelligence Trace**
A real-time **backend reasoning log** that shows the user exactly what the AI is thinking.
- Tracks Knowledge Base searches.
- Logs specific reasoning steps (Scope Generation, Quality Checks, Reference Crossing).
- Demonstrates technical transparency and system reliability.

###  **4. Hybrid AI Engine (Groq + Gemini)**
Leverage the best of both worlds!
- **Llama-3.3 (via Groq):** Used for heavy logical reasoning and gap analysis (Ultra-fast).
- **Gemini-1.5 Pro (via Google):** Used for speed, multimodal understanding, and creative formatting.
- **Hybrid Mode:** Combines outputs from both for the most robust documentation.

---

## 🛠 Features Breakdown

- ** Strategic Scope Generation:** Automatically creates high-quality Scope Documents with Objectives, In-Scope/Out-of-Scope boundaries, and Navigation structures.
- **📄 Site-Map & Content Framework:** Generates page-by-page functional requirements and CTA strategies.
- **🔍 Automated Gap Analysis:** Identifies what the client *didn't* say but *needs* to know.
- **📚 Knowledge Base (RAG):** Uses Vector Search (FAISS + Sentence Transformers) to compare current projects against past successful ones for consistency.
- **📥 Feedback Loop:** Stakeholder comments are instantly re-indexed into the knowledge base to improve future AI outputs.
- **📤 Multi-Format Export:** Export your professional documents to **Markdown** or **DOCX** with one click.

---

## 🏗 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | Streamlit (Premium Custom CSS + Glassmorphism) |
| **Backend** | FastAPI / Python 3.10+ |
| **AI Layer** | LangChain, Llama-3.3 (Groq), Gemini-1.5 (Google) |
| **Vector DB** | FAISS (Local Vector Search) |
| **Embeddings** | HuggingFace (sentence-transformers/all-MiniLM-L6-v2) |
| **Visuals** | Graphviz Core |

---

##  Getting Started

### 1. Prerequisites
Ensure you have Python 3.10 or higher installed.

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/AnshuML/Infinity.git
cd Infinity

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_key_here
GOOGLE_API_KEY=your_google_key_here
```

### 4. Run the Application
```bash
# Start the Integrated Streamlit UI
streamlit run frontend/app.py
```

### 5. Evaluate System Accuracy
Run the automated evaluation script to test AI performance against historical examples:
```bash
python backend/evaluate_examples.py --provider hybrid
```

---

## 📂 Project Structure
```text
infinity/
├── backend/            # AI Core, Validation & Export Logic
├── frontend/           # Streamlit Premium Interface
├── data/               # Project Input/Output Examples
├── knowledge_base/     # Vector Index & Stored Reference Data
├── .gitignore          # Protected secrets & ignored files
└── requirements.txt    # System Dependencies
```

---

##  Why this Project?
This project demonstrates **Full-Stack AI Engineering** capabilities:
1. **RAG Implementation:** Retrieval-Augmented Generation for quality control.
2. **System Design:** Handling complex state and multiple AI providers.
3. **UX/UI Excellence:** Creating tools that are both functional and visually stunning.
4. **Product Mindset:** Focusing on "Gap Analysis" and "Maturity Scores"—real-world PM problems.

---
Developed with  by **Anshu**
