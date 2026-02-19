# Deployment Guide

This project is split into two parts:
1.  **Backend (Python/Flask)** -> Deploy on **Render** (or Railway).
2.  **Frontend (React/Vite)** -> Deploy on **Vercel**.

---

## Part 1: Deploy Backend (Render)

1.  Sign up at [render.com](https://render.com/).
2.  Click **"New +"** -> **"Web Service"**.
3.  Connect your GitHub repository.
4.  Use the following settings:
    -   **Name**: `emotion-music-backend` (or similar)
    -   **Runtime**: **Python 3**
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `gunicorn app:app`
5.  **Environment Variables** (Advanced -> Add Environment Variable):
    -   Key: `MONGO_URI`
    -   Value: `your_mongodb_connection_string` (Copy from your local `.env`)
    -   Key: `TF_ENABLE_ONEDNN_OPTS`
    -   Value: `0`
    -   Key: `PYTHON_VERSION`
    -   Value: `3.11.9`
    -   **Update Build Command**: `./render-build.sh`
6.  Click **"Create Web Service"**.
7.  Wait for deployment. Once live, copy the **Backend URL** (e.g., `https://emotion-backend.onrender.com`).

---

## Part 2: Deploy Frontend (Vercel)

1.  Sign up at [vercel.com](https://vercel.com/).
2.  Click **"Add New..."** -> **"Project"**.
3.  Import your GitHub repository.
4.  **Framework Preset**: Select **Vite**.
5.  **Root Directory**: Click "Edit" and select `client`.
6.  **Environment Variables**:
    -   Key: `VITE_API_URL`
    -   Value: `https://emotion-backend.onrender.com` (Paste the URL from Part 1)
7.  Click **"Deploy"**.

---

## Final Verification
Open your Vercel URL. It should load the frontend and connect to the Render backend for emotion detection.
