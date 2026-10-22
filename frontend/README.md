# PaperPicks frontend

This directory contains the React/Vite frontend, including the login mockup in
`src/App.jsx`.

## Run locally

From the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (usually `http://localhost:5173`) in a
browser. Vite's hot-module reloading will update the page as you edit files in
`src/`.

## Check frontend changes

Run the linter:

```powershell
cd frontend
npm run lint
```

Create a production build:

```powershell
cd frontend
npm run build
```

To preview the production build locally:

```powershell
cd frontend
npm run preview
```

The current login is intentionally a frontend-only mockup. The buttons and
form display feedback, but no credentials are sent to the backend yet.
