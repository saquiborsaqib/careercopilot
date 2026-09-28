# AI CareerPilot — Frontend

React + Vite + Tailwind CSS dashboard for the AI CareerPilot platform.

## Setup

```bash
npm install
cp .env.example .env     # set VITE_API_BASE_URL if the backend isn't on 127.0.0.1:8000
npm run dev
```

Opens at `http://localhost:5173`. The backend must be running (see the repo root README) for
login/register and every data-fetching page to work.

## Structure

```
src/
├── api/           axios client (auth-token interceptor) + one function per backend endpoint
├── context/       AuthContext — token/user/profile state, login/register/logout
├── components/    Layout (sidebar nav), ProtectedRoute, shared Card/Badge/Button/ScoreRing
├── pages/         one page per feature area (Dashboard, Profile, Skills, Careers, Roadmap,
│                  Resume, Interview, Opportunities, Recommendations, ...)
└── App.jsx        route table
```

## Build

```bash
npm run build     # outputs to dist/
npm run preview   # serve the production build locally
```
