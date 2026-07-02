# 🧭 Smart Task Router

A lightweight system that routes each incoming request to a **cheap/fast model** or a **larger model**, based on how complex the request is — and shows the real cost and latency tradeoff on a live dashboard.

Most LLM demos just call one model for everything. In production, that's expensive and slow. This project shows a simple, working example of intelligent model routing: simple questions get answered instantly and cheaply, complex ones get escalated to a stronger model — automatically.

## 🎥 Demo

*(Add a screenshot or GIF of the app here once you run it)*

## 🛠️ Tech Stack

- **FastAPI** — backend API (`/route`, `/history` endpoints)
- **Streamlit** — frontend dashboard, no HTML/CSS/JS needed
- **Groq API** — free-tier LLM inference (fast, generous free quota)
- **SQLite** — zero-setup local logging of every request
- **Python + requests** — no heavy agent frameworks, so the routing logic is fully transparent

## 🧠 How It Works

1. User submits a request in the Streamlit UI
2. The backend classifies it as `simple` or `complex` using a lightweight rule-based heuristic (word count + keyword matching)
3. Based on the classification, it calls either:
   - `llama-3.1-8b-instant` for simple requests (fast, cheap)
   - `llama-3.3-70b-versatile` for complex requests (stronger reasoning)
4. The response, model used, latency, tokens, and estimated cost are logged to SQLite
5. The dashboard shows live history and running total cost

## 🚀 Running It Locally

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/smart-task-router.git
cd smart-task-router
```

### 2. Set up a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Add your API key
Get a free key from [Groq Console](https://console.groq.com), then:
```bash
cp .env.example .env
# edit .env and paste your key
```

### 4. Start the backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 5. Start the frontend (in a new terminal)
```bash
streamlit run app.py
```

Open the URL Streamlit gives you (usually `http://localhost:8501`).

## 📁 Project Structure
```
smart-task-router/
├── app.py              # Streamlit frontend
├── backend/
│   ├── main.py          # FastAPI app + endpoints
│   ├── router.py         # Complexity classification + model routing
│   └── db.py              # SQLite logging
├── requirements.txt
├── .env.example
└── README.md
```

## 💡 What I Learned

Building this taught me how model routing works in production LLM systems, and why it matters for cost control. I intentionally avoided heavy agent frameworks (like LangChain) at first so I could understand the request → classify → route → log flow without abstraction hiding the logic.

**What I'd improve next:** replace the rule-based classifier with a tiny model-based classifier, add authentication, and deploy the backend so the whole app is live rather than local-only.

## 📄 License

MIT
