# Weekly Activities - Django site

Simple Django app: admin creates accounts + weekly activities (each with
its own max spots), users log in, enroll/leave activities, and see their
score.

## How it's organized

```
weeklysite/
    manage.py
    weeklysite/          <- project settings, urls
    activities/          <- the actual app
        models.py        <- Activity, Enrollment, Profile (score)
        admin.py          <- admin panel setup (create accounts/activities here)
        views.py          <- activity list, enroll, unenroll, my score
        urls.py
        templates/activities/   <- your pages
        templates/registration/login.html
    static/activities/style.css  <- swap this for your own CSS
```

## First-time setup

```bash
cd weeklysite
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser   # this is YOU, the admin
python manage.py runserver
```

Then open:
- http://127.0.0.1:8000/admin/  -> log in as the superuser you created.
  This is where you:
  - Create user accounts (Users -> Add user). Each new user automatically
    gets a "Profile" with a score, editable right there.
  - Create Activities (name, description, week date, max_participants).
  - See/add/remove who's enrolled in an activity directly on its admin page.
  - Edit anyone's score from their user edit page.

- http://127.0.0.1:8000/  -> the regular user-facing site. Log in with any
  account you created, see the list of activities, enroll/leave, and
  check "My Score".

## Plugging in your existing HTML/CSS

The templates live in `activities/templates/activities/`:
- `base.html` — shared layout (nav bar + messages), extend this
- `activity_list.html` — the activity grid + enroll/leave buttons
- `my_score.html` — score + enrollments
- `registration/login.html` — login form

They currently link to `static/activities/style.css` as a placeholder.
Easiest path: drop your own CSS file in `static/activities/`, update the
`{% static %}` link in `base.html`, and adjust class names in the
templates to match your markup. The Django logic doesn't care about
styling at all — it just renders whatever's in these template files.

## Notes / things you'll likely want to tweak

- **No public signup** — only the admin panel creates accounts, per your spec.
- **Score** is a plain manual number the admin sets per user (Users -> edit
  user -> Profile section). If you want auto-scoring later (e.g. +1 per
  activity), that logic would go in `views.py`'s `enroll` view.
- **Enrollment cap** is per-activity (`max_participants` field) — set it to
  3, 4, or anything else when creating each Activity.
- Change `SECRET_KEY` and set `DEBUG = False` + proper `ALLOWED_HOSTS` in
  `weeklysite/settings.py` before deploying anywhere public.
