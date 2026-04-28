# 📰 Big Data News Classifier — AI Powered

A scalable news headline classifier using **DistilBERT**, **FastAPI**, and **Streamlit**,
trained on **live 2026 news** fetched from the NewsAPI.

---

## 🗂️ Project Structure

```text
news_classifier/
├── news_fetcher.py          ← Fetch 2026 headlines from NewsAPI
├── classifier.py            ← Baseline ML models (Naive Bayes, LogReg)
├── distilbert_classifier.py ← Train advanced DistilBERT model
├── api.py                   ← FastAPI real-time prediction backend
├── app.py                   ← Streamlit interactive UI dashboard
├── scheduler.py             ← Scheduled daily data fetcher
├── requirements.txt         ← All Python dependencies
├── Dockerfile               ← Docker deployment configuration
├── README.md                ← This file
└── .gitignore               ← Excludes model_output/, datasets/, *.csv
```

> **Note:** The `model_output/` directory (trained model files) and dataset files are generated at runtime and are excluded from GitHub via `.gitignore`.

---

## ⚙️ Setup — Local Execution

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Get a FREE NewsAPI key
1. Go to 👉 https://newsapi.org/register
2. Sign up (it's free, no credit card)
3. Copy your API key from the dashboard

### Step 3 — Add your API key
Create a `.env` file in the root directory and add your key:
```env
NEWSAPI_KEY=abc123yourkeyhere
```

### Step 4 — Fetch 2026 live news data
```bash
python news_fetcher.py
```
This saves **news_2026.csv** with headlines from 7 categories:
`BUSINESS | ENTERTAINMENT | GENERAL | HEALTH | SCIENCE | SPORTS | TECHNOLOGY`

### Step 5 — Train the Model
```bash
python distilbert_classifier.py
```
This trains the DistilBERT model and saves it to `./model_output`.

### Step 6 — Run the App
Start the backend API:
```bash
uvicorn api:app --reload
```
Start the frontend UI (in a new terminal):
```bash
streamlit run app.py
```

---

## 🐳 Docker Deployment

You can run the entire application (API + UI) using Docker.

```bash
# Build the image
docker build -t news-classifier .

# Run the container (Make sure you have trained the model first, or map the volume!)
docker run -p 8000:8000 -p 8501:8501 --env-file .env news-classifier
```

---

## 🚀 Features

- **Advanced NLP**: BERT / DistilBERT transformer model for higher accuracy.
- **REST API**: Built with FastAPI for real-time predictions.
- **Interactive UI**: Streamlit web dashboard for interactive sentiment tracking.
- **Automation**: Scheduled daily fetch to grow the dataset automatically.
- **Sentiment Analysis**: Understand the underlying tone of the news.
