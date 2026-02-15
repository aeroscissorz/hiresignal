# Intent Engine

Multi-tenant real-time hiring opportunity detection system with React frontend and Supabase backend.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  React Frontend │────▶│    Supabase     │
│   (User Auth)   │     │  (PostgreSQL)   │
└─────────────────┘     └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │  Intent Engine  │
                        │ (Python Backend)│
                        └────────┬────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
        ┌──────────┐      ┌──────────┐      ┌──────────┐
        │  Reddit  │      │   HN     │      │ Telegram │
        │   RSS    │      │   API    │      │   Bot    │
        └──────────┘      └──────────┘      └──────────┘
```

## Setup

### 1. Supabase Database

1. Go to your Supabase project SQL Editor
2. Run the contents of `supabase/schema.sql`

### 2. Backend (Python)

```bash
pip install -r requirements.txt
python main.py
```

### 3. Frontend (React)

```bash
cd frontend
npm install
npm start
```

## Configuration

### Backend (.env)
```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
POLL_INTERVAL_SECONDS=60
SCORE_THRESHOLD=3
REDDIT_SUBREDDITS=forhire,freelance,startups
```

### Frontend (frontend/.env)
```
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_anon_key
```

## Features

- Multi-tenant: Each user has their own Telegram bot
- Single ingestion: Polls sources once, fans out to all users
- 24-hour window: Only processes posts from the last day
- Per-user keywords: Users define their own skill keywords
- Duplicate prevention: Tracks notifications per user in database

## Deployment

Backend: Deploy to Railway, Fly.io, Render, or any VPS (512MB RAM sufficient)

Frontend: Deploy to Vercel, Netlify, or any static host
