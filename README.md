# WindWise UK: Day-Ahead Wind Forecast & Accuracy Dashboard

A full-stack UK electricity day-ahead wind generation forecast and accuracy verification dashboard built for the Gridbricks technical assignment.

---

## Architecture Overview

```
c:\Projects\WindWiseUK\
├── backend\
│   ├── .venv\                     # Isolated Python virtual environment
│   ├── app\
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app & CORS configuration
│   │   ├── config.py              # Environment settings & allowed origins
│   │   ├── schemas.py             # Pydantic request/response models
│   │   ├── dependencies.py        # Shared dependency providers
│   │   ├── client.py              # Elexon Insights Solution (BMRS API v1) client
│   │   ├── cache.py               # SQLite caching layer for high performance
│   │   ├── processing.py          # Day-ahead cutoff matching & hourly alignment
│   │   ├── metrics.py             # Accuracy engine (MAE, RMSE, Bias, WAPE)
│   │   └── routes\
│   │       ├── health.py          # GET /api/health
│   │       ├── metrics_routes.py  # GET /api/summary, GET /api/metrics
│   │       └── timeseries_routes.py # GET /api/timeseries, GET /api/forecast-evolution
│   ├── tests\
│   │   ├── conftest.py            # Isolated fixtures & synthetic data
│   │   ├── test_metrics.py        # Mathematical formula tests
│   │   ├── test_processing.py     # Cutoff enforcement & resolution tests
│   │   └── test_api.py            # Endpoint & error-handling tests
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Python 3.13-slim container definition
│   ├── .dockerignore              # Backend Docker ignore rules
│   ├── .env.example               # Example backend configuration
│   ├── windwise_cache.db          # Embedded SQLite cache (local dev)
│   ├── verify_live_january.py     # Live verification script
│   └── verify_frontend_integration.py # Live integration test
├── frontend\
│   ├── src\
│   │   ├── components\
│   │   │   ├── Header.tsx         # Header, brand & live status badges
│   │   │   ├── FilterBar.tsx      # Date range, quick presets & cutoff selector
│   │   │   ├── KpiCards.tsx       # MAE, RMSE, Bias, WAPE, GWh & quality cards
│   │   │   ├── TimeseriesChart.tsx # 24h Actual vs Forecast area chart
│   │   │   ├── ErrorChart.tsx     # Hourly forecast error delta bar chart
│   │   │   ├── DailyAccuracyView.tsx # 31-day MAE/WAPE bar chart & interactive table
│   │   │   ├── ForecastEvolutionView.tsx # Multi-cutoff gate closure comparison
│   │   │   └── MethodologyPanel.tsx # Resolution, UTC & market methodology
│   │   ├── services\
│   │   │   └── api.ts             # Typed API service client
│   │   ├── types\
│   │   │   └── index.ts           # TypeScript interfaces matching backend
│   │   ├── App.tsx                # Main dashboard coordinator
│   │   ├── index.css              # Custom energy-analytics design system
│   │   └── main.tsx               # React entrypoint
│   ├── Dockerfile                 # Multi-stage build (Node 22 -> Nginx Alpine)
│   ├── nginx.conf                 # Nginx SPA routing & /api/ reverse proxy
│   ├── vercel.json                # Vercel SPA client rewrite routing
│   ├── .dockerignore              # Frontend Docker ignore rules
│   ├── .env.example               # Frontend environment template
│   ├── .env                       # Local frontend environment
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docker-compose.yml             # Orchestration for frontend & backend
├── .gitignore                     # Root Git exclusions
└── README.md
```

---

## Quickstart Guide for Windows Terminal (PowerShell)

### 1. Run the FastAPI Backend
Open PowerShell in `c:\Projects\WindWiseUK\backend` and run:
```powershell
.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```
* **API Server:** `http://localhost:8000`
* **Interactive Swagger UI:** `http://localhost:8000/docs`
* **Health Check:** `http://localhost:8000/api/health`

### 2. Run the React Frontend
Open a second PowerShell window in `c:\Projects\WindWiseUK\frontend` and run:
```powershell
npm run dev -- --host 127.0.0.1 --port 5173
```
* **Dashboard URL:** `http://127.0.0.1:5173`

### 3. Run Backend Automated Tests
From the root directory `c:\Projects\WindWiseUK`:
```powershell
backend\.venv\Scripts\pytest -v backend\tests
```
*(All 16 unit and integration tests execute against deterministic synthetic fixtures).*

### 4. Build the Frontend for Production
From `c:\Projects\WindWiseUK\frontend`:
```powershell
npm run build
```
*(Runs TypeScript validation and compiles static bundle into `frontend/dist/`).*

### 5. Verify Live Integration
```powershell
backend\.venv\Scripts\python backend\verify_frontend_integration.py
```
*(Tests both the Vite frontend server and all backend API routes simultaneously).*

---

## Docker Containerization (Phase 3A)

WindWise UK is fully containerized with Docker and Docker Compose for production-grade local execution, isolated environments, and simplified deployment.

### Development vs Production Mode

| Dimension | Local Development Mode | Containerized Production Mode |
| :--- | :--- | :--- |
| **Frontend Runtime** | Vite HMR dev server on port `5173` | Multi-stage build served by Nginx on port `3000` |
| **Backend Runtime** | Uvicorn reload on port `8000` | FastAPI on Python 3.13-slim (`0.0.0.0:8000`) with non-root user `appuser` |
| **API Networking** | Direct HTTP to `http://localhost:8000` via CORS | Nginx reverse-proxies `/api/` to `http://backend:8000/api/` (no CORS needed) |
| **Client-Side Routing** | Vite development server middleware | Nginx `try_files $uri $uri/ /index.html;` (SPA refresh support) |
| **Cache Database** | `backend/windwise_cache.db` on host disk | Named persistent volume `windwise_backend_data` mapped to `/app/data/windwise_cache.db` |

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on Windows with the WSL 2 backend enabled.
- Ensure Docker Desktop is running before executing commands.

### Start Containers
From the project root `c:\Projects\WindWiseUK`:
```powershell
docker compose up --build -d
```
* **Frontend Web Application:** [http://localhost:3000](http://localhost:3000)
* **Backend Direct API:** [http://localhost:8000](http://localhost:8000)
* **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Backend Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health)
* **Frontend Proxy Health Check:** [http://localhost:3000/api/health](http://localhost:3000/api/health)

### Health Status & Logs
```powershell
# View running containers and health status
docker compose ps

# View live container logs
docker compose logs -f

# View specific service logs
docker compose logs backend
docker compose logs frontend
```

### Pre-Seeding the Persistent Cache Volume
The backend automatically fetches data on-demand from the official Elexon API when queried. To pre-populate the named Docker volume with complete January 2026 data upfront:
```powershell
docker compose exec backend python verify_live_january.py
```
*(Fetches 1,488 actual records and 18,688 forecast records into `/app/data/windwise_cache.db`).*

### Stop Containers
```powershell
# Stop running containers (preserves volume data)
docker compose stop

# Stop and remove containers and network (preserves volume data)
docker compose down

# Stop and wipe persistent volume data completely
docker compose down -v
```

### Troubleshooting
1. **Port 8000 or 3000 Conflict**:
   If another application (such as local Uvicorn or another Node app) is using port 8000 or 3000, find the PID and stop it:
   ```powershell
   netstat -ano | findstr :8000
   netstat -ano | findstr :3000
   ```
2. **Container Healthcheck Inspection**:
   Both services include automated container health checks:
   - Backend: Python-native check hitting `http://localhost:8000/api/health`.
   - Frontend: `wget -q --spider http://127.0.0.1:80/`.
   Inspect detailed health logs with:
   ```powershell
   docker inspect --format="{{json .State.Health}}" windwise-backend
   docker inspect --format="{{json .State.Health}}" windwise-frontend
   ```
3. **Database File Permissions**:
   The backend container runs as non-root user `appuser` (UID 1000). The Dockerfile creates `/app/data` with ownership assigned to `appuser`, ensuring persistent SQLite operations succeed without permission errors.

---

## Cloud Deployment Guide (Phase 3B: Render & Vercel)

WindWise UK is architected for independent, zero-downtime deployment:
- **Backend**: FastAPI web service hosted on [Render](https://render.com) (or compatible Python cloud platform).
- **Frontend**: React + TypeScript SPA hosted on [Vercel](https://vercel.com).
- **Data Source**: Live official Elexon Insights Solution (BMRS) API.

```
       +-----------------------+              +------------------------------+
       |   Vercel Edge CDN     |              |     Render Web Service       |
       |  (React 19 + Vite)    |  HTTPS CORS  |      (FastAPI + SQLite)      |
       | https://...vercel.app | -----------> | https://...onrender.com      |
       +-----------------------+              +------------------------------+
                                                              |
                                                              | HTTPS Stream
                                                              v
                                              +------------------------------+
                                              |      Official Elexon         |
                                              |     BMRS Data API v1         |
                                              +------------------------------+
```

### Recommended Deployment Sequence
To prevent broken API calls and chicken-and-egg configuration loops, always deploy the **Backend first**, then the **Frontend second**:

1. Deploy the backend on Render to receive its public HTTPS URL (e.g. `https://windwise-backend.onrender.com`).
2. Test backend `/api/health` directly in your browser.
3. Deploy the frontend on Vercel with `VITE_API_BASE_URL` set to that Render URL.
4. Add the resulting Vercel URL to `ALLOWED_ORIGINS` in Render to lock down CORS.

---

### Step 1: Backend Deployment on Render

#### Service Configuration
1. Create a new **Web Service** on Render and connect your GitHub repository.
2. Select **Native Python** environment (or Docker if preferred).
3. Configure settings:
   - **Name**: `windwise-backend` (or your preferred slug)
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

*(Note: If deploying via Render's Docker runtime instead of Native Python, the backend `Dockerfile` automatically resolves `${PORT:-8000}`).*

#### Backend Environment Variables

| Variable Name | Required | Example Safe Value | Purpose |
| :--- | :---: | :--- | :--- |
| `ALLOWED_ORIGINS` | Yes | `https://your-windwise-app.vercel.app` | Comma-separated list of allowed frontend URLs for CORS. |
| `ELEXON_BASE_URL` | No | `https://data.elexon.co.uk/bmrs/api/v1` | Official Elexon BMRS endpoint (defaults to this value). |
| `ELEXON_TIMEOUT_SECONDS` | No | `30.0` | HTTP request timeout for large streaming datasets. |
| `CACHE_DB_PATH` | No | `./windwise_cache.db` | SQLite database location (see persistence options below). |
| `PORT` | Auto | *10000* | Automatically assigned by Render. |

#### SQLite Cache Persistence Considerations
Render provides two architectural choices for SQLite cache storage:
- **Approach A (Persistent Disk — Recommended for Production)**:
  - Attach a persistent disk on Render (e.g. 1 GB mounted at `/var/data`).
  - Set `CACHE_DB_PATH=/var/data/windwise_cache.db`.
  - Data downloaded from Elexon survives all service redeployments, restarts, and sleep cycles.
- **Approach B (Ephemeral Storage — Free Tier Compatible)**:
  - Keep default `CACHE_DB_PATH=./windwise_cache.db` (no persistent disk attached).
  - The application's built-in `ensure_data_loaded()` self-heals by downloading January 2026 data on-demand from the official Elexon API on the first user query.
  - Understand that when the instance restarts or redeploys, the local cache is reset and will be downloaded again on the next query.

#### Verification
Once Render finishes deploying, verify the backend directly in your browser:
- Health check: `https://<your-render-service>.onrender.com/api/health` (should return JSON with `"status": "ok"`).
- Interactive OpenAPI Docs: `https://<your-render-service>.onrender.com/docs`.

---

### Step 2: Frontend Deployment on Vercel

#### Project Configuration
1. Create a **New Project** on Vercel and import your GitHub repository.
2. Configure settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (or default `vite build`)
   - **Output Directory**: `dist`

#### Frontend Environment Variables

| Variable Name | Required | Example Safe Value | Purpose |
| :--- | :---: | :--- | :--- |
| `VITE_API_BASE_URL` | Yes | `https://<your-render-service>.onrender.com` | Public URL of your deployed Render backend (no trailing slash). |

> **Important:** In Vite, `import.meta.env.VITE_API_BASE_URL` is baked into static assets during `npm run build`. You must set this variable in Vercel **before** triggering the initial build.

#### SPA Routing Support (`vercel.json`)
The repository includes `frontend/vercel.json`:
```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```
This guarantees direct browser navigation and page refreshes work smoothly on Vercel without 404 errors, while letting Vercel serve bundled static assets from `dist/assets/` directly.

---

### Step 3: Complete CORS Setup
Once Vercel deploys your frontend:
1. Copy the assigned production domain (e.g. `https://windwise-uk.vercel.app`).
2. Go to your Render Web Service $\rightarrow$ **Environment**.
3. Set `ALLOWED_ORIGINS=https://windwise-uk.vercel.app`.
4. Render automatically redeploys with the locked-down CORS origin.

---

### Hosting Provider Limitations & Free-Tier Checklist

> [!NOTE]
> Please verify current provider terms and quotas directly with your chosen hosting platform:

1. **Render Free-Tier Spin-Down (Cold Starts)**:
   - Free Web Services spin down after 15 minutes of inactivity.
   - The first request to a sleeping instance typically takes ~30–50 seconds while Render provisions the container. Once active, responses return in milliseconds.
   - Free tier includes 750 free instance hours/month.
2. **Render Persistent Disks**:
   - Free Web Services do not support persistent disks. If running on the Free tier, use **Approach B** (ephemeral storage with on-demand Elexon downloading).
   - Upgrading to a paid instance ($7/mo Starter) is required if a persistent disk ($0.25/GB/mo) is needed.
3. **Vercel Hobby Tier**:
   - Generous free tier includes 100 GB bandwidth and automated HTTPS certificates. Fully sufficient for this take-home project.
4. **Local Docker Distinction**:
   - `docker-compose.yml` is maintained strictly for local grading, testing, and containerized development. It is not used for Vercel/Render deployments.

---

## Key Dashboard Features

1. **Header & Live Health Monitor**: Displays real-time API connectivity and cached Elexon records count.
2. **Analysis Filter Controls**:
   - Date range selector (default: Jan 1–31, 2026) with quick preset pills (Full Month, Weeks 1–4, Focus Days).
   - Day-Ahead Decision Cutoff selector (`09:00`, `11:00`, `12:00`, `14:00`, `17:00` UTC on day $D-1$) with strict no-lookahead filtering.
3. **KPI Metrics Cards**:
   - **MAE**: Mean Absolute Error (MW).
   - **RMSE**: Root Mean Square Error (MW).
   - **Forecast Bias**: Mean error with contextual **Overforecasting** (amber) and **Underforecasting** (violet) badges.
   - **WAPE**: Weighted Absolute Percentage Error (%) avoiding calm-period division by zero.
   - **Total Generation Volume**: Actual vs Forecast (GWh).
   - **Data Quality**: Matched observation hours (744/744) and missing record auditing.
4. **Day-Ahead Forecast vs Actual Generation Chart**:
   - Dual-line/area Recharts visual showing 24-hour metered outturn vs selected forecast.
   - Date navigator (Previous/Next day buttons and date picker).
   - Tooltip displaying the exact forecast publication timestamp.
5. **Forecast Error Distribution Chart**:
   - Hourly error bars ($F_i - A_i$) with a zero-error dashed reference line.
6. **Daily Accuracy Breakdown & Interactive Log**:
   - Bar chart toggleable between Daily MAE (MW) and Daily WAPE (%).
   - Interactive table: Clicking any day row instantly syncs the 24-hour hourly inspection chart!
7. **Forecast Evolution Across Gate Closures**:
   - Multi-line curve demonstrating how forecasts adjusted as gate closure progressed from 09:00 to 17:00 on day $D-1$.
8. **Methodology & Compliance Specifications**:
   - Explicit documentation of half-hourly actual averaging, hourly forecast alignment, UTC standardization, and market trading disclaimers.

---

## Verified January 2026 Accuracy Metrics (12:00 UTC Cutoff Baseline)

| Metric | Verified Value | Interpretation |
| :--- | :--- | :--- |
| **Total Evaluation Window** | **744 Hours** | 31 days $\times$ 24 hours (100% complete coverage) |
| **Mean Actual Generation** | **11,580.74 MW** | Average metered wind generation across Great Britain |
| **Mean Forecast Generation** | **13,386.97 MW** | Average National Grid ESO day-ahead forecast |
| **MAE** | **2,017.92 MW** | Mean absolute error |
| **RMSE** | **2,477.04 MW** | Root mean square error |
| **Forecast Bias** | **+1,806.23 MW (+15.60%)** | Systematic overforecasting during Jan 2026 |
| **WAPE** | **17.42%** | Weighted absolute percentage error |
| **Total Energy Outturn** | **8,616.07 GWh** | Total metered wind energy delivered to GB grid |
