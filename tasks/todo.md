# Cyber Defend Africa LTD — Build Plan

Directory is currently empty (no git repo, no project files). This is a from-scratch build
of a Django + Supabase(PostgreSQL+Storage) + Bootstrap 5 + DRF platform, per the spec.

Given the size of the spec (100+ sections), this plan sequences work in priority order
(per spec section 113: a working secure core beats decorative marketing). Each phase will
be implemented, then briefly reported on, then checked off here. This is a multi-session
build — I will keep working through phases without stopping to ask "continue", but will
flag genuine blockers (e.g. missing Supabase credentials) as they come up and keep building
everything else around them.

## Phase 0 — Project scaffolding & tooling
- [x] `git init`, `.gitignore`, base repo layout
- [x] Python virtualenv + `requirements.txt` / `requirements-dev.txt`
- [x] Django project (`config/`) with split settings (base/development/production/test)
- [x] `apps/` package with all planned app skeletons registered
- [x] `.env.example` with all documented environment variables
- [x] `package.json` + `jest.config.js` scaffolding
- [x] Makefile with install/migrate/seed/run/test/test-js/check

## Phase 1 — Database & Storage configuration
- [x] `DATABASE_URL`-driven Supabase PostgreSQL config (env-based, SSL, no hardcoded creds)
- [x] `apps/core/services/storage.py` centralized Supabase Storage service (upload/delete/
      signed URLs/MIME+size validation) — mockable/testable without live credentials
- [x] Document pooled vs direct connection usage

## Phase 2 — Custom user model & auth (priority 1)
- [x] Custom user model (AbstractUser/AbstractBaseUser, UUID pk, role, status)
- [x] Registration (student-only public signup), login, logout, password reset/change
- [x] Role-based authorization helpers/mixins (student/instructor/admin/super_admin)
- [x] `create_initial_superadmin` management command

## Phase 3 — Courses & enrollment (priority 2)
- [x] Course, CourseModule, Lesson models + migrations
- [x] Enrollment, LessonProgress models (server-side progress calc)
- [x] InstructorAssignment model + enforcement
- [x] Seed command with 3 flagship courses + modules/lessons

## Phase 4 — Question Bank (priority 3)
- [x] Question, QuestionOption models (MC/multi-select/T-F/short-answer)
- [x] Instructor Question Bank UI: list/search/filter/pagination/CRUD/duplicate/archive
- [x] Historical-safety strategy for edited questions

## Phase 5 — Quiz builder, attempts, grading (priorities 4-6)
- [x] Quiz, QuizQuestion, QuizRandomRule models
- [x] Quiz builder UI (manual + random rules)
- [x] QuizAttempt, AttemptQuestion, QuizAnswer models
- [x] Secure attempt start (transaction.atomic, frozen question set/order)
- [x] Student quiz-taking UI: timer, navigator, autosave (JS modules), submit
- [x] Server-side grading service (MC/multi-select/T-F auto, short-answer manual)
- [x] Correct-answer leakage protection (serializers/views/API)

## Phase 6 — Assignments & private Storage (priorities 7-9)
- [x] Assignment, AssignmentSubmission models
- [x] Instructor create/publish; enrolled-only student access
- [x] Secure file submission to private Supabase Storage bucket (signed URLs)
- [x] Instructor grading UI

## Phase 7 — Feedback (priorities 10-11)
- [x] StudentFeedback model with rating CheckConstraints
- [x] Student submission UI (enrolled courses only)
- [x] Instructor/management views with anonymity protection
- [x] Analytics + CSV/PDF export (priority 12)

## Phase 8 — Dashboards (priorities 13-15)
- [x] Student dashboard (overview, courses, quizzes, assignments, feedback, certificates,
      notifications, progress, profile, security)
- [x] Instructor dashboard (overview, courses, students, question bank, quizzes,
      assignments, grading, feedback, analytics, announcements)
- [x] Management dashboard (users, courses, enrollments, requests, reports, audit logs)
- [x] Django Admin registration for core models

## Phase 9 — Certificates, notifications, reports, audit
- [x] Certificate model + PDF generation (ReportLab) + public verification route
- [x] Notification/Announcement models + UI
- [x] Reports (enrollment/progress/quiz/feedback/certificate/lead) CSV+PDF
- [x] AuditLog model + logging of sensitive actions

## Phase 10 — REST API
- [x] DRF setup, versioned `/api/v1/` endpoints per spec
- [x] Custom permissions (IsStudent/IsInstructor/IsAdmin/IsEnrolledStudent/etc.)
- [x] drf-spectacular schema + docs routes

## Phase 11 — Public marketing site (priority 16 — last)
- [x] Homepage, About, Solutions, GPT Sentinel, Services, Academy, 3 course pages
- [x] Career path assessment (JS scoring + Jest tests)
- [x] Contact/Demo/Pilot/Consultation request forms, Resources/blog, Newsletter
- [x] Google Form waitlist integration (env-driven, graceful fallback)
- [x] Legal pages, error pages (400/403/404/500), SEO basics

## Phase 12 — Testing, CI, docs
- [x] Python tests covering security/permission-critical flows (spec section 86 + 112)
- [x] Jest tests (timer, navigator, autosave, waitlist, career assessment, form helpers)
- [x] GitHub Actions CI (`ci.yml`), issue/PR templates
- [x] `docs/unix-development.md`, `docs/supabase-setup.md`, README, CONTRIBUTING, SECURITY

## Phase 13 — Final verification
- [x] `python manage.py check`
- [x] `python manage.py makemigrations --check`
- [x] `python manage.py test`
- [x] `npm test`
- [x] Sweep for TODO/FIXME/pass/"Coming Soon"/href="#"/placeholder in core features
- [x] Final report per spec section 110

---

## Notes on blockers
- No live Supabase project credentials exist yet. I'll build against `DATABASE_URL`/env
  vars so it works once you supply them, and keep local dev running on a normal Postgres/
  SQLite fallback for tests. I'll flag this again when we reach Phase 1 setup, but will not
  stop building because of it.
- No Google Form URL yet — waitlist button will be env-driven and gracefully disabled with
  a dev-mode hint until you provide `WAITLIST_FORM_URL`.

## Review

### What was built

A working Django 5.1 + DRF + Bootstrap 5 platform for Cyber Defend Africa
LTD, covering the full role-based learning platform (public marketing site,
student/instructor/management dashboards, Question Bank, Quiz engine with
secure grading, Assignments with private Supabase Storage, Feedback with
anonymity protection, Certificates, Notifications, Audit logging, and a
REST API), plus tests, CI, and docs. See `README.md` for the full picture
and `docs/supabase-setup.md` / `docs/unix-development.md` for setup.

### Verification performed

- `python manage.py check` — passes
- `python manage.py makemigrations --check` — no missing migrations
- `python manage.py test` — 61/61 passing (role boundaries, quiz grading
  for all 4 question types, attempt security, feedback anonymity/duplicate
  policy, assignment isolation/score-cap, certificate verification, storage
  service validation with mocked Supabase calls)
- `npm test` — 39/39 passing (quiz timer, question navigator, autosave,
  waitlist URL validation, career assessment scoring, form helpers)
- A scripted end-to-end run (not just unit assertions) drove real
  instructor→student→instructor workflows through the Django test Client:
  create question → build quiz → publish → student attempt → autosave →
  submit → auto-grade → manual grade short answer → finalize; and
  instructor create/publish assignment → student submit → instructor
  grade → student sees grade; and student submit feedback → instructor
  sees anonymized view → CSV/PDF export redacts identity.
- A full crawl of all 122 zero-argument URL patterns × 4 roles (488
  requests) found and fixed one real bug (see below) and confirmed zero
  500-level responses afterward.

### Bugs found and fixed during verification (not just written, actually caught by testing)

1. `QuestionForm` used `instance.pk` to detect "is this a new record" —
   always true for UUID-default primary keys, so creating a question via
   the instructor UI crashed. Fixed to check `course_id` instead.
2. `save_answer()` compared string option ids (from the JSON payload)
   against a set of UUID objects, so every selected quiz answer was
   silently dropped — multiple-choice/select/true-false questions always
   scored 0 regardless of what the student picked. Fixed to compare as
   strings.
3. `option_order_snapshot` (JSONField) stored raw UUID objects, which
   crashed on `json.dumps` at attempt-start. Fixed to store strings, with
   matching lookups on the read side.
4. `core:post_login_redirect` referenced `student:overview` /
   `instructor:overview`, but the actual registered namespaces are
   `student_dashboard` / `instructor_dashboard` — login would 500 for
   every student/instructor. Found via a full URL crawl, fixed, and
   locked in with a regression test.
5. A genuine Django 5.1 / Python 3.14 incompatibility
   (`BaseContext.__copy__` relies on a `copy(super())` idiom that no
   longer produces a valid object) broke *every* template-rendering
   response captured by Django's test Client, masking real test failures
   behind a recursive exception-handling crash. Patched in
   `apps/core/apps.py` with a comment explaining why, since this is an
   upstream bug, not application code.
6. Manifest-based static storage (`CompressedManifestStaticFilesStorage`)
   requires a `collectstatic` run to build its manifest, which broke every
   `{% static %}` reference in tests/dev. Restricted the manifest storage
   to production only.

### Known limitations / not done

- No live Supabase project is connected — `DATABASE_URL` and the
  `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_ROLE_KEY` are blank in `.env`.
  `SUPABASE_URL` and `WAITLIST_FORM_URL` were provided and are set. The app
  runs on local SQLite until the database/storage credentials are
  supplied — see `docs/supabase-setup.md`'s live-verification checklist,
  which has not been run against a real project.
- The management dashboard has a working overview (platform stats) but
  relies on Django Admin for full CRUD screens on individual records
  (users, courses, enrollments, leads, resources, audit logs) rather than
  dedicated custom pages for each.
- Resources/blog has no seeded content (model + list/detail views work,
  just no sample posts).
- No automated linting is wired into CI beyond Django's own checks.
- Browser-driven (Playwright/Selenium-style) verification was not
  performed — all end-to-end verification used the Django test Client,
  which exercises the real view/template/permission/database stack but
  not actual browser JS execution. The JS modules (timer, navigator,
  autosave, career assessment, waitlist, form helpers) are unit-tested
  under Jest but not exercised in a live browser DOM in this session.
