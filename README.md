# Zecpath Project

Django backend for the Zecpath hiring platform.

## Setup

```bash
git clone https://github.com/Aljotennis/Zecpath_Project.git
cd Zecpath_Project
python -m venv myenv
myenv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # then set your own SECRET_KEY
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Structure

- `core/` – models and shared code
- `services/` – business logic
- `utils/` – helper functions
- `zecpath_project/` – settings and URLs

## Branching

`main` (stable) ← `development` ← `feature/*`. Commits follow Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `chore:`).
