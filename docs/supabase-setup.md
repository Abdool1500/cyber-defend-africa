# Supabase Setup

This project uses Supabase for two things:

1. **Hosted PostgreSQL** — Django's ORM connects to it directly via
   `DATABASE_URL`. Django migrations are the only mechanism that creates or
   changes tables; never create the application's tables manually in the
   Supabase SQL editor.
2. **Storage** — private and public buckets for assignment submissions,
   avatars, course thumbnails, resource assets, and certificate assets, via
   `apps/core/services/storage.py`.

## 1. Create a Supabase project

Create a project at https://supabase.com. Note the project reference and the
database password you set — you'll need both below.

## 2. Configure the database connection

Open your Supabase project → **Project Settings → Database** and copy the
connection string. Supabase offers two connection modes:

- **Direct connection** (`db.<project-ref>.supabase.co:5432`) — use this for
  running migrations and for local development.
- **Pooled connection** (`<project-ref>.pooler.supabase.com:6543`, via
  PgBouncer) — use this for your production web process, since serverless/
  many-worker deployments can exhaust direct Postgres connections quickly.
  Note that PgBouncer in transaction-pooling mode does not support prepared
  statements the same way a direct connection does — if you hit issues,
  run migrations against the **direct** connection and point only the
  running web app at the **pooled** one.

Set it in `.env`:

```
DATABASE_URL=postgres://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres
DB_SSL_MODE=require
```

If `DATABASE_URL` is left blank, the app falls back to local SQLite — useful
for development before Supabase credentials are available, but not a
substitute for testing against real Postgres before deploying.

## 3. Run migrations

```
python manage.py migrate
```

Django creates every application table (`accounts_user`, `courses_course`,
`quizzes_quiz`, etc.) from its own migration files. Do not create these
tables by hand in the Supabase SQL editor — that will conflict with
Django's migration state.

Verify the tables landed correctly by checking **Table Editor** in the
Supabase dashboard, or via `psql "$DATABASE_URL"` → `\dt`.

## 4. Configure Storage credentials

From **Project Settings → API**, copy:

```
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_ANON_KEY=<anon-public-key>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
```

`SUPABASE_SERVICE_ROLE_KEY` is server-only — it bypasses row-level security
and must never appear in templates, JavaScript, client responses, or
version control. It's read once in `apps/core/services/storage.py` and
nowhere else in the codebase.

## 5. Create Storage buckets

Create these buckets from **Storage** in the Supabase dashboard:

| Bucket                  | Privacy |
|--------------------------|---------|
| `avatars`                 | private |
| `course-thumbnails`       | public  |
| `assignment-submissions`  | private |
| `resource-assets`         | public  |
| `certificate-assets`      | private |

These match `SUPABASE_STORAGE_BUCKETS` in `config/settings/base.py` — if you
rename a bucket, update that setting too.

## 6. Test an upload and a signed download

With credentials configured, use the Django shell to sanity-check the
storage service end-to-end:

```python
python manage.py shell
>>> from apps.core.services.storage import get_storage_service
>>> import io
>>> service = get_storage_service()
>>> service.upload("assignment-submissions", "test/hello.txt", io.BytesIO(b"hello"), "text/plain")
>>> service.signed_url("assignment-submissions", "test/hello.txt")
```

The signed URL should be time-limited and work in a browser; the same path
requested without a signature should not be publicly accessible, since the
bucket is private.

## Live verification checklist

Until real credentials are supplied, `apps/core/tests.py` covers the storage
service's validation logic and error handling with mocked Supabase
responses — those tests do **not** prove connectivity to a live project.
Once `DATABASE_URL` and the `SUPABASE_*` variables are set:

- [ ] `python manage.py migrate` runs cleanly against the live database
- [ ] Tables are visible in the Supabase Table Editor
- [ ] A record created via Django ORM (e.g. `seed_demo_data`) is visible in
      Supabase
- [ ] A file uploaded via `StorageService.upload()` appears in the bucket
- [ ] `StorageService.signed_url()` produces a working, time-limited link
- [ ] An unsigned request to a private bucket object is rejected

This checklist has not been run against a live project as part of this
build — no production Supabase credentials were provided. Everything above
it is verified with mocks and local SQLite.
