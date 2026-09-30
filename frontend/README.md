# PolarGrid AI - Frontend

Frontend for the PolarGrid AI smart energy management system.
Built with React, Vite, TypeScript, Tailwind CSS, and Recharts.

## Setup

1. Make sure you are in the `frontend` directory.
2. Install dependencies:
   ```bash
   npm install
   ```

3. Environment setup:
   Copy `.env.example` to `.env` (it will use `http://localhost:8000` by default).

   ```env
   VITE_API_URL=http://localhost:8000
   VITE_USE_MOCK=false
   ```
   If the backend is not available, set `VITE_USE_MOCK=true` to view the UI with demo data.

4. Run the development server:
   ```bash
   npm run dev
   ```

5. Open your browser and navigate to `http://localhost:5173`.
