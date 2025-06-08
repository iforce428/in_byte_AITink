# Alumni Insights Dashboard

This project provides an interactive dashboard for alumni data analysis, integrated with a chatbot for insights and an OCR tool for data extraction.

## Features

- **Interactive Dashboard**: Visualize alumni data with charts for graduation trends, gender distribution, programs, job titles, and geographic locations.
- **Dynamic Metrics**: Display key alumni metrics such as total alumni, active programs, global presence, employment rate, and current year graduates, with year-over-year change indicators.
- **AI-Powered Chatbot**: Engage with an intelligent chatbot to query alumni data using natural language, providing data-driven responses based on the comprehensive alumni database.
- **OCR Data Extraction**: Upload images containing structured data (e.g., alumni profiles) and use the OCR tool to extract information, which can then be processed and stored.
- **Resizable & Floating Chatbot**: The chatbot component is designed to be floating and can be minimized/maximized and resized, providing a flexible user experience.
- **Navigation Bar**: A modern navigation bar with a link to the ASBhive website and a direct link to the dashboard.

## Technologies Used

### Frontend
- **React**: A JavaScript library for building user interfaces.
- **Vite**: A fast build tool for modern web projects.
- **TypeScript**: A strongly typed superset of JavaScript that compiles to plain JavaScript.
- **Tailwind CSS**: A utility-first CSS framework for rapid UI development.
- **Chart.js**: A flexible JavaScript charting library for visualizing data.
- **psycopg2-binary**: Python PostgreSQL adapter
- **react-resizable**: For creating resizable components.
- **lucide-react**: A collection of beautiful open-source icons.

### Backend
- **Python**: The programming language used for the backend.
- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
- **OpenAI API**: Used for the AI chatbot and OCR functionalities.
- **PostgreSQL**: The relational database used to store alumni data.
- **Supabase**: Used as a backend-as-a-service, providing a PostgreSQL database and API access.
- **psycopg2**: A PostgreSQL adapter for Python.

## Setup Instructions

### Prerequisites
- Node.js (with npm) installed
- Python 3.x installed
- PostgreSQL database (e.g., Supabase project) with your alumni_profiles table
- OpenAI API Key

### 1. Backend Setup

Navigate to the `backend` directory:
```bash
cd backend
```

Install the Python dependencies:
```bash
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory and add your database connection URI and OpenAI API Key:
```
DATABASE_URL="postgresql://YOUR_USER:YOUR_PASSWORD@YOUR_HOST:YOUR_PORT/YOUR_DATABASE"
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
```

Run the backend server:
```bash
python server.py
```

The backend server will run on `http://localhost:8000`.

### 2. Frontend Setup

Navigate to the `frontend` directory:
```bash
cd frontend
```

Install the Node.js dependencies:
```bash
npm install
```

Run the frontend development server:
```bash
npm run dev
```

The frontend application will be accessible at `http://localhost:5173` (or another port if 5173 is in use).

## Usage

- Access the dashboard to view alumni analytics.
- Use the floating chatbot to ask questions about alumni data.
- Utilize the OCR tool to extract data from images (if integrated in the UI).

## Project Structure

```
. # project root
├── backend/
│   ├── requirements.txt
│   └── server.py
├── frontend/
│   ├── public/
│   │   └── images/
│   ├── src/
│   │   ├── assets/
│   │   │   └── images/
│   │   ├── components/
│   │   │   ├── charts/
│   │   │   ├── Chatbot.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   └── Navbar.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
└── README.md
```