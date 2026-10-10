# University AI Assistant - Frontend

Modern React application built with Vite and Tailwind CSS providing an authoritative, grounded chat assistant interface and administrative knowledge base management console.

---

## Features

- **Chat Assistant**: Real-time interactive AI chat with grounded citation badges, policy rule references, conflict warnings, and audit trace links.
- **Admin & Ingestion**: Live document ingestion console (`POST /ingest`) with immediate vector embeddings and live Source Register viewer (`GET /sources`).
- **System Health Monitor**: Live backend connection indicator and LLM mode status.
- **Tailwind CSS Styling**: Clean, modern enterprise UI with custom navy/slate palette, glassmorphism accents, and responsive layout.

---

## Directory Layout

```text
frontend/
├── src/
│   ├── components/
│   │   ├── Navbar.jsx       # Header navigation and system health status
│   │   └── AuditModal.jsx   # Detailed audit log inspector modal
│   ├── pages/
│   │   ├── ChatPage.jsx     # Main chat assistant interface
│   │   └── AdminPage.jsx    # Live document ingestion & Source Register
│   ├── lib/
│   │   └── api.js           # Centralized HTTP API client
│   ├── App.jsx              # Main application container
│   ├── main.jsx             # React DOM entrypoint
│   └── index.css            # Global CSS styles
├── public/                  # Static assets
├── vite.config.js           # Vite config with /api proxy to http://localhost:8000
├── package.json             # NPM package scripts and dependencies
├── tailwind.config.js       # Tailwind CSS configuration
└── Dockerfile               # Production container image
```

---

## Getting Started

### 1. Prerequisites
- Node.js 18+ or 20+
- `npm` package manager

### 2. Installation
```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### 3. Run Development Server
```powershell
npm run dev
```
Open `http://localhost:5173` in your browser.

> **Note**: Vite is configured to automatically proxy all `/api/*` requests directly to the FastAPI backend running at `http://localhost:8000`.

### 4. Build for Production
```powershell
npm run build
```
Production assets are generated in `dist/`.
