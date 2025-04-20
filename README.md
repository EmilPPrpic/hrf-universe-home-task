# Days to Hire API

This is a simple FastAPI app for calculating "days to hire" statistics based on job postings.

---

## 🔧 Features

- Minimal FastAPI setup (everything in `main.py` for simplicity)
- No authentication to keep it lightweight
- Configurable thresholds and batch size (via code)
- Batching used to handle large data efficiently

---

## ⚙️ Configuration

You can change these values directly in the code:

- `MIN_JOB_POSTINGS_THRESHOLD = 5` → Minimum number of job postings required to store stats
- `BATCH_SIZE = 1000` → Number of rows processed and written at a time

---

## 🚀 Running the App

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Run the FastAPI app**:

```bash
uvicorn main:app --reload
```

3. **Access the API**:

- Open your browser and go to `http://localhost:8000/docs` to see the API documentation and test the endpoints.