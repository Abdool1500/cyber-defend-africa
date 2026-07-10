# Unix Development Workflow

A quick reference for the shell commands you'll use most often while working
on this project, with examples specific to this codebase.

## Navigation

```
pwd                     # print current directory
ls -la                  # list files, including hidden ones, with details
cd apps/quizzes         # change directory
mkdir -p apps/newapp/migrations   # create nested directories
touch apps/newapp/__init__.py     # create an empty file
```

## Copying and moving

```
cp .env.example .env              # copy the env template to your local .env
mv old_name.py new_name.py        # rename/move a file
```

## Reading files

```
cat requirements.txt              # print a whole file
less docs/supabase-setup.md       # page through a long file (q to quit)
```

## Searching

```
grep -rn "SUPABASE_URL" apps/ config/     # find every reference to a setting
find . -name "*.py" -path "*/tests.py"    # find all test files
```

## Permissions

```
chmod +x scripts/setup.sh         # make a script executable
```

## Processes

```
ps aux | grep runserver           # find the running dev server process
kill <pid>                        # stop a process by its process id
```

## Networking

```
curl -i http://127.0.0.1:8000/healthz/     # check the health check endpoint
curl -i http://127.0.0.1:8000/api/v1/courses/
```

## Python & the virtual environment

```
python3 -m venv .venv             # create a virtual environment
source .venv/bin/activate         # activate it (deactivate to leave)
pip install -r requirements-dev.txt
python manage.py runserver
python manage.py test
```

## npm

```
npm install                       # install JS dependencies (Jest)
npm test                          # run the Jest suite
```

## Git

```
git status                        # see what's changed
git add apps/quizzes/models.py    # stage a specific file
git commit -m "Add quiz random rules"
git branch feature/certificates   # create a branch
git switch feature/certificates   # switch to it
git switch main
git merge feature/certificates    # merge a branch into the current one
git pull                          # fetch + merge from the remote
git push                          # push your branch to the remote
```

## psql (Supabase PostgreSQL)

Once `DATABASE_URL` is configured (see `docs/supabase-setup.md`), you can
connect directly with `psql` for one-off inspection — Django migrations
remain the source of truth for schema changes, this is read-only debugging:

```
psql "$DATABASE_URL"
\dt                                # list tables
\d courses_course                  # describe a table
SELECT count(*) FROM accounts_user;
\q
```

A note on destructive commands: this document intentionally does not cover
`rm -rf`, `git reset --hard`, or similar — those are documented in project
runbooks with explicit safeguards, not casually listed as everyday
reference commands.
