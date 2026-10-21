# Agent role persistence

The original role definitions are in `C:\Users\Playdata\PycharmProjects\AI02\.codex\agents\`:

- `backend-dev.toml`: intended backend developer for the app's FastAPI project. Match the existing project structure.
- `frontend-dev.toml`: Vue frontend developer. Check any design guide first; organize work around `api`, `assets`, `components`, `router`, `stores`, and `views`; use axios for backend calls.

## Session handling

The collaboration agents instantiated for the 2026-10-20 session are `backend_dev` and `frontend_dev`. Collaboration agents are session-scoped; a later session must instantiate agents again from the role definitions. Keep this file as the durable reminder of the roles and their source.

For frontend work, current project instructions take precedence over the older frontend role text: keep the API proxy target at `http://127.0.0.1:8000`, use Node.js `22.23.3`, and do not start frontend or backend servers.

## Source definition issues

- `backend-dev.toml` sets `name = "frontend_dev"`, duplicating the frontend role name.
- Both definitions contain `model = "gpt-=5.6-Luna"` and the misspelled key `modle_reasoning_effort`.
- The original files are outside this frontend workspace's writable root. They were left unchanged. Review and correct those fields in the source definitions if Codex must load them as native agent configuration.
