# Session preferences

- Do not start the frontend or backend development servers for this project; the user starts and stops them manually.
- The frontend API proxy must target `http://127.0.0.1:8000`.
- Use Node.js `22.23.3` for the frontend (`nvm use 22.23.3` on Windows before `npm run dev`).

## Custom Codex agents

- `.codex/agents/backend-dev.toml` defines the reusable `backend_dev` profile for FastAPI work in `app/`.
- `.codex/agents/frontend-dev.toml` defines the reusable `frontend_dev` profile for Vue work in `frontend/`.
- Select the matching profile when delegating project work. These files persist the roles and instructions across sessions; an individual running subagent/session itself does not persist between sessions.
