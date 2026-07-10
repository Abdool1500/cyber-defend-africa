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
- [ ] `git init`, `.gitignore`, base repo layout
- [ ] Python virtualenv + `requirements.txt` / `requirements-dev.txt`
- [ ] Django project (`config/`) with split settings (base/development/production/test)
- [ ] `apps/` package with all planned app skeletons registered
- [ ] `.env.example` with all documented environment variables
- [ ] `package.json` + `jest.config.js` scaffolding
- [ ] Makefile with install/migrate/seed/run/test/test-js/check

## Phase 1 — Database & Storage configuration
- [ ] `DATABASE_URL`-driven Supabase PostgreSQL config (env-based, SSL, no hardcoded creds)
- [ ] `apps/core/services/storage.py` centralized Supabase Storage service (upload/delete/
      signed URLs/MIME+size validation) — mockable/testable without live credentials
- [ ] Document pooled vs direct connection usage

## Phase 2 — Custom user model & auth (priority 1)
- [ ] Custom user model (AbstractUser/AbstractBaseUser, UUID pk, role, status)
- [ ] Registration (student-only public signup), login, logout, password reset/change
- [ ] Role-based authorization helpers/mixins (student/instructor/admin/super_admin)
- [ ] `create_initial_superadmin` management command

## Phase 3 — Courses & enrollment (priority 2)
- [ ] Course, CourseModule, Lesson models + migrations
- [ ] Enrollment, LessonProgress models (server-side progress calc)
- [ ] InstructorAssignment model + enforcement
- [ ] Seed command with 3 flagship courses + modules/lessons

## Phase 4 — Question Bank (priority 3)
- [ ] Question, QuestionOption models (MC/multi-select/T-F/short-answer)
- [ ] Instructor Question Bank UI: list/search/filter/pagination/CRUD/duplicate/archive
- [ ] Historical-safety strategy for edited questions

## Phase 5 — Quiz builder, attempts, grading (priorities 4-6)
- [ ] Quiz, QuizQuestion, QuizRandomRule models
- [ ] Quiz builder UI (manual + random rules)
- [ ] QuizAttempt, AttemptQuestion, QuizAnswer models
- [ ] Secure attempt start (transaction.atomic, frozen question set/order)
- [ ] Student quiz-taking UI: timer, navigator, autosave (JS modules), submit
- [ ] Server-side grading service (MC/multi-select/T-F auto, short-answer manual)
- [ ] Correct-answer leakage protection (serializers/views/API)

## Phase 6 — Assignments & private Storage (priorities 7-9)
- [ ] Assignment, AssignmentSubmission models
- [ ] Instructor create/publish; enrolled-only student access
- [ ] Secure file submission to private Supabase Storage bucket (signed URLs)
- [ ] Instructor grading UI

## Phase 7 — Feedback (priorities 10-11)
- [ ] StudentFeedback model with rating CheckConstraints
- [ ] Student submission UI (enrolled courses only)
- [ ] Instructor/management views with anonymity protection
- [ ] Analytics + CSV/PDF export (priority 12)

## Phase 8 — Dashboards (priorities 13-15)
- [ ] Student dashboard (overview, courses, quizzes, assignments, feedback, certificates,
      notifications, progress, profile, security)
- [ ] Instructor dashboard (overview, courses, students, question bank, quizzes,
      assignments, grading, feedback, analytics, announcements)
- [ ] Management dashboard (users, courses, enrollments, requests, reports, audit logs)
- [ ] Django Admin registration for core models

## Phase 9 — Certificates, notifications, reports, audit
- [ ] Certificate model + PDF generation (ReportLab) + public verification route
- [ ] Notification/Announcement models + UI
- [ ] Reports (enrollment/progress/quiz/feedback/certificate/lead) CSV+PDF
- [ ] AuditLog model + logging of sensitive actions

## Phase 10 — REST API
- [ ] DRF setup, versioned `/api/v1/` endpoints per spec
- [ ] Custom permissions (IsStudent/IsInstructor/IsAdmin/IsEnrolledStudent/etc.)
- [ ] drf-spectacular schema + docs routes

## Phase 11 — Public marketing site (priority 16 — last)
- [ ] Homepage, About, Solutions, GPT Sentinel, Services, Academy, 3 course pages
- [ ] Career path assessment (JS scoring + Jest tests)
- [ ] Contact/Demo/Pilot/Consultation request forms, Resources/blog, Newsletter
- [ ] Google Form waitlist integration (env-driven, graceful fallback)
- [ ] Legal pages, error pages (400/403/404/500), SEO basics

## Phase 12 — Testing, CI, docs
- [ ] Python tests covering security/permission-critical flows (spec section 86 + 112)
- [ ] Jest tests (timer, navigator, autosave, waitlist, career assessment, form helpers)
- [ ] GitHub Actions CI (`ci.yml`), issue/PR templates
- [ ] `docs/unix-development.md`, `docs/supabase-setup.md`, README, CONTRIBUTING, SECURITY

## Phase 13 — Final verification
- [ ] `python manage.py check`
- [ ] `python manage.py makemigrations --check`
- [ ] `python manage.py test`
- [ ] `npm test`
- [ ] Sweep for TODO/FIXME/pass/"Coming Soon"/href="#"/placeholder in core features
- [ ] Final report per spec section 110

---

## Notes on blockers
- No live Supabase project credentials exist yet. I'll build against `DATABASE_URL`/env
  vars so it works once you supply them, and keep local dev running on a normal Postgres/
  SQLite fallback for tests. I'll flag this again when we reach Phase 1 setup, but will not
  stop building because of it.
- No Google Form URL yet — waitlist button will be env-driven and gracefully disabled with
  a dev-mode hint until you provide `WAITLIST_FORM_URL`.

## Review
(To be filled in at the end with a summary of what was built.)
