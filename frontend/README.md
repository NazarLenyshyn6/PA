# ML Agent Frontend

A Next.js frontend application for the ML Agent platform.

## Features

- Modern login/register pages with beautiful UI (no Google OAuth - email/password only)
- Dashboard for data upload and ML agent interaction
- TypeScript support
- Tailwind CSS for styling
- Responsive design
- Backend integration with localhost:8003

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Backend Requirements

Make sure your backend is running on **localhost:8003** before using the application.

## API Integration

The application integrates with the following backend endpoints (localhost:8003):

- `POST /api/v1/gateway/auth/login` - User authentication (form-urlencoded: username, password)
- `POST /api/v1/gateway/auth/register` - User registration (JSON: email, password)
- `POST /api/v1/gateway/files` - File upload
- `POST /api/v1/gateway/chat` - Chat with ML agent
- `GET /api/v1/gateway/session` - Session management

## Pages

- `/` - Redirects to login page (or chat if authenticated)
- `/login` - User login with email/password
- `/register` - User registration
- `/chat` - Main chat interface with ML Agent
- `/dashboard` - Data upload and analysis interface

## Tech Stack

- Next.js 14 with App Router
- TypeScript
- Tailwind CSS
- Lucide React Icons