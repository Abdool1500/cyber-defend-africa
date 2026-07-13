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

---

# Phase 14 — Public site & auth UX polish

Investigated the current state against the new spec first. Good news: the
architecture the spec asks for is already built — custom `User` model with
`role`/`status`, `core:post_login_redirect` role-based redirect,
`@student_required`/`@instructor_required`/`@admin_required` decorators,
env-gated waitlist button, 400/403/404/500 templates, three dashboard base
layouts with sidebars. This phase is UI/UX polish and a few genuine gaps,
**not** a rebuild. No database migrations planned — `phone`/`country`
already exist on `User`; nothing here requires a schema change.

## 14.1 — Navigation ✅ DONE
- [x] Reorder navbar to: Home, Academy, Courses, GPT Sentinel, About,
      Pricing, Contact (Solutions/Services moved to footer, Resources
      added to footer — reachable, not deleted, just not top-level per
      the new spec)
- [x] Anonymous state: Login, Register, Join Waitlist buttons
- [x] Authenticated state: "Welcome {name}" dropdown → Dashboard, Profile,
      Logout (logout implemented as a POST form — Django 5.1's
      `LogoutView` only accepts POST, and there was previously no logout
      link anywhere in the UI at all)
- [x] Kept mobile offcanvas behavior — untouched, still works

## 14.2 — New Pricing page ✅ DONE (bundled with 14.1 — the new navbar
links to `company:pricing`, so it had to exist to avoid a broken link)
- [x] Added `company:pricing` view + template + 3 static plan cards in
      `apps/company/data.py` (Community/free, Academy Pro, Enterprise —
      same pattern as About/Solutions, no new models, no invented dollar
      figures — paid tiers say "Contact Us"/"Join Waitlist")

## 14.3 — Login page redesign ✅ DONE
- [x] Card-based layout: brand mark, "Welcome Back" heading, email,
      password, Remember Me checkbox, Forgot Password, Login button, Back
      to Home, disabled "Continue with Google" placeholder (clearly
      labeled "Coming soon" — no fake OAuth flow)
- [x] Wired Remember Me: unchecked → `session.set_expiry(0)` (expires at
      browser close), checked → default 2-week persistence. Verified both
      paths with the test client.

## 14.4 — Registration page redesign ✅ DONE
- [x] Split full name entry into First Name / Last Name inputs that
      combine into the existing `full_name` field on save (no model
      change); added required Phone Number and Country fields (already on
      `User`, just not exposed in `StudentRegistrationForm` before);
      added required "I agree to the Terms of Service" checkbox linking
      to `company:terms`
- [x] Kept: student-only signup, auto-login, redirect to student
      dashboard, and the role-injection guarantee (role is still never a
      form field)
- [x] Updated `apps/accounts/tests.py` registration tests to post the new
      required fields (they posted the old `full_name`-only payload) and
      added a test that missing `agree_terms` blocks account creation

## 14.5 — Profile page ✅ DONE
- [x] Show role and email as read-only display fields (not just the edit
      form) — new header block shows full name, role badge, and email
      above the edit form
- [x] Added an initials-based avatar badge (derived from `full_name` via
      a new `initials` template filter in
      `apps/core/templatetags/cda_extras.py`, pure template/CSS — no file
      upload, no storage dependency)

## 14.6 — Homepage hero ✅ DONE
- [x] Renamed hero CTAs to Enroll Now / Join Waitlist / Learn More;
      Enroll Now (→ `accounts:register`) becomes "Go To Dashboard" (→
      `core:post_login_redirect`) when authenticated. Learn More jumps to
      the "What We Do" section (`#what-we-do`, with `scroll-margin-top`
      so the sticky navbar doesn't cover it). Old "Explore Our
      Solutions"/"Discover Our Academy" hero buttons removed per the new
      3-button spec — both pages remain reachable via the footer and
      further down the homepage, nothing was deleted.

## 14.7 — Error pages ✅ DONE
- [x] 403: added explicit "Access Denied" heading + icon, card layout
- [x] 404: added explicit "Page Not Found" heading + icon, card layout
- [x] 500: added a "Try Again" (`location.reload()`) button alongside the
      existing "Back to Home" link — kept fully standalone/inline-CSS
      (no external CDN dependency), since this page must render even if
      something upstream is broken
- [x] Bonus: applied the same card treatment to 400.html for visual
      consistency (not explicitly in spec, but trivial and keeps all
      error pages looking like one family)
- [x] Verified both 403 and 404 through Django's real error-handling path
      (`DEBUG=False`, actual `PermissionDenied`/`Http404`), not just by
      rendering the template directly

## 14.8 — Dashboard quick access ✅ DONE
- [x] Student overview: added quick-access cards for Courses, Assignments,
      Quizzes, Certificates, Feedback, plus a disabled "Payments — Coming
      Soon" stub card (no billing logic, just the card)
- [x] Instructor overview: added quick-access cards for My Courses,
      Question Bank, Assignments, Quizzes, Students, Feedback (overview
      page previously had none — just stat counters)
- [x] Management overview: added quick-access cards for Users and Courses
      (linking to the existing Django Admin changelists), Analytics (via
      the existing `reports` app), GPT Sentinel, Academy, plus a disabled
      "Revenue — Coming Soon" stub card
- [x] Added a small `.cda-quick-link` hover-lift CSS rule for these cards
- [x] Verified all three dashboards render (200) as their respective
      roles with every card present, plus the full test suite (63/63)

## 14.9 — UI polish ✅ DONE
- [x] Converted flat Bootstrap alerts into dismissible Bootstrap 5 toast
      notifications (`templates/base.html`), auto-shown by new
      `static/js/ui.js`
- [x] Fixed a real latent bug found while doing this: Django's
      `messages.error()` tag is `"error"`, but Bootstrap 5 has no
      `.alert-error`/`.text-bg-error` class — error messages were
      rendering unstyled. Added `MESSAGE_TAGS` in
      `config/settings/base.py` mapping `ERROR` → `"danger"`. Covered by
      a new regression test.
- [x] Added loading-spinner state to submit buttons on form submit via
      `static/js/ui.js` (disables the button, swaps in a spinner +
      "Please wait…"; opt-out via `data-no-spinner` if ever needed).
      Confirmed no existing form uses an `onsubmit`-cancel pattern that
      this could conflict with (grepped for it), and the quiz-attempt
      page uses click handlers + fetch, not form submission, so it's
      unaffected.
- [x] Smooth scroll for in-page anchors, gated behind
      `prefers-reduced-motion: no-preference`
- [x] Subtle fade-in-up entrance animation on `.cda-surface` cards and
      the hero heading/lead/buttons — neutralized for reduced-motion
      users by the existing global animation-duration override
- [x] Added 2 new tests (`apps/core/tests.py`) covering the toast
      rendering and the MESSAGE_TAGS fix; full suite 65/65, Jest 39/39

## 14.10 — Final verification ✅ DONE
- [x] `python manage.py check` — zero errors
- [x] Full-site crawl: every zero-argument URL pattern (133 of them) ×
      every role (anonymous/student/instructor/admin) = 532 requests,
      using the same approach as the original Phase 13 build
      verification. Zero 500-level responses. The only non-200/302 codes
      were all expected: 403 on cross-role dashboard access, 405 on
      `GET /accounts/logout/` (correct — Django 5.1's `LogoutView` only
      accepts POST), 404 on detail pages needing objects that don't exist
      in an empty test DB.
- [x] Spot-checked every page touched this phase directly: home,
      pricing, login, register, about (anonymous, all 200); profile,
      student/instructor/management dashboards (correct role, 200;
      wrong role, 403)
- [x] Re-ran `python manage.py test` (65/65) and `npm test` (39/39) — all
      green
- [x] Security pass over every edited view/form/setting:
  - `StudentRegistrationForm.Meta.fields` still only exposes
    `email`/`phone`/`country` — role/status are still hardcoded
    server-side in `save()`, never derived from user input. The
    role-injection regression test still passes.
  - `AccountLoginView.form_valid` calls `super().form_valid()` first
    (unchanged auth logic) before touching session expiry — no auth
    bypass introduced.
  - `PricingView` is a plain public `TemplateView` like About/Solutions
    — no sensitive data, no auth needed, consistent with the rest of the
    public marketing site.
  - `MESSAGE_TAGS` addition is cosmetic only.
  - Every new/edited `<form>` (login, register, profile, logout) still
    has exactly one `{% csrf_token %}`.
  - `ui.js`'s spinner sets `button.innerHTML` to a fixed hardcoded
    string only — never interpolates user-controlled data, so no new
    XSS surface.
  - The new `initials` template filter outputs through Django's default
    autoescaping — a hostile `full_name` can't inject HTML.
  - Management dashboard's new Users/Courses quick-access cards link to
    Django Admin, which has its own independent permission checks; the
    overview page itself stays behind `@admin_required` (confirmed via
    the crawl: student/instructor get 403 on `/management/`).

## Phase 14 Review

### What changed
Public-facing UX polish and a handful of genuine gaps closed, on top of
an already-complete platform — no rebuild, no removed features, no DB
migrations:
- Navbar reordered to spec (Home/Academy/Courses/GPT Sentinel/About/
  Pricing/Contact) with a real auth-state switch (Login/Register/Join
  Waitlist vs. a Welcome-name dropdown with Dashboard/Profile/Logout).
  Solutions/Services/Resources moved to the footer, not deleted.
- New Pricing page (static content, no billing model).
- Login page redesign: brand mark, Remember Me (wired to real session
  expiry), disabled-but-honest "Continue with Google" placeholder.
- Registration page redesign: first/last name split, required phone/
  country, required Terms checkbox — all built on fields that already
  existed on `User`.
- Profile page: role/email header display, initials-based avatar badge.
- Homepage hero: Enroll Now / Join Waitlist / Learn More, with Enroll
  Now becoming Go To Dashboard when authenticated.
- 400/403/404/500 error pages restyled with explicit headings.
- Quick-access card grids added to all three dashboard overview pages
  (student/instructor/management), including agreed "Coming Soon" stubs
  for Payments/Revenue.
- Site-wide UI polish: toast notifications, submit-button spinners,
  smooth scroll, subtle entrance/hover animations.

### Bugs found and fixed along the way (not just written — caught during this work)
1. There was previously **no logout link anywhere in the UI** — only a
   URL you'd have to type. Fixed by adding it to the new navbar dropdown
   as a POST form (Django 5.1's `LogoutView` only accepts POST).
2. `messages.error()`'s default tag `"error"` has no matching Bootstrap 5
   class (`.text-bg-error` doesn't exist), so error messages were
   rendering with no color at all. Fixed via `MESSAGE_TAGS` in
   `config/settings/base.py`, with a regression test.

### Verification performed
- `python manage.py check` — zero errors, every time a change was made
- Full crawl: 133 zero-argument URLs × 4 roles (532 requests) — zero
  500-level responses
- `python manage.py test` — 65/65 passing (up from 61 at the start of
  this phase; added registration-terms and message-toast regression
  tests)
- `npm test` — 39/39 passing, untouched
- Manually verified with the Django test client (not just template
  inspection): anonymous vs. authenticated navbar state, Remember Me
  session expiry in both states, registration field order and required
  fields, profile avatar/role/email display, homepage hero CTA swap,
  real 403/404 via Django's actual error-handling path (not just
  rendering the template directly), all three dashboards under their
  correct role

### Known limitations / not done
- Profile picture is an initials-derived badge, not a real file upload —
  deferred until live Supabase credentials are available (per your
  decision in the plan check-in).
- Payments/Revenue are disabled "Coming Soon" stub cards — no billing
  feature exists in this codebase (per your decision).
- Country field on registration is a plain text input, not a validated
  country dropdown — kept intentionally minimal, matching the existing
  model field (free-text `CharField`).
- Browser-driven (Playwright/Selenium-style) verification of the new
  animations/toasts/spinners was not performed — verified via the
  Django test client (real view/template/permission stack) and by
  reading the rendered HTML/CSS/JS directly, not by an actual browser.

## Decisions (confirmed with you before starting)
1. **Payments / Revenue**: no payments app exists in this codebase — these
   ship as clearly-labeled, disabled "Coming Soon" stub cards, not real
   functionality.
2. **Profile picture**: initials-based avatar derived from `full_name`,
   pure template/CSS. No file upload wiring in this phase — real upload to
   the Supabase `avatars` bucket is deferred to when live credentials are
   available.
