# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Run Commands
- Frontend: `npm run dev` (development), `npm run build` (production)
- Backend: `python src/backend/run.py` (start FastAPI server)
- Tests: No test framework configured yet

## Code Style Guidelines
### Python
- Imports: standard library → third-party → local imports
- Type annotations required for all function parameters and return values
- Snake_case for variables/functions, PascalCase for classes
- Docstrings use triple quotes with param/return documentation
- Error handling with try/except blocks or context managers

### JavaScript/React
- ES6+ syntax with functional components and hooks
- Component files use PascalCase (CardGroup.jsx)
- Variables/functions use camelCase
- JSX indentation: 2 spaces
- React component props should be documented with comments

### Git Commit Messages
- Format: `<Type>: <제목>` (Title under 50 chars, no period)
- Types: Feat, Fix, Docs, Refactor, Test, Chore
- Use Korean or English consistently within a commit