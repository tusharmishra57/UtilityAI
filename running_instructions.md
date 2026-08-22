# UtilityAI Project Run Guide

This guide provides instructions to run the UtilityAI application locally on your machine. The application is divided into a FastAPI Python backend and a React + Vite TypeScript frontend.

---

## 🛠️ Step 1: Backend Setup & Database Initialization

The backend uses **Python** (FastAPI) and a **PostgreSQL** database with the `pgvector` extension for AI-driven semantic retrieval (RAG).

### 1. Set Up the Virtual Environment
Navigate to the `backend` directory and ensure a virtual environment is active.
- **Windows (PowerShell)**:
  ```powershell
  cd backend
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **macOS/Linux**:
  ```bash
  cd backend
  python3 -m venv venv
  source venv/bin/activate
  ```

### 2. Install Dependencies
Install all required libraries specified in [requirements.txt](file:///d:/Desktop/Utility%20consumption/backend/requirements.txt):
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy [.env.example](file:///d:/Desktop/Utility%20consumption/backend/.env.example) to `.env` and fill in the required configurations:
- **`DATABASE_URL`**: Your connection string for PostgreSQL (supports Neon Tech, local PG instances, etc.).
- **`GEMINI_API_KEY`**: Your Google Gemini API Key.
- **`SECRET_KEY`**: A secure key for signing JWT tokens (can be generated using `openssl rand -hex 32`).

*Note: The project is currently configured with a `.env` containing a Neon Database URL and a configured Gemini API Key.*

### 4. Initialize the Database Schema
Run the database setup script to enable the vector extension and create the required tables:
```bash
python init_db.py
```

### 5. Seed the Database
Run the seeding script. This loads policy documentation (`billing_guide.txt`, `energy_saving.txt`, `payment_policy.txt`), generates embeddings for AI search, and registers a test user account:
```bash
python seed.py
```

---

## 💻 Step 2: Start the Backend Server

Start the FastAPI application on port `8000` (which matches the URL configured in the frontend):
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```
Once started, the backend documentation will be accessible at:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🎨 Step 3: Frontend Setup & Dev Server

The frontend is built using React, Vite, Tailwind CSS, and Recharts.

### 1. Install Node Dependencies
Open a new terminal window, navigate to the `frontend` folder, and install all dependencies:
```bash
cd frontend
npm install
```

### 2. Start the Frontend Development Server
Run the Vite development server:
```bash
npm run dev
```
By default, the application will run at:
- **Local Dev Server**: [http://localhost:5173/](http://localhost:5173/)

---

## 👤 Step 4: Login & Features Verification

Once both servers are running:
1. Open [http://localhost:5173/](http://localhost:5173/) in your web browser.
2. Log in using the seeded test account:
   - **Email**: `test@example.com`
   - **Password**: `password123`
3. Explore the dashboard:
   - **Analytics Charts**: Displays monthly energy consumption history in kWh.
   - **Bills Summary**: Check paid and unpaid invoices.
   - **Payment Simulation**: Pay outstanding bills directly through the simulated workflow.
   - **AI Chat Assistant (RAG)**: Chat with the AI regarding billing queries, energy-saving tips, or payment policies. Try asking: *"How can I save energy?"* or *"What is the payment policy?"*
