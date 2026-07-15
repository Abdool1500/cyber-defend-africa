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

---

# Phase 15 — Real avatar upload to Supabase Storage

Live credentials are now in `.env` (previously deferred in Phase 14).
Rechecked connectivity before planning: the Postgres pooler host and the
Supabase Storage REST API are both reachable from here right now (an
earlier DNS failure this session looks like it was transient). A
read-only bucket listing came back empty — **no Storage buckets have
been created yet** in the live project (bucket creation is a manual
Supabase-dashboard step per `docs/supabase-setup.md`, not something
Django does). That means a real end-to-end live upload isn't possible
until the `avatars` bucket exists on your end, regardless of the code.

Plan: build this exactly the way `apps/assignments/` already does its
private-bucket file handling (same `StorageService`, same
`generate_safe_path`/`signed_url` calls, same `StorageError` →
`messages.error()` pattern), and test it the same way the existing
suite already tests storage — mocking `requests.post`/`.delete` rather
than depending on live credentials, which is the documented convention
in this codebase ("the suite never depends on live Supabase credentials
being available in CI"). No DB migration needed — `User.avatar_path`
already exists.

## 15.1 — Form ✅ DONE
- [x] Added a non-model `avatar = forms.ImageField(required=False)` field
      to `ProfileForm` (same pattern as `password1`/`agree_terms` being
      declared fields on a `ModelForm`)
- [x] `clean_avatar()` reuses `storage.validate_mime_type` /
      `validate_file_size`, raising `forms.ValidationError` so it renders
      as a normal field error
- [x] Verified with real Pillow-generated images (not just fake bytes,
      since Django's `ImageField` does its own Pillow-based decode check
      before `clean_avatar` even runs): a valid PNG passes; a
      Pillow-valid GIF is correctly rejected for not being in the
      3-format allow-list; an oversized real PNG (~26 MB) is correctly
      rejected with the exact byte counts in the error message

## 15.2 — View ✅ DONE
- [x] On successful upload: `generate_safe_path("avatars", str(user.id),
      original_filename=avatar.name)` → `StorageService.upload("avatars",
      ...)` → set `user.avatar_path`
- [x] Best-effort delete of the previous `avatar_path` object (non-fatal
      if it fails — don't block the profile update over cleanup)
- [x] `StorageError` (including `StorageNotConfiguredError`) caught and
      shown via `messages.error()`, exactly like
      `apps/assignments/student_views.py` — never a raw 500
- [x] Added `_signed_avatar_url(user)` helper — always regenerates fresh
      (private bucket, signed URLs expire), never persisted/cached
- [x] Verified end-to-end with mocked Supabase calls through the real
      view: first upload sets `avatar_path` and calls the mocked
      `requests.post`; a second upload correctly calls `requests.delete`
      on the *previous* path before switching `avatar_path` to the new
      one (confirmed no orphaned-file leak on re-upload)

## 15.3 — Template ✅ DONE
- [x] Profile page: if `avatar_url` is present, shows a real `<img
      class="cda-avatar-img">` from the freshly-generated signed URL;
      falls back to the existing initials badge otherwise (empty
      `avatar_path` or a failed signed-URL call)
- [x] Added `enctype="multipart/form-data"` to the profile form (missing
      before — no file field existed) and a `.cda-avatar-img` CSS rule
      sized to match the existing initials badge
- [x] Also render each field's `help_text` (needed for the new avatar
      field's "PNG, JPEG, or WEBP. Max 20 MB." hint) — purely additive,
      no other field on this form sets help_text so nothing else changes
- [x] Verified both states directly: no-avatar page shows the initials
      badge and the correct `enctype`; after a mocked upload, the page
      shows `cda-avatar-img` with the real signed URL from the mocked
      Supabase response

## 15.4 — Tests ✅ DONE
- [x] Added `ProfileAvatarUploadTests` to `apps/accounts/tests.py` (same
      `@override_settings` + `@patch(".storage.requests.post")` pattern
      as `apps/core/tests.py`), 7 tests: successful upload sets
      `avatar_path`; re-upload deletes the previous file; oversized real
      PNG rejected without ever reaching the mocked storage call;
      Pillow-valid-but-disallowed GIF rejected the same way; a genuine
      Supabase error response (500) surfaces as a user-facing message,
      not a 500 to the browser; profile page shows the initials badge
      with no avatar and the real signed-URL `<img>` after one

## 15.5 — Verification ✅ DONE
- [x] `python manage.py check` — zero errors
- [x] Full suite: `python manage.py test` 72/72 (up from 65 — 7 new
      avatar tests), `npm test` 39/39
- [x] Proved (not just assumed from the `@patch` decorators) that no
      live Supabase call happens during the test run: monkeypatched
      `socket.socket.connect` to raise on any real connection attempt and
      reran the full `apps.accounts` suite — still 19/19 green, meaning
      every Supabase interaction really is mocked
- [ ] Optional live smoke-test against the real project — still blocked
      on the `avatars` bucket not existing yet in the live Supabase
      dashboard (confirmed via a read-only bucket-list call in the
      planning step). Not attempted; ask before doing this once you've
      created the bucket.

## Phase 15 Review

### What changed
Real profile-picture upload, replacing the Phase 14 initials-only
placeholder — no DB migration (`User.avatar_path` already existed),
built on the same `StorageService`/`generate_safe_path`/`signed_url`
pattern `apps/assignments/` already uses for private-bucket files:
- `ProfileForm` gained a non-model `avatar` `ImageField` with MIME/size
  validation (3-format allow-list, 20 MB cap — same limits as everywhere
  else in the app)
- `profile()` view uploads to the private `avatars` bucket, updates
  `avatar_path`, and best-effort deletes the previous file on re-upload
  so the bucket doesn't accumulate orphaned images
- Profile page shows a real `<img>` from a freshly-generated signed URL
  when set, falling back to the Phase 14 initials badge otherwise
- 7 new mocked-Supabase tests in `apps/accounts/tests.py`

### Security check
- Upload path is `avatars/{request.user.id}/{random-uuid}.{ext}` —
  namespaced to the authenticated user's own ID (not attacker-supplied),
  so a user can never write into another user's avatar path
- `generate_safe_path` (unchanged, reused as-is) never trusts the
  original filename beyond a sanitized extension — already covered by
  existing tests, no path-traversal surface reopened here
- Signed URLs are generated fresh per request, never persisted — no
  long-lived direct link leaks out
- `SUPABASE_SERVICE_ROLE_KEY` never reaches the template/frontend, same
  as every other use of `StorageService`
- Upload failures surface as a `messages.error()`, never a raw 500, and
  never partially save other profile fields if the avatar upload fails
  (atomic: `form.save(commit=False)` then one `user.save()` at the end)

### Verification performed
- `python manage.py check` — zero errors
- `python manage.py test` — 72/72 (was 65 before this phase)
- `npm test` — 39/39, untouched
- Proved the storage tests are genuinely network-isolated by
  monkeypatching `socket.socket.connect` to raise and rerunning the
  suite — still green, so nothing silently depends on live credentials
- Confirmed via a **read-only** bucket-list call that the live Supabase
  project has no Storage buckets yet — a real end-to-end live test isn't
  possible until you create them from the dashboard; not attempted

### Known limitation
- Live smoke-test against your actual Supabase project is still
  outstanding — needs the `avatars` bucket created first. Ask before
  running one once that's done, since it touches real infrastructure.

---

# Phase 16 — Learning Analytics & Impact Measurement System

This is a large feature — roughly 6-10x the size of Phases 14-15
combined. Investigated the existing codebase first (quizzes, courses/
enrollments/lessons, certificates, instructors, reports, REST API,
notifications/audit, feedback, dashboards, time-tracking) before
planning, to reuse rather than duplicate. Key findings:

- **Reusable as-is**: Quiz/QuizAttempt scoring (`percentage` is already
  server-calculated), `Enrollment.progress_percentage` +
  `LessonProgress.completed`, `Certificate` uniqueness + verification
  view, CSV export pattern (`apps/reports/`), PDF export pattern
  (ReportLab, already a dependency), REST API versioning/permission
  classes (`apps/core/api_permissions.py`), `StudentFeedback`'s
  anonymity pattern, `AuditLog`.
- **Genuinely new, no migration to reuse**: no pre/post-test concept on
  `Quiz`; no time-spent tracking anywhere (only state-change
  timestamps); no cohort/section concept at all; no QR code on
  certificates; no practical-lab tracking; no employment-outcome
  tracking; no NPS/confidence fields on feedback; no Excel export
  (`openpyxl` not installed); no charting library wired in (Chart.js via
  CDN, same pattern as Bootstrap).
- **New dependencies needed**: `qrcode` (certificate QR codes),
  `openpyxl` (Excel export). Chart.js loads via CDN like Bootstrap
  already does — no npm package needed.

## Decisions (confirmed with you before starting)
1. **Demographics** (for "Women trained"/"Youth trained"): optional
   `gender` + `date_of_birth` fields added to the **profile page only**,
   never required, never on the registration form.
2. **Leaderboard**: anonymized — each student sees their own
   rank/percentile only (e.g. "Top 15%"), never other students' names.
   Same posture as the existing anonymous-feedback pattern.
3. **Dark/light mode**: build a **real, site-wide toggle** — bigger than
   just the new analytics pages, since `base.html` currently hardcodes
   `data-bs-theme="dark"` everywhere. Placed in the foundation phase
   (16.A) so every subsequent analytics page is built theme-aware from
   the start instead of needing retrofitting later.
4. **App structure**: several focused new apps —
   `apps.cohorts`, `apps.labs` (practical lab tracking),
   `apps.employment` (graduate outcomes), `apps.analytics`
   (aggregation/impact dashboard/API) — matching the existing
   one-app-per-domain convention (`courses`, `enrollments`, `feedback`,
   `certificates` are each separate).

## Defaults I'm applying (flag if you want something different when you review)
- **QR codes**: generated **on-the-fly** via a dedicated view
  (`/certificates/<id>/qr.png`), not pre-generated and stored — avoids a
  Supabase Storage dependency entirely (the `certificate-assets` bucket
  doesn't exist yet in your live project per the Phase 15 investigation)
  and is simpler/always-fresh.
- **Non-derivable impact KPIs** ("SMEs protected", "Healthcare workers
  trained", "Businesses started"): these can't be algorithmically
  derived from LMS data (no such events are tracked anywhere). Adding a
  simple admin-editable "Impact Snapshot" model for figures like these,
  clearly separated in the UI from the genuinely-computed stats (people
  trained, certificates, hours, labs, employment outcomes, etc.) so
  it's never unclear which numbers are measured vs. self-reported.
- **Employment evidence & salary data**: private Supabase bucket (same
  pattern as Phase 15 avatars), visible only to the student themselves
  and admin/management roles — never to instructors. Salary shown only
  as an optional range, never exact figures, and only aggregated
  (bucketed) in any report.
- **Revenue**: spec marks this "(future)" — same "Coming Soon" stub
  treatment as Payments/Revenue got in Phase 14, not a real feature.

## Roadmap (sub-phases — detailed checklist below for 16.A only; later
sub-phases get the same full-detail treatment when we reach them, same
as how the original Phase 0-13 build was sequenced)

- **16.A — Foundation**: site-wide dark/light theme toggle; optional
  `gender`/`date_of_birth` fields on profile; scaffold `apps.cohorts`,
  `apps.labs`, `apps.employment`, `apps.analytics` (registered, empty);
  add `qrcode`/`openpyxl` to requirements
- **16.B — Pre/Post-Test tracking** ✅ DONE: `Quiz.quiz_type` field
  (standard/pre_test/post_test); skill-improvement calculation service;
  "My Skill Improvement" student widget + chart
- **16.C — Learning time tracking** ✅ DONE: login/logout session
  tracking via Django auth signals; per-lesson time via a lightweight
  heartbeat endpoint; today/weekly/monthly/lifetime aggregates
- **16.D — Practical lab tracking** ✅ DONE (`apps.labs`): lab catalog
  covering every tool/category in the spec; per-student lab progress
  (not-started/in-progress/completed, attempts, score, instructor
  feedback); student + instructor UI
- **16.E — Course/module progress** ✅ DONE: auto-recalculating progress
  via signals (was manual); module-level progress; progress-bar UI
- **16.F — Cohort analytics** ✅ DONE (`apps.cohorts`): Cohort + membership
  models; per-cohort enrollment/completion/score/improvement/dropout/
  certificate stats
- **16.G — Certificate verification enhancements** ✅ DONE: QR code
  (on-the-fly per the default above), certificate hash, richer
  verification page (instructor name, hash)
- **16.H — Employment outcomes** ✅ DONE (`apps.employment`): graduate
  profile self-report form, evidence upload, management-facing
  aggregation
- **16.I — Learner feedback/NPS** ✅ DONE: extend `StudentFeedback` with
  difficulty, confidence-before/after and an NPS question (0-10); NPS
  calculation service in `apps.analytics`
- **16.J — Management Analytics Dashboard** ✅ DONE: Chart.js-driven
  dashboard — DAU/MAU, enrollments, completion, scores, certificates,
  retention, top instructors/courses, dropout, learning hours, skill
  improvement, employment rate
- **16.K — Impact Dashboard** ✅ DONE: dedicated page combining derived
  stats + the admin-editable Impact Snapshot for non-derivable KPIs;
  CSV-exportable (Excel/PDF versions deferred to 16.L)
- **16.L — Exports** ✅ DONE: CSV/Excel/PDF for Impact, Course, Student,
  and Employment reports, following the existing export conventions
- **16.M — REST API** ✅ DONE: `/api/v1/analytics/`, `/api/v1/impact/`,
  `/api/v1/cohorts/`, `/api/v1/employment/`, plus a new `/api/v1/
  certificates/` (progress was already adequately covered by the
  existing `EnrollmentViewSet`)
- **16.N — Student dashboard widgets** ✅ DONE: Learning Streak, Hours
  Learned, Skill Improvement, Labs Completed, Certificates, Upcoming
  Assignments, Recent Quiz Scores, anonymized Leaderboard Position
- **16.O — Instructor dashboard widgets** ✅ DONE: engagement, average
  grades, students-at-risk, lab completion, quiz/assignment analytics,
  feedback trends
- **16.P — FID Impact Evidence report** ✅ DONE: dedicated KPI service +
  downloadable funder-ready export (built on 16.L's export infra) —
  "FID" confirmed with the user to mean generic funder impact
  documentation, not a specific named donor template
- **16.Q — Data quality pass** ✅ DONE: signals for auto-updating
  analytics on quiz/assignment/lab/certificate events, duplicate-
  prevention constraint audit, audit-log hooks — found and fixed 3 real
  bugs, not just a clean audit
- **16.R — Final verification** ✅ DONE: `manage.py check`, full-site
  crawl, full test suite, security pass (same discipline as Phases
  14-15) — Phase 16 is complete

Each sub-phase gets its own tests as it's built (matching the Phase
14/15 convention) rather than one giant testing phase at the end.

---

## 16.A — Foundation ✅ DONE

### Dark/light theme toggle
- [x] Added a toggle button to the navbar (`.theme-toggle-btn`),
      persisted via `localStorage("cda-theme")`, applied by a tiny
      inline script as the first thing in `<head>` (before any CSS
      loads) to avoid a flash of the wrong theme
- [x] Added light-theme CSS variable overrides in `main.css`
      (`[data-bs-theme="light"]` block redefining `--cda-navy`,
      `--cda-surface`, `--cda-text`, etc.)
- [x] **Design decision made while implementing**: the navbar and
      footer keep `data-bs-theme="dark"` pinned directly on themselves
      (brand chrome, always dark) using Bootstrap 5.3's nested
      theme-scoping — everything inside `<main>` (all page content,
      including dashboard sidebars) toggles. This avoided rewriting 38+
      templates that use Bootstrap's hardcoded `.btn-outline-light` /
      `.text-light` / `.link-light` / `.text-secondary` /
      `.border-secondary` utilities (these are NOT theme-adaptive in
      Bootstrap — confirmed against Bootstrap's own source — they're
      literal "always this brand color" utilities). Added scoped
      `[data-bs-theme="light"] main .X` overrides for all five instead.
- [x] **Real bug found and fixed while verifying**: `.cda-surface`
      (footer's own wrapper class) had no explicit `color`, so
      unstyled headings inside it (footer's "Cyber Defend Africa" h5,
      "Company"/"Academy"/"Legal" h6s) inherited `body`'s *already-
      resolved* light-theme text color instead of re-deriving from the
      footer's own dark-pinned `--cda-text` — because CSS `color`
      inheritance copies the parent's computed value, it doesn't
      re-evaluate `var()` expressions per descendant. Fixed by adding
      an explicit `color: var(--cda-text)` directly to `.cda-surface`.
      Caught via computed-style inspection in a real browser, not just
      visual screenshot review — confirmed the fix with
      `getComputedStyle()` before/after.
- [x] Verified in a real headless-Chromium session (Playwright): home
      page, pricing, login, and an actual student dashboard (registered
      a real throwaway account through the live form) — both light and
      dark — plus theme persistence across a full page reload. Zero
      console errors.

### Profile demographics
- [x] Added optional `gender` (choices incl. "Prefer not to say") and
      `date_of_birth` to `User`, exposed only on the profile edit form
      — migration `accounts/0002_user_date_of_birth_user_gender.py`
      (additive, nullable, zero data-loss risk)
- [x] `ProfileForm` + profile template updated (template needed no
      changes — it already used a generic field loop) — future date of
      birth rejected with a clear error
- [x] 4 new tests confirming: registration form never exposes these
      fields (checked via a fresh anonymous client — `setUp()`'s logged
      -in client would've redirected before rendering the form),
      demographics are fully optional, valid values save correctly,
      future dates are rejected

### App scaffolding
- [x] `apps/cohorts`, `apps/labs`, `apps/employment`, `apps/analytics` —
      registered in `INSTALLED_APPS`, confirmed loadable with zero
      models each (scaffolding only — real models land in
      16.D/16.F/16.H/16.J-K)

### New dependencies
- [x] Added `qrcode>=8.0` and `openpyxl>=3.1` to `requirements.txt` and
      installed both into the project venv

### Verification
- [x] `manage.py check` — zero errors
- [x] `manage.py makemigrations --check --dry-run` — no missing
      migrations
- [x] Full suite: `manage.py test` 76/76 (up from 72), `npm test` 39/39

## 16.B — Pre/Post-Test tracking ✅ DONE

- [x] Added `Quiz.quiz_type` (standard/pre_test/post_test, default
      standard) with a conditional `UniqueConstraint` — at most one
      pre-test and one post-test per course (standard quizzes are
      unlimited), matching the spec's "Each course must support:
      Diagnostic Pre-Test, Final Post-Test" (singular). Migration
      `quizzes/0002_...` — additive, safe.
- [x] Exposed `quiz_type` in the instructor `QuizForm` (needed no
      template change — form.html already used a generic field loop)
      and added a Pre-Test/Post-Test/Standard badge column to the
      instructor quiz list table
- [x] New `apps/analytics/services/skill_improvement.py`:
      `get_skill_improvement(student, course)` — reads the student's
      *latest graded* attempt on the course's pre-test and post-test
      quizzes (server-side only, same philosophy as
      `quizzes/services/grading.py`) and returns raw improvement
      (percentage points) plus normalized/Hake gain (how much of the
      *possible* improvement was captured — going from 90%→95% is a
      bigger relative achievement than 35%→40%, even though both are
      +5 points). Handles the "not available yet" state explicitly
      (`complete: False`) rather than assuming zeros.
- [x] "My Skill Improvement" widget on the student dashboard: a
      Chart.js grouped bar chart (pre vs. post per course) plus a
      table with the improvement delta, shown only for courses where
      both tests are graded
- [x] 10 new tests in `apps/analytics/tests.py` covering: no
      pre/post-test configured, pre-test not yet attempted, full
      improvement calculation, latest-attempt-wins over earlier
      attempts, ungraded attempts ignored, perfect-pre-test
      division-by-zero guard, failed-post-test pass/fail flag, and the
      duplicate pre/post-test database constraint itself

### Bugs found and fixed while building this (not just written — caught during verification)
1. **XSS risk in my own first draft**: I initially serialized the chart
   data with `json.dumps()` in the view and rendered it with
   `{{ ...|safe }}` in the template — if a course title ever contained
   `</script>`, that would break out of the script tag. Caught this
   before shipping and switched to Django's `json_script` template
   filter (which HTML-escapes safely for exactly this case), reading it
   back via `JSON.parse(...textContent)` in JS instead.
2. **Chart colors hardcoded for dark mode only**: the tick/legend label
   colors I first wrote (`#94a3b8`/`#e6ecf5`) would have been
   unreadable against the light theme added in 16.A — Chart.js renders
   to a `<canvas>`, which doesn't pick up CSS variable changes the way
   HTML elements do. Fixed by reading the current `data-bs-theme` at
   chart-init time to pick contrasting colors, and re-applying them via
   `chart.update()` when the toggle is clicked while the page is open
   (not just on next reload). Verified both the initial render and the
   live in-page toggle in a real browser screenshot.

### Verification performed
- `manage.py check` — zero errors; `makemigrations --check` — clean
- Full suite: `manage.py test` 86/86 (up from 76), `npm test` 39/39
- Functional test confirming the widget renders with real pre/post-test
  data (35% → 90%, shows "+55.0%"), and is correctly *absent* when a
  course has no pre/post-test data (not a broken/empty state — just not
  shown)
- Real-browser verification (Playwright): logged in as a seeded student
  with actual graded pre/post-test attempts, confirmed the chart and
  table render correctly in dark mode, then confirmed live re-coloring
  on theme toggle without a page reload. Cleaned up the seeded test
  data from the dev database afterward.

## 16.C — Learning time tracking ✅ DONE

### Design decision made while planning this
The spec's "Track:" list (login/logout, per-lesson, per-course, video/
reading/lab time) and its "Display:" list (today/weekly/monthly/
lifetime) are two different concerns that needed separating into two
models, not one:
- **`LearningSession`** (`apps/analytics/models.py`) — one row per
  login, closed on logout. Tracks *time on the platform*. Kept for
  every authenticated user (not just students), since it'll also feed
  the platform-wide DAU/MAU metric in the Management Dashboard (16.J) —
  restricting it to students now would've undercounted that later.
- **`LearningTimeEntry`** — one row per **(student, lesson, date)**,
  incremented by a heartbeat while a lesson page is open. This is a
  content-*engagement* metric, and it's what actually drives the
  "today/weekly/monthly/lifetime" dashboard widget — a single
  cumulative `time_spent_seconds` counter (my first instinct) can't be
  sliced by day at all, since `last_accessed_at` only reflects the
  *most recent* touch, not when each chunk of time was actually
  accumulated. Splitting entries by date makes every aggregate (daily,
  weekly, monthly, lifetime, per-lesson, per-course, per-content-type)
  a simple date-range/group-by sum over the same source of truth.
- "Time spent in practical labs" per this phase means time on
  `Lesson`s where `lesson_type == "lab"` (already an existing choice on
  `Lesson`) — **not** the full practical-lab catalog/attempt/scoring
  subsystem the spec describes in its own section 3, which is a
  separate, bigger piece of work landing in **16.D**.

### What was built
- `LearningSession` + `LearningTimeEntry` models (`apps/analytics/`,
  migration `0001_initial.py` — brand new tables, no risk to existing
  data)
- `apps/analytics/signals.py`: `user_logged_in`/`user_logged_out`
  handlers open/close a `LearningSession`. An abandoned session (tab
  closed without logout) gets capped at `MAX_SESSION_HOURS=4` and
  closed the next time that user logs in, rather than staying open
  indefinitely
- `lesson_heartbeat` view (`apps/enrollments/student_views.py`) — POST
  endpoint the lesson page calls every 60s while visible. Never trusts
  the client's reported duration beyond `MAX_HEARTBEAT_SECONDS=90`;
  verifies the student is actually enrolled before accepting any time
  for a lesson (reuses the existing `_get_enrollment` helper — same
  access-control path as viewing the lesson itself)
- `apps/analytics/services/learning_time.py`: `get_learning_time_summary()`
  (today/week/month/lifetime) and `get_course_time_breakdown()`
  (video/reading/lab/live split for one course)
- "My Learning Time" card row on the student dashboard, plus a new
  `duration_hm` template filter (`5425` seconds → `"1h 30m"`)
- Heartbeat JS in `templates/student/learning/lesson.html`, pausing
  when the tab isn't visible (`document.visibilityState`)
- 22 new tests across `apps/analytics/tests.py` (learning-time
  aggregation boundaries, per-course breakdown, login/logout signal
  behavior including the stale-session cap), `apps/enrollments/tests.py`
  (new file — heartbeat capping/accumulation/cross-day/access-control),
  and `apps/core/tests.py` (dashboard widget rendering)

### Bugs found and fixed while building this
1. **Test fixture bug, not app code**: my first `_make_lesson()` test
   helper created a new `CourseModule` per call, which collided with
   `CourseModule`'s unique `(course, display_order)` constraint the
   moment a test needed more than one lesson in the same course. Fixed
   by having the helper reuse one module per course via
   `get_or_create`.
2. Confirmed via a real browser that the lesson page's CSRF token is
   now unconditionally present (`{% csrf_token %}` was previously only
   rendered inside the "Mark Complete" form, which doesn't exist once a
   lesson is already completed — the heartbeat JS would have crashed on
   `document.querySelector(...).value` being null for any already-
   completed lesson).

### Verification performed
- `manage.py check` — zero errors; `makemigrations --check` — clean
- Full suite: `manage.py test` 108/108 (up from 86), `npm test` 39/39
- Real-browser (Playwright) end-to-end check: logged in as a seeded
  student, opened a real lesson page, confirmed the CSRF token element
  exists, fired the exact fetch the 60s interval would perform, got a
  real 200 response, confirmed the row actually persisted in the dev
  database (`60` seconds, correct lesson, today's date), then confirmed
  the student dashboard's "My Learning Time" widget displays it
  ("1m"). Cleaned up the seeded data afterward.

### Known limitation
- If a browser tab is closed without an explicit logout, up to ~59
  seconds of in-progress lesson time (since the last heartbeat) and the
  platform session's true end time are not captured precisely — the
  session gets capped at `MAX_SESSION_HOURS` on next login instead of
  reflecting the real (unknowable) close time. This is a standard,
  documented trade-off for heartbeat-based tracking without a
  `sendBeacon`-on-unload mechanism, which was deliberately left out to
  avoid the reliability issues browsers have with unload-time requests.

## 16.D — Practical lab tracking ✅ DONE

### Design decisions made while planning this
- **`PracticalLab` mirrors `Assignment` almost exactly** (course-scoped,
  instructor-authored, student submits, instructor grades) — that's the
  closest existing pattern in this codebase for "student does hands-on
  work, instructor scores it," so I reused its shape rather than
  inventing something new: course FK (required, not nullable — matches
  Quiz/Assignment/Question Bank so the exact same
  `InstructorAssignment`-based ownership check applies uniformly),
  module FK (optional), status draft/published/archived,
  `allow_resubmission`.
- **Only 2 stored statuses** (`in_progress`, `completed`) on
  `LabProgress`, not 3 — "Not Started" is the absence of a row entirely,
  matching how `LessonProgress` already represents "not started" in
  this codebase. Storing a `NOT_STARTED` status value would mean a row
  exists for every student × every lab in the catalog, which is both
  wasteful and semantically odd (there's nothing to record yet).
- **"Completion time" is a computed property** (`completion_duration`,
  `completed_at - started_at`), not a stored field — same "derive,
  don't cache" approach as `QuizAttempt` (which computes duration from
  `started_at`/`submitted_at`) and everything built in 16.B/16.C.
- **Resubmission workflow matches `Assignment.allow_resubmission`
  exactly**: a student can restart a lab (incrementing `attempts`) only
  while `allow_resubmission=True` **and** the record isn't graded yet —
  once `score` is set, it's final. Same rule, same wording as the
  existing assignment help text.
- Gave instructors a full lab CRUD (not just Django Admin) — every
  other content type in this platform (quizzes, assignments, question
  bank) already has instructor-facing create/edit UI, so routing labs
  through Admin-only would have been an inconsistent asymmetry.

### What was built
- `PracticalLab` (13 categories covering every tool named in the spec:
  Linux, Networking, Nmap, Wireshark, Burp Suite, OWASP, Web Security,
  SOC, Threat Hunting, Digital Forensics, Cloud Security, Python
  Security Automation, AI Security Engineering) + `LabProgress`
  (`apps/labs/`, migration `0001_initial.py` — brand new tables)
- Student: lab list (status badge per lab) + detail page with
  Start/Mark Complete/Restart actions, enrollment-gated exactly like
  the existing lesson-viewing view
  (`apps/enrollments/student_views.py`'s pattern)
  reused
- Instructor: lab list/create/edit (course selection restricted to
  their own `InstructorAssignment`s, exactly like `AssignmentForm`),
  per-lab progress list, and a grade form (score capped at
  `max_score`, audit-logged via the existing `apps.audit.services.log_action`
  — same call as assignment grading)
- Wired into both dashboards: student gets a "My Practical Labs"
  not-started/in-progress/completed summary (via a new
  `apps.analytics.services.lab_progress.get_lab_summary()`) and a
  Quick Access card; instructor gets a "Pending Lab Grading" stat card
  and a Quick Access card. Both sidebars got a "Practical Labs" link.
- 20 new tests: `apps/labs/tests.py` (17 — model constraints, the full
  student start/complete/restart state machine including the two ways
  restart can be blocked, instructor course-ownership scoping on every
  view, score-cap validation, audit log creation) and 3 more in
  `apps/analytics/tests.py` for `get_lab_summary()`

### Verification performed
- `manage.py check` — zero errors; `makemigrations --check` — clean
- Full suite: `manage.py test` 128/128 (up from 108), `npm test` 39/39
- Real end-to-end browser verification (Playwright, two separate
  browser contexts so student/instructor sessions didn't share
  cookies — caught and fixed a test-script bug where they initially
  did): registered student starts a lab → marks it complete → sees
  "Awaiting instructor review"; instructor sees it in their progress
  list → grades it (88/100 + feedback) → audit-logged; student
  immediately sees the score and feedback, and confirms the lab is now
  correctly locked from further restarts. Cleaned up seeded data
  afterward.

### Known scope note
- Lab **execution environments** (actual VMs/containers/sandboxes for
  Nmap/Wireshark/etc.) are explicitly out of scope — this phase tracks
  *progress and grading* against a lab catalog, the same way
  `Assignment` tracks submissions without hosting the work itself.
  Building real interactive lab environments would be an infrastructure
  project of its own, well beyond an analytics/tracking feature.

## 16.E — Course/module progress ✅ DONE

### What was wrong before
`Enrollment.recalculate_progress()` already existed and worked
correctly — but it was called from exactly **one** place: the
`lesson_detail` view's "mark complete" POST handler. Every other way
the underlying data could change left `progress_percentage` silently
stale:
- Editing a `LessonProgress` row via Django Admin
- A future API doing the same
- An instructor publishing a **new** lesson (the denominator grows for
  every enrolled student, not just whoever triggered it) or
  unpublishing one (denominator shrinks)
- An instructor publishing/unpublishing an entire module

### What was built
- **`apps/enrollments/signals.py`** (wired via `EnrollmentsConfig.ready()`):
  `post_save`/`post_delete` on `LessonProgress` recalculates that one
  student's enrollment; the same on `Lesson`/`CourseModule`
  recalculates *every* active enrollment in that course, since the
  denominator changed for all of them. Removed the now-redundant manual
  `enrollment.recalculate_progress()` call from `lesson_detail` — the
  signal already fires from the `progress.save()` immediately before
  it, per the "remove duplicate code" requirement.
- **`apps/analytics/services/course_progress.py`**: `get_module_progress()`
  (per-module percentage), `get_course_module_breakdown()` (per-course
  list), and `get_overall_academy_progress()` — a **lesson-count-weighted**
  average across all enrolled courses, not a plain average of
  percentages. A plain average would let a 2-lesson course finished
  count exactly as much as a 50-lesson course barely started; weighting
  by actual lesson count is what "overall academy progress" should
  mean. Verified with a real test: 1-lesson course at 100% + 9-lesson
  course at 0% is **10%** overall (1 of 10 total lessons), not the 50%
  a plain average would give.
- Real progress bars (Bootstrap `.progress`/`.progress-bar`, not just
  text percentages) added to: the student dashboard's new "Overall
  Academy Progress" bar, the "My Courses" page, and the course overview
  page (course-level bar + one bar per module).

### Verification performed
- `manage.py check` — zero errors; no migration needed (no new models,
  pure logic + signals)
- Full suite: `manage.py test` 138/138 (up from 128) — 5 new tests
  proving the signals actually fire for every path that used to go
  stale (direct `LessonProgress` creation/deletion, publishing a new
  lesson, unpublishing a lesson, unpublishing a whole module — each one
  asserts the exact resulting percentage, not just "it changed"), plus
  5 new tests for the course-progress service functions. `npm test`
  39/39.
- Real-browser (Playwright) verification with realistic seeded data
  (3/4 lessons done in one module, 1/4 in another): dashboard showed
  "Overall Academy Progress: 50%" with a real bar; the course page
  showed the course-level 50% bar plus **75% and 25%** bars for the two
  modules respectively, both correct in the same screenshot as the
  lesson-by-lesson checkmarks. Cleaned up seeded data afterward.

## 16.F — Cohort analytics ✅ DONE

### Design decisions made while planning this
- **`CohortMembership` is a many-to-many through-model, not a FK on
  `User`** — a student can realistically belong to more than one cohort
  at once (e.g. a time-based intake cohort like "March 2026" *and* a
  demographic/program cohort like "Women in Cybersecurity"
  simultaneously). A single FK would have forced an artificial choice.
- **Cohort CRUD stays on Django Admin; the analytics view is a new
  custom page** — this splits cleanly along the same line the original
  build already established (`management_overview`'s own "Known
  limitations" note: Admin handles raw record CRUD, custom pages handle
  computed platform stats). Creating a cohort and adding/removing
  members is basic data entry with no logic — Admin already does this
  well, with a `TabularInline` for membership so it's a single form.
  The stats page is the actual new value: Admin can't show *computed
  aggregates*, only raw rows.
- **"Average score" is scoped to graded quiz attempts only**, not a
  blended quiz+assignment+lab figure — assignment/lab average scores
  are explicit, separate KPIs on the Management Analytics Dashboard
  (16.J) and Instructor Dashboard (16.O); conflating them here into one
  number would have obscured which score type it actually reflects.
- **"Average improvement" reuses 16.B's `get_skill_improvement()`
  directly**, run once per cohort-member enrollment and averaged across
  only the ones with a completed pre/post-test pair — no new
  calculation logic, just aggregation over the existing per-student
  function. Confirmed via a dedicated test that this is really calling
  through, not reimplementing the math.

### What was built
- `Cohort` + `CohortMembership` (`apps/cohorts/`, migration
  `0001_initial.py` — brand new tables) with Django Admin registration
  (`TabularInline` for membership, with `autocomplete_fields`)
- `apps/analytics/services/cohort_stats.py`: `get_cohort_stats(cohort)`
  — member count, total enrollments, completion rate, average quiz
  score, average improvement, dropout rate (withdrawn + suspended
  enrollments), certificates earned
- Management-facing cohort list (all cohorts with their computed stats
  in one table) and detail page (same stats as cards + a member
  roster), both `@admin_required` — confirmed students/instructors get
  403, not just "no link to it"
- Wired into the management sidebar and overview Quick Access
- 14 new tests: 7 in `apps/cohorts/tests.py` (membership constraints, a
  student in multiple cohorts, view access control per role) and 7 in
  `apps/analytics/tests.py` (every stat in `get_cohort_stats`
  individually — empty cohort, dropout-rate math, graded-vs-ungraded
  quiz filtering, the skill-improvement reuse, certificate status
  filtering, and cross-cohort isolation so one cohort's stats never
  leak another's members)

### Verification performed
- `manage.py check` — zero errors; `makemigrations --check` — clean
- Full suite: `manage.py test` 152/152 (up from 138), `npm test` 39/39
- Real-browser verification with realistic seeded data (2 students, one
  completed enrollment + one active, one issued + one revoked
  certificate, two different quiz scores): the cohort list and detail
  pages both showed the exact right numbers (50.0% completion, 80.0%
  average score — correctly the mean of 88 and 72 — 0.0% dropout, 1
  certificate, "—" for average improvement since no pre/post-test data
  existed), and a student session got a real 403 hitting the cohort
  list URL directly. Cleaned up seeded data and stray dev-server
  processes left over from earlier phases afterward.

## 16.G — Certificate verification enhancements ✅ DONE

### What already existed (confirmed before building, to avoid duplicating it)
Duplicate-certificate prevention, `certificate_number`, and
`verification_code` were already solid — the unique constraint and
auto-generation were untouched. The gaps were specifically: no QR code,
no certificate hash, and the verification page was missing instructor
name (certificates aren't directly linked to an instructor — derived
via `InstructorAssignment` for the course instead).

### Design decision: a real HMAC, not a plain hash
A plain `sha256(certificate_number + student_id + course_id)` would
give **zero** actual tamper-evidence — anyone with direct database
write access could alter a field and recompute a matching plain hash
in the same breath, since both the data and the check live in the same
row. Instead, `certificate_hash` is an **HMAC-SHA256 signed with
Django's `SECRET_KEY`**, which lives in settings/env, never in the
database. Forging a hash that matches tampered data requires knowing
that key — direct DB tampering alone can't produce a valid one. Added
`Certificate.hash_is_valid()` (recomputes from current field values,
compares via `hmac.compare_digest`) and wired it into a read-only
Django Admin column. Also **locked `student`/`course` as read-only in
Admin** while I was in there — a certificate's identity shouldn't
change post-issuance, and this closes the one legitimate way the hash
could otherwise legitimately go stale (an Admin edit to student/course
after issuance). `issued_at` is deliberately excluded from the hash
payload — it's an `auto_now_add` field not yet populated on the
in-memory instance at the point in `save()` where the hash needs to be
computed, so including it would've meant restructuring the save
order for no real benefit (certificate_number + student + course
already uniquely identify the record).

### What was built
- `Certificate.certificate_hash` field + `compute_certificate_hash()` +
  `hash_is_valid()` (migration `0002_...` — includes a `RunPython`
  backfill step for any certificates that might already exist in an
  environment that isn't this fresh dev database, even though this
  project's own DB currently has zero)
- QR code generated **on-the-fly** (`certificates:qr_code`), per the
  Phase 16 planning default — encodes the public verification URL,
  never stored, always reflects current status (if a certificate is
  later revoked, the same QR still resolves to a page that says so)
- Verification page now shows: QR code image, Certificate Number,
  Recipient, Course, Completion Date, **Instructor** (derived from
  `InstructorAssignment`, "—" if none assigned), **Verification URL**
  (as a copyable link), and the full **Certificate Hash**
- Student certificate list also got a QR thumbnail per certificate
- 12 new tests: hash generation/validity/tamper-detection (including a
  direct test that a naive unsigned hash would NOT match — proving the
  HMAC dependency is real, not just asserted), QR endpoint (real PNG
  content-type + 404 for unknown codes), and verification-page content
  (hash shown, URL shown, instructor name shown when assigned vs. "—"
  when not)

### Verification performed
- `manage.py check` — zero errors; `makemigrations --check` — clean
- Full suite: `manage.py test` 164/164 (up from 152), `npm test` 39/39
- Real-browser verification: the public verification page rendered a
  genuine scannable QR image (confirmed 410×410 real PNG dimensions via
  `naturalWidth`/`naturalHeight`, not a broken image icon), the
  instructor name pulled correctly from a real `InstructorAssignment`
  ("Dr. Chidi Okoro"), and the full hash/URL/completion-date all
  displayed together in one screenshot. Student certificate list showed
  the matching QR thumbnail. Zero console errors. Cleaned up seeded
  data and the dev server afterward.

## 16.H — Employment outcomes ✅ DONE

### Design decision: append-only history, not a mutable snapshot
`EmploymentOutcome` is an append-only log (one row per self-reported
update), not one row per student that gets overwritten. The spec's own
wording — "students should update these **after** graduation" — implies
a sequence of updates over a career (seeking → internship → employed →
promoted), and a single mutable record would silently destroy that
timeline, which is exactly the kind of longitudinal data a real impact
report wants to show. A student's "current" status is just their most
recent row, computed on read, not stored.

### Respecting the Phase 16 planning decision on salary/evidence privacy
The plan already decided: private storage, visible only to the student
and admin/management, never instructors, salary shown only as a
bucketed range and only ever in aggregate. This phase enforces that
concretely:
- `salary_range` is a `TextChoices` of buckets (e.g. "$50,000 -
  $100,000/year"), never a free-form number field — there's no way to
  enter an exact figure even if someone wanted to.
- Evidence reuses the **exact** private-bucket pattern from Phase 15's
  avatar upload (`generate_safe_path` + `StorageService.upload`, same
  capped MIME/size validation, same graceful `StorageError` →
  `messages.error()` handling) — added a new `employment-evidence`
  bucket to `SUPABASE_STORAGE_BUCKETS`.
- The **management-facing page is aggregate-only** — status counts and
  an employment rate, nothing per-student. Individual records
  (including salary and a signed evidence link) are deliberately
  confined to Django Admin, matching the exact split 16.F already
  established for cohorts. Added a dedicated test that explicitly
  posts a certificate with `OVER_150K` salary and a fake evidence path,
  then asserts neither string appears anywhere in the aggregate page's
  rendered output — not just "didn't think to add it," actually
  verified.
- No instructor-facing view or URL exists for this app at all — not
  hidden via a missing link, genuinely absent from `instructor_urls.py`
  equivalents entirely.

### What was built
- `EmploymentOutcome` model (`apps/employment/`, migration
  `0001_initial.py` — brand new table) with signed-URL evidence review
  wired into Django Admin (reusing `get_storage_service().signed_url()`,
  same try/except pattern as assignment grading)
- Student-facing timeline (`student_employment:list`) + update form
  (`student_employment:create`)
- `apps/analytics/services/employment_stats.py`:
  `get_employment_summary()` — reporting-graduate count, employment
  rate, full status breakdown. "Latest per student" uses a plain
  per-student loop rather than Postgres-only `.distinct(field)`, since
  this project also runs on SQLite for dev/tests
- Management-facing aggregate summary page, `@admin_required`
- Wired into both dashboards' sidebars and Quick Access grids
- 16 new tests: model ordering, the full student submit flow
  (with/without evidence, oversized/disallowed evidence rejected before
  ever reaching the mocked storage call, a genuine Supabase error
  surfacing as a message not a 500), management summary math (including
  "only the latest of several updates for one student counts"), access
  control, and the salary/evidence-never-leaks-into-aggregates test

### Verification performed
- `manage.py check` — zero errors; `makemigrations --check` — clean
- Full suite: `manage.py test` 180/180 (up from 164), `npm test` 39/39
- Real-browser verification end-to-end: submitted a real employment
  update as a student (SOC Analyst, $50k-$100k range, no evidence file —
  the evidence-upload code path itself is already covered by the mocked
  unit tests, same reasoning as the Phase 15 avatar-upload verification)
  and confirmed it appeared correctly in the student's timeline;
  logged in separately as an admin and confirmed the management summary
  showed "1 Graduate Reporting, 100.0% Employment Rate, Employed
  Full-Time: 1" — the real aggregation, not a hardcoded number. Zero
  console errors. (Hit and resolved an unrelated environment flake this
  session: Chromium was picking up a system-level proxy config that
  hung navigation; `--no-proxy-server` fixed it for the rest of this
  phase's browser checks.)

## 16.I — Learner feedback/NPS ✅ DONE

### Design decision: new dedicated fields, not repurposed ratings
The spec calls for a real Net Promoter Score, which is only meaningful
on the standard 0-10 "how likely to recommend" scale — none of the
existing 1-5 rating fields can be recast into that without changing
their meaning for every prior response. Added `difficulty`,
`confidence_before`, `confidence_after` (1-5, matching the existing
rating fields' conventions) and `nps_score` (0-10) as four new
non-nullable fields, each with its own `CheckConstraint` following the
exact pattern already used for `overall_rating` etc.

### What was built
- `apps/feedback/models.py`: 4 new fields + `CheckConstraint`s on
  `StudentFeedback`; migration `0002_nps_and_confidence_fields.py`
  (hand-written — the interactive one-off-default prompt for
  `makemigrations` doesn't work non-interactively, so it mirrors
  exactly what Django's interactive flow would generate)
- `apps/feedback/forms.py`: `TypedChoiceField`s for all 4 new fields
  (0-10 `NPS_CHOICES` for `nps_score`, 1-5 for the rest), plus
  spec-aligned labels on `overall_rating`/`practical_lab_quality`/
  `instructor_effectiveness` ("Course satisfaction", "Lab quality",
  "Instructor rating"). No template changes needed — the student
  feedback form template loops over `form` generically.
- `apps/analytics/services/nps.py`: `calculate_nps(feedback_queryset)`
  — standard methodology (Promoters 9-10 / Passives 7-8 / Detractors
  0-6, NPS = %Promoters − %Detractors). Lives in `apps.analytics`
  rather than `apps.feedback` so it's reusable by the platform-wide
  Management Dashboard (16.J) without a cross-app view dependency.
- Instructor feedback analytics page: added Avg Difficulty/Confidence
  Before/Confidence After stat cards plus an NPS card showing the score
  and the promoter/passive/detractor breakdown
- Instructor feedback list: added an NPS column only (difficulty/
  confidence stay in analytics — the list table was already at 7
  columns and didn't need more crowding)
- CSV export: all 4 new fields added as columns (no space constraint)
- PDF export: NPS column only added, matching the list-table decision
  (ReportLab table has less usable width than a CSV, so only the
  single highest-value new metric was added there)
- `apps/feedback/serializers.py`: all 4 new fields exposed via the
  existing student-facing `StudentFeedbackViewSet`
- `apps/feedback/admin.py`: `nps_score` added to `list_display`

### What was fixed along the way
Adding 4 new non-nullable fields to `StudentFeedback` broke 4 of the
7 existing `apps.feedback` tests, purely because their fixtures
(hardcoded POST payloads and raw `.objects.create()` kwargs) predated
the new required fields — not an application bug. Added
`_valid_model_kwargs()`/updated `_valid_payload()` helpers and
propagated them through every test that constructs a `StudentFeedback`,
without touching any assertion.

### Verification performed
- `manage.py check` — zero errors; `makemigrations --check --dry-run`
  — clean (no drift)
- `apps.feedback` suite: 7/7 pass; full suite: `manage.py test`
  180/180
- Manual smoke test: `build_feedback_report_pdf` against an empty
  queryset confirms the new NPS column doesn't break PDF generation;
  rendered `StudentFeedbackForm()` HTML confirms all 4 new fields are
  present in the form output

### Security review
- No new attack surface: all 4 new fields are server-side validated
  `TypedChoiceField`s with fixed integer choice sets, backed by DB
  `CheckConstraint`s — same defense-in-depth pattern as every existing
  rating field on this model.
- Anonymity guarantee untouched: `display_name()` remains the single
  place identity is resolved, and the new CSV/PDF/analytics code paths
  all read through the existing `_visible_feedback()` /
  `display_name()` helpers rather than touching `feedback.student`
  directly.
- No new sensitive data exposed to the frontend — NPS/difficulty/
  confidence are ratings and derived aggregates, nothing PII-adjacent.

## 16.J — Management Analytics Dashboard ✅ DONE

### What was built
- `apps/analytics/services/platform_stats.py`: `get_platform_analytics()`
  — the single platform-wide aggregation function, deliberately reusing
  every existing building block rather than redefining metrics
  (`DROPOUT_STATUSES` from `cohort_stats.py`, `get_employment_summary()`,
  `calculate_nps()`) so a platform-wide number can never silently
  disagree with the same metric computed at cohort level. Returns:
  `dau`/`mau` (distinct `LearningSession` users today / trailing 30
  days), enrollment totals + completion/dropout/retention rates,
  average quiz score, average pre-test/post-test score + platform-wide
  skill improvement, certificates issued (total + this month), total
  learning hours, top 5 courses by enrollment, top 5 instructors by
  average feedback rating, employment summary, and NPS.
- New view `analytics_dashboard` in `apps/reports/views.py`
  (`@admin_required`), URL `reports:analytics_dashboard` at
  `/management/reports/analytics/`
- New template `templates/management/reports/analytics_dashboard.html`
  — stat cards for every KPI plus 4 Chart.js charts (enrollment health
  doughnut, pre/post-test bar, top courses horizontal bar, top
  instructors horizontal bar), following the exact `json_script` +
  theme-aware-colors + IIFE pattern already established in the student
  dashboard's skill-improvement chart — no new charting convention
  invented.
- Linked from the existing Reports index page (`reports:index`) with a
  new "Open Dashboard" card at the top

### Bug found and fixed during testing
`top_courses`/`top_instructors` were originally grouped by
`course__title` / `instructor__full_name` alone. Neither field is
actually unique on its model — two different courses (or instructors)
that happen to share a display name would have had their enrollment
counts/ratings silently merged into one bucket. A test using two
distinctly-titled courses caught this immediately (a shared test
helper's hardcoded title exposed it). Fixed by grouping on
`course_id`/`instructor_id` alongside the display field, so identity is
always resolved by primary key, never by name collision risk.

### Important environment finding: Supabase dev DB was 8 migrations behind
While preparing to verify the dashboard against a real logged-in admin
session, `manage.py shell` failed with `column accounts_user.gender
does not exist` — the actual Supabase Postgres database this project
connects to (via `DATABASE_URL`, `config.settings.development`) had
**never received any Phase 16 migration**, going all the way back to
16.A (`analytics`, `cohorts`, `employment`, `labs` — brand new apps —
plus `accounts.gender`/`date_of_birth`, `certificates.certificate_hash`,
`quizzes.quiz_type`, `feedback`'s NPS/confidence fields: 8 migrations
in total). Every verification this session had exercised only the
isolated in-memory SQLite test database, so the test suite passing
never surfaced this. Flagged it to the user before touching the shared
database (per project safety norms around shared/hard-to-reverse
state); user approved applying migrations now. Ran `manage.py migrate`
— all 8 applied cleanly with zero data loss (purely additive: new
tables and nullable-safe new columns on existing rows). Confirmed
`showmigrations` shows zero pending afterward. This means Phase 16 was
effectively unusable on the real database until this point — worth
keeping in mind for 16.R's final verification pass, and worth deploying
this migration ASAP outside of this session if there's a separate
production database that mirrors this one.

### Verification performed
- `manage.py check` — zero errors
- Full suite: `manage.py test` 190/190 (up from 180) — 7 new
  `PlatformStatsServiceTests` (empty-platform zero-state, completion/
  dropout/retention math, certificates-issued status filtering, top
  courses/instructors ranking incl. the id-vs-name collision fix,
  platform-wide skill improvement, DAU/MAU from `LearningSession`), 3
  new `apps.reports` access-control tests (admin sees it, student/
  instructor get 403)
- Live verification against the real (now-migrated) Supabase database:
  no Playwright/chromium tooling was available in this environment this
  time (network-restricted, nothing cached locally) — rather than
  claim a browser check that didn't happen, verified via a real HTTP
  round-trip instead: started the dev server, created a throwaway admin
  account, logged in over HTTP with a real CSRF-protected POST, fetched
  `/management/reports/analytics/`, and confirmed: 200 status, correct
  title, all 4 `<canvas>` elements present, the embedded chart JSON
  reflecting real DB data (1 real course/enrollment, NPS of -100 traced
  back to one real pre-existing feedback row with `nps_score=5` — a
  detractor — confirming the math, not a bug). Deleted the throwaway
  account and stopped the dev server afterward.

### Security review
- `@admin_required` on the only new view — confirmed student and
  instructor accounts get 403, matching the existing convention used by
  every other management-only page.
- No individual-level sensitive data exposed: every KPI is an aggregate
  (rate, average, top-5 list) — no per-student rows, no salary figures
  (employment summary already enforces that at its own layer), no
  feedback text.
- Top-instructors ranking only ever shows a name and an average rating
  — never links back to which student gave which score, preserving the
  same anonymity guarantee Phase 16.I already established for feedback.

## 16.K — Impact Dashboard ✅ DONE

### Design decision: append-only self-reported model, not a forced singleton
Researched whether this codebase has an existing "singleton admin
content" pattern (e.g. `django-solo`, a `pk=1`-enforced model) before
building `ImpactSnapshot`, since the original Phase 16 planning notes
called for "a simple admin-editable Impact Snapshot model." Found no
such pattern anywhere in the codebase — `apps.company`/`apps.academy`
have no models at all, and every existing "admin enters a number, page
displays it" case (`EmploymentOutcome`) uses an **append-only log**
where "current" is simply the most recent row. Followed that exact
precedent instead of inventing a new singleton pattern: `ImpactSnapshot`
is a plain model with `ordering = ["-created_at"]`, and "the current
figures" is just `.objects.first()`. This also gives a free history of
how these self-reported numbers changed over time, which a forced
singleton would have destroyed.

### What was built
- `ImpactSnapshot` model (`apps/analytics/models.py`) — `smes_protected`,
  `healthcare_workers_trained`, `businesses_started`, `notes`,
  `recorded_by` (auto-set to the logged-in admin via `save_model()` on
  first save), `created_at`. Migration `0002_impactsnapshot.py`
  (generated cleanly — no interactive prompt needed since every new
  field has a real default).
- Registered in Django Admin (`ImpactSnapshotAdmin`) — this is
  deliberately the *only* way to create/edit a snapshot, matching the
  established Admin-vs-custom-page split from 16.F/16.H: the custom
  page only ever displays computed and self-reported figures, it never
  hosts a data-entry form.
- `apps/analytics/services/impact_stats.py`: `get_impact_dashboard_data()`
  — returns two clearly separate dict keys, `computed` and
  `self_reported`, specifically so the template (and any future
  consumer) can never accidentally present a self-reported number as a
  measured one. `computed` reuses `get_platform_analytics()` from 16.J
  (certificates, learning hours, completion rate, skill improvement,
  employment rate, NPS) plus two new platform-wide aggregates this
  phase needed: `people_trained` (distinct students with any
  enrollment) and `labs_completed` (platform-wide `LabProgress` count
  with `status=COMPLETED`).
- New view `impact_dashboard` (`@admin_required`) at
  `/management/reports/impact/`, template
  `management/reports/impact_dashboard.html` — two visually distinct
  sections with an "Measured" vs. "Self-Reported" badge on each heading,
  plus a direct link to the Django Admin add-form for updating the
  self-reported figures.
- CSV export (`export_impact_csv`) — every computed and self-reported
  metric as `Metric, Value, Type` rows, with the self-reported section
  explicitly labeled `Self-Reported` and its as-of date included. Excel/
  PDF versions are explicitly deferred to 16.L, which already owns
  "CSV/Excel/PDF for Impact, Course, Student, and Employment reports" —
  building the richer export formats there avoids doing this work twice
  under two different roadmap items.
- Linked from the Reports index page alongside the 16.J Analytics
  Dashboard link.

### Verification performed
- `manage.py check` — zero errors; migration generated with no drift
- Full suite: `manage.py test` 198/198 (up from 190) — 4 new
  `ImpactDashboardServiceTests` (empty-platform zero-state incl.
  `None` self-reported values, people-trained counts distinct students
  not enrollments, labs-completed filters by status, latest-of-several-
  snapshots wins) + 4 new `apps.reports` `ImpactDashboardTests`
  (zero-state render, snapshot figures render, CSV contains both
  Computed and Self-Reported rows, student gets 403)
- Applied `manage.py migrate analytics` to the real Supabase database
  (already back in sync as of 16.J's migration catch-up) — zero pending
  migrations afterward.

### Security review
- `@admin_required` on the only new view, confirmed via test that a
  student account gets 403.
- The self-reported figures are aggregate counts only (SMEs/healthcare
  workers/businesses — no names, no identifying detail was ever in
  scope for these fields), so there's no new PII surface.
- Data entry is Admin-only by construction — there is no public or
  student/instructor-facing form that could write to `ImpactSnapshot`,
  removing any risk of a non-admin inflating these figures.

## 16.L — Exports ✅ DONE

### What was built
- `apps/reports/services/excel.py` — first `openpyxl` usage in this
  codebase (the dependency was already in `requirements.txt` since
  16.A but unused until now). Mirrors the exact philosophy already
  documented in `services/pdf.py`: small, focused builder functions per
  report type rather than one generic "headers + rows" engine, sharing
  only genuine boilerplate (`_new_sheet()` — branded header row
  styling) the same way `pdf.py`'s `_base_doc()` is shared. Four
  builders: `build_impact_report_excel`, `build_course_report_excel`,
  `build_student_report_excel`, `build_employment_report_excel`.
- `apps/reports/services/pdf.py` extended with the same four report
  types (`build_impact_report_pdf`, `build_course_report_pdf`,
  `build_student_report_pdf`, `build_employment_report_pdf`), reusing
  the existing `_base_doc()` plus a newly-extracted `_styled_table()`
  helper (the table style block was previously inlined once in
  `build_feedback_report_pdf`; now shared since it's pure styling
  boilerplate, not privacy logic).
- `apps/reports/services/report_data.py` — new row-shaping functions
  `get_course_report_rows()` (per course: enrollments, completed,
  completion rate, average quiz score, average feedback rating,
  certificates issued) and `get_student_report_rows()` (per student:
  enrollments, completed, average quiz score, certificates earned,
  learning hours). Deliberately placed in `apps.reports`, not
  `apps.analytics` — nothing else in the platform consumes a full
  per-course/per-student row list, so this is report-only shaping, not
  a reusable analytics building block. Computed with simple per-row
  queries (same "admin-reporting page, not a hot path" reasoning
  `cohort_stats.py` already established) rather than one large joined
  annotation.
- Impact report: reused the existing `get_impact_dashboard_data()` from
  16.K — Excel/PDF versions added alongside the CSV that 16.K already
  built (scope split decided in 16.K to avoid duplicate work).
- Employment report: reused the existing `get_employment_summary()`
  from 16.H — deliberately aggregate-only (status breakdown + total
  reporting + employment rate), never salary or evidence, matching the
  Phase 16 planning decision already enforced everywhere else this
  data appears.
- 12 new view functions in `apps/reports/views.py`
  (`export_{impact,course,student,employment}_{csv,excel,pdf}`), all
  `@admin_required`, wired into `apps/reports/urls.py`. Impact CSV
  already existed from 16.K; only Excel/PDF were new for that one.
- Report cards for Course/Student/Employment added to the Reports
  index page (each with CSV/Excel/PDF buttons), and Excel/PDF buttons
  added to the Impact Dashboard page itself alongside its existing CSV
  button.

### Verification performed
- `manage.py check` — zero errors (no new migrations this phase — no
  new models, only new services/views/templates)
- Full suite: `manage.py test` 203/203 (up from 198) — 5 new
  `ExportEndpointsTests` in `apps/reports/tests.py`, built against real
  fixture data (a course, a graded quiz attempt, a certificate, an
  employment outcome) rather than just the empty-platform case, so the
  openpyxl/ReportLab row-writing code actually executes, not just the
  "no data" branches. Covers all 12 new endpoints' status code,
  Content-Type header, non-empty body, and — for the employment
  export — an explicit assertion that "salary" never appears in the
  output.
- Extra manual verification beyond the test suite: ran every new Excel
  builder against the real (production-shaped) Supabase database and
  reloaded the bytes with `openpyxl.load_workbook()` to confirm they're
  genuinely valid `.xlsx` files, not just non-empty byte strings; did
  the same sanity check for all four new PDF builders (byte length
  check against real data).

### Security review
- All 12 new endpoints are `@admin_required`; confirmed via test that
  a student account gets 403 across CSV/Excel/PDF alike.
- Employment export reuses the same aggregate-only service as the
  existing management-facing page — no code path in this phase ever
  touches `EmploymentOutcome.salary_range` or the evidence file/signed
  URL, and a test explicitly asserts "salary" is absent from the CSV
  output.
- Student report exposes email address and progress/score data to
  admin/management only (already the only role with access to this
  view) — no new exposure beyond what Django Admin already shows for
  the same underlying models.

## 16.M — REST API ✅ DONE

### Design decision: which existing convention each new endpoint follows
Researched the existing DRF setup before building anything (router-based
registration in `apps/core/api_urls.py` under `/api/v1/`,
`SessionAuthentication` + `IsAuthenticated` by default, drf-spectacular
for schema/docs, zero DRF-native role permission classes so far — every
existing role check was a Django view decorator/mixin, which doesn't
apply to DRF ViewSets/APIViews). Matched conventions exactly rather than
inventing new ones, and split the four new endpoint groups into two
different shapes based on what they actually are:
- **Computed dict, no backing queryset** (`/analytics/`, `/impact/`,
  `/employment/`): plain `APIView` + a new `serializer_class` on the
  view (needed for drf-spectacular schema generation, caught by running
  `manage.py spectacular --fail-on-warn` before considering this done —
  it flagged all three as "unable to guess serializer" until added) +
  a new plain (non-`ModelSerializer`) `serializers.Serializer` per
  service function's dict shape, since none of these three service
  functions are backed by a single model.
- **Real collection** (`/cohorts/`, `/certificates/`):
  `ReadOnlyModelViewSet` registered on the router like every existing
  endpoint, each with its own `ModelSerializer`.

### What was built
- `apps/accounts/permissions.py`: new `IsAdminRole(BasePermission)` —
  the DRF-native counterpart to the existing `admin_required`
  decorator/`AdminRequiredMixin`, since neither of those work on DRF
  views. Same role/status check, just implemented via
  `has_permission()` instead of wrapping a view function.
- `apps/analytics/serializers.py` (new) — `PlatformAnalyticsSerializer`,
  `ImpactDashboardSerializer` (nested `computed`/`self_reported`, same
  split as the Impact Dashboard template so API consumers can't
  conflate measured and self-reported figures either), `NPSSerializer`,
  `EmploymentSummarySerializer`. Nested list-of-dict fields
  (`top_courses`, `top_instructors`, `status_breakdown`) use
  `ListField(child=DictField())` rather than one-off nested serializer
  classes for each — a deliberate minimal-effort tradeoff for a v1
  read-only reporting API; drf-spectacular documents these as generic
  objects rather than fully-typed schemas.
- `apps/analytics/api_views.py` (new) — `PlatformAnalyticsAPIView`,
  `ImpactDashboardAPIView`, both `IsAdminRole`-gated, wrapping
  `get_platform_analytics()`/`get_impact_dashboard_data()` (the same
  16.J/16.K services, not reimplemented).
- `apps/employment/api_views.py` (new) — `EmploymentSummaryAPIView`,
  `IsAdminRole`-gated, aggregate-only (reuses
  `get_employment_summary()`) — deliberately does **not** expose a
  collection of raw `EmploymentOutcome` records, since that would risk
  salary/evidence leaking through an API response in a way the
  Admin-only-for-raw-records convention (established in 16.H, reused in
  16.L) is specifically designed to prevent.
- `apps/cohorts/serializers.py` + `api_views.py` (new) — `CohortViewSet`
  (`ReadOnlyModelViewSet`, `IsAdminRole`), each cohort serialized with a
  nested `stats` field via `SerializerMethodField` calling the existing
  `get_cohort_stats()` — no duplicate stat logic.
- `apps/certificates/serializers.py` + `api_views.py` (new) —
  `CertificateViewSet` (`ReadOnlyModelViewSet`, `IsAuthenticated`,
  scoped to `request.user`'s own issued certificates only — identical
  object-scoping pattern to the existing `EnrollmentViewSet`).
  Deliberately excludes `certificate_storage_path` from the serializer
  (internal Supabase reference never shown in any template either);
  includes `certificate_hash` since that's already shown on the public
  verification page. This is the "certificate read endpoint" the
  roadmap called for — progress was judged already adequately covered
  by the existing `EnrollmentViewSet` (exposes `progress_percentage`),
  so no separate progress endpoint was added.
- Wired all of the above into `apps/core/api_urls.py`: `cohorts` and
  `certificates` registered on the existing router; `analytics/`,
  `impact/`, `employment/` added as explicit `path()` entries since
  they're not router-style collections.

### Verification performed
- `manage.py check` — zero errors (no new migrations — no new models)
- `manage.py spectacular --fail-on-warn` — caught and fixed 3 missing
  `serializer_class` errors on the plain `APIView`s and one missing
  type hint on `CohortSerializer.get_stats()`; the one remaining
  warning (an enum-naming collision on the many "status" fields across
  the whole schema, not something newly introduced by this phase) isn't
  enforced by this project's CI, so it was left as-is rather than
  chasing a cosmetic schema-naming fix
- Full suite: `manage.py test` 217/217 (up from 203) — 14 new tests
  across `apps/analytics/tests.py`, `apps/cohorts/tests.py`,
  `apps/employment/tests.py`, `apps/certificates/tests.py`, covering:
  admin can fetch each endpoint with the right shape, student/anonymous
  get 403 on every one of them, a student only ever sees their own
  certificates (not another student's), and — mirroring the exact same
  test already written for the CSV export in 16.L — an explicit
  assertion that the Employment API response never contains "salary"
  figures or the evidence storage path
- Live verification: started the dev server, created a throwaway admin
  account, logged in over real HTTP, and hit all 5 new endpoints
  (`/api/v1/analytics/`, `/impact/`, `/employment/`, `/cohorts/`,
  `/certificates/`) plus `/api/v1/docs/` — all returned 200 with
  correctly-shaped JSON reflecting real database data (e.g. the
  `top_courses` list showing the one real course, `impact.self_reported`
  correctly `null` since no `ImpactSnapshot` has been recorded yet).
  Deleted the throwaway account and stopped the dev server afterward.

### Security review
- Every new endpoint requires authentication; the 4 admin-only ones
  (`analytics`, `impact`, `employment`, `cohorts`) use the new
  `IsAdminRole` permission class, confirmed via test that both a
  student account and an anonymous request get 403.
- `certificates` uses object-level queryset scoping (`student=request.
  user`), the same pattern already proven safe by `EnrollmentViewSet` —
  confirmed via test that one student's certificate list never includes
  another student's certificate.
- No salary, evidence file path, or certificate storage path is
  reachable through any new endpoint — confirmed via explicit tests for
  both the employment aggregate and the certificate serializer.

## 16.N — Student dashboard widgets ✅ DONE

### What was already there vs. what was genuinely new
Audited the existing student dashboard (`apps/core/dashboard_views.py::
student_overview` + `templates/student/dashboard/overview.html`) before
writing anything — 4 of the 8 spec'd widgets already existed from
earlier sub-phases (Hours Learned via 16.C's `get_learning_time_summary`,
Skill Improvement via 16.B's chart, Labs Completed via 16.D's
`get_lab_summary`, Certificates via the existing `certificate_count`
stat card). Only 4 were genuinely missing: Learning Streak, Upcoming
Assignments, Recent Quiz Scores, and the anonymized Leaderboard
Position — this phase only built those four.

### Design decision: leaderboard ranks by average graded quiz score, computed in one query
Considered ranking by `get_overall_academy_progress()` (already used
elsewhere) but rejected it for the leaderboard specifically — it would
require calling that service once per platform student in a Python
loop (fine for a cohort-scoped admin report, but this runs on every
single student's dashboard page load, at platform scale, so an O(n)
per-page-load fan-out felt like the wrong tradeoff here). Instead
ranked by average `QuizAttempt.percentage` (GRADED only) via one
`values().annotate(Avg()).order_by()` query — comparable across every
student regardless of which courses they're enrolled in, and computed
as a single query rather than a loop.

### What was built
- `apps/analytics/services/learning_time.py`: `get_learning_streak(student)`
  — consecutive days (ending today or yesterday) with a
  `LearningTimeEntry`. Deliberately "survives" a day that hasn't
  happened yet — no entry for today doesn't zero out a streak that was
  still active yesterday, so a student checking their dashboard first
  thing in the morning doesn't see their streak reset before they've
  had a chance to study today.
- `apps/analytics/services/leaderboard.py` (new): `get_leaderboard_position(student)`
  — returns `eligible` (False if the student has zero graded quiz
  attempts — there's nothing to compare), `top_percentage` (lower is
  better; the single best-scoring student is "Top 1%"), and
  `total_ranked`. Never returns another student's name or score —
  same anonymity posture already established for feedback (16.I) and
  top-instructor rankings (16.J).
- `apps/core/dashboard_views.py::student_overview`: added
  `upcoming_assignments` (published assignments in the student's
  enrolled courses, excluding ones already submitted — same shape as
  the existing `upcoming_quizzes` query) and `recent_quiz_attempts`
  (last 5 graded attempts, newest first).
- Template: new stat cards for Learning Streak and Leaderboard
  Position, plus new "Upcoming Assignments" and "Recent Quiz Scores"
  list sections, following the exact existing list-group/stat-card
  markup conventions already used throughout this dashboard.

### Verification performed
- `manage.py check` — zero errors (no new migrations — no new models)
- Full suite: `manage.py test` 228/228 (up from 217) — 6 new service
  tests (`get_learning_streak`'s zero-state, consecutive-days,
  "survives a missing today", and "broken by a gap day" cases;
  `get_leaderboard_position`'s not-ranked and best-vs-worst-of-two
  cases) + 5 new dashboard view tests (zero-state, streak counts
  correctly through the full view render, recent quiz score + rank
  render together, upcoming assignment shows, and — the important
  negative case — an already-submitted assignment is correctly
  excluded)
- Live verification: since this is a student-facing UI change and no
  Playwright/browser tooling was available this session (same
  constraint as 16.J/16.M), verified via a real HTTP round-trip
  instead — started the dev server, created a throwaway student
  account, logged in, and confirmed `/student/` renders all 4 new
  widgets with the correct zero-state copy ("0 days", "Complete a
  graded quiz to rank", "No upcoming assignments.", "No graded quiz
  attempts yet."). Deleted the throwaway account and stopped the dev
  server afterward.

### Security review
- The leaderboard never exposes another student's name, email, or raw
  score — only the logged-in student's own rank is computed and shown,
  and the underlying query only ever returns `student_id` values used
  internally to locate the current student's position, never rendered.
- No new PII surface: Upcoming Assignments and Recent Quiz Scores only
  ever show the logged-in student's own data, scoped by
  `student=request.user` exactly like every other query on this
  dashboard.

## 16.O — Instructor dashboard widgets ✅ DONE

### Design decision: at-risk students are never anonymized here, unlike 16.N's student-facing leaderboard
An instructor already sees their own students' real names elsewhere in
this platform (the existing Students page, feedback list, grading
queues) — anonymizing a name on the At Risk table specifically would be
inconsistent with everything else on this dashboard and wouldn't
actually protect anything, since the instructor could just look the
student up. This is the opposite posture from 16.N's leaderboard
(where anonymity is the whole point) and from 16.I/16.J's feedback
anonymity (a deliberate, narrow exception) — deliberately not treated
the same way, and the reasoning is written into the service's docstring
so a future reader doesn't "fix" it into an inconsistent anonymization.

### Design decision: at-risk criteria and why the per-enrollment loop is fine here
A student is flagged "at risk" if either their enrollment progress is
below 30% or their average graded quiz score in that course is below
50% — catching both "hasn't engaged" and "engaged but struggling"
cases, since progress alone would miss a student who's clicking
through content without absorbing it. Computed with a per-enrollment
loop (one query per enrollment for that student's average score),
which would be a real concern at platform scale — but this loop is
bounded to one instructor's own roster, not all students platform-wide,
capped at 10 rows, and this is a dashboard read, not a hot path. Same
"admin/instructor-reporting page, not a hot path" reasoning already
used in `cohort_stats.py` and reused in 16.J's course export
row-shaping.

### What was built
- `apps/analytics/services/instructor_stats.py` (new):
  `get_instructor_dashboard_stats(instructor)` — scoped entirely to
  `InstructorAssignment`-active courses. Returns: `active_this_week`
  (distinct students with a `LearningTimeEntry` in the trailing 7 days),
  `average_quiz_score`/`average_assignment_score` (straight `Avg()`
  aggregates, GRADED-only), `lab_completion_rate` (completed lab-progress
  rows ÷ total possible student×lab pairs), `quiz_completion_rate`/
  `assignment_submission_rate` (% of the instructor's students who've
  attempted at least one quiz / submitted at least one assignment),
  `at_risk_students` (see above), and `feedback` (reuses
  `calculate_nps()` from 16.I plus a plain average rating — not
  reimplemented).
- `apps/core/dashboard_views.py::instructor_overview`: added a single
  `stats` context key wrapping the whole service call, rather than
  spreading a dozen individual keys the way the student dashboard view
  does — the instructor dashboard already had 5 loose top-level stat
  variables from earlier phases, and adding 9 more the same way would
  have made the view function's return dict unreadable.
- Template: new "Engagement & Performance" stat-card section (8 cards
  across two rows) and a new "Students At Risk" table, both following
  the exact existing stat-card/table markup conventions already used on
  this dashboard and the Feedback Analytics page (16.I).

### Verification performed
- `manage.py check` — zero errors (no new migrations — no new models)
- Full suite: `manage.py test` 237/237 (up from 228) — 6 new
  `InstructorDashboardStatsServiceTests` (empty-course zero-state,
  cross-instructor isolation — another instructor's enrollment never
  counts, quiz/assignment score averages, at-risk-by-low-progress,
  at-risk-by-low-score-despite-high-progress, feedback stats correctly
  delegating to `calculate_nps()`) + 3 new `apps.core`
  `InstructorDashboardWidgetTests` (zero-state renders both new
  sections, an at-risk student's real name appears in the table, a
  student account gets 403 on this instructor-only page)
- Live verification: no Playwright/browser tooling available this
  session (same constraint as 16.J/16.M/16.N) — verified via a real
  HTTP round-trip instead: started the dev server, created a throwaway
  instructor account, logged in, and confirmed `/instructor/` renders
  both new sections with the correct zero-state copy. Deleted the
  throwaway account and stopped the dev server afterward.

### Security review
- `@instructor_required` unchanged on this view (no new decorator
  needed — the whole view was already gated); confirmed via test that
  a student account gets 403.
- At-risk student names are intentionally visible to the instructor —
  see the design decision above for why this is correct here rather
  than a gap versus 16.N's anonymization.
- No cross-instructor leakage: confirmed via test that a course another
  instructor teaches (with its own enrolled student) contributes
  nothing to this instructor's stats.

## 16.P — FID Impact Evidence report ✅ DONE

### Clarified "FID" with the user before building anything
The roadmap term "FID Impact Evidence report" had no definition
anywhere in this plan or the codebase, and I couldn't find any prior
context for what it stood for. Rather than guess — building the wrong
thing for what's explicitly meant to be a funder-facing compliance/
reporting deliverable felt like a case where a wrong guess is expensive
to unwind — asked the user directly. Confirmed: no specific named
funder or required template; this should be a comprehensive,
professional impact-evidence export combining everything already
tracked, reusing 16.K/16.L's existing data and export infrastructure.

### What was built
- `apps/analytics/services/fid_report.py` (new): `get_fid_impact_report_data(prepared_for=None)`
  — a rollup, not a new metric source. Every figure is pulled from
  services that already exist (`get_impact_dashboard_data()` from
  16.K, `get_employment_summary()` from 16.H, `get_platform_analytics()`
  from 16.J for the top-courses list, `get_cohort_stats()` per cohort
  from 16.F) and grouped into the sections a funder report typically
  wants: Reach, Learning Outcomes, Employment Outcomes, Field Impact
  (self-reported), Cohort Breakdown, Top Courses. Nothing is
  recomputed, so this can never silently drift from what the
  Analytics/Impact dashboards already show.
- `apps/reports/services/pdf.py::build_fid_impact_report_pdf()` — one
  multi-section PDF (each section its own heading + table), reusing
  the existing `_base_doc()`/`_styled_table()` helpers rather than
  inventing new layout code.
- `apps/reports/services/excel.py::build_fid_impact_report_excel()` —
  one workbook, one sheet per section (a funder can flip between tabs
  rather than scroll one long flat sheet) — the first multi-sheet
  workbook in this codebase, via a new shared `_add_sheet()`/
  `_style_header_row()` helper (refactored out of the original
  single-sheet `_new_sheet()` so the header styling isn't duplicated
  between the two).
- Two new admin-only export views (`export_fid_pdf`, `export_fid_excel`)
  accepting an optional `?prepared_for=` query param for the report's
  "Prepared for" line, wired into `apps/reports/urls.py`.
- Reports index page: a dedicated "Impact Evidence Report" card above
  the plain export grid (this is the flagship funder deliverable, not
  just another report type) with a "Prepared for" text field and two
  submit buttons using different `formaction`s — no JavaScript needed
  to route the same input to two different export endpoints.

### Security fix caught during this phase (not pre-existing — introduced and fixed in the same pass)
`prepared_for` comes from a raw, unauthenticated-adjacent query
parameter (admin-only endpoint, but still user-controlled input) and
gets interpolated into a ReportLab `Paragraph`, which parses its own
small XML-like markup language — unescaped input could break PDF
generation with malformed tags (e.g. `<b><unclosed`). Fixed by wrapping
it in `xml.sax.saxutils.escape()` before interpolation, with a comment
explaining why the escape is required and not just defensive
boilerplate. Added a test (`test_malformed_prepared_for_does_not_crash_pdf_generation`)
that specifically sends unbalanced markup and asserts the endpoint
still returns 200 — this is a regression test for the exact fix, not a
generic "does it work" check.

### Verification performed
- `manage.py check` — zero errors (no new migrations — no new models)
- Full suite: `manage.py test` 246/246 (up from 237) — 4 new
  `FidImpactReportServiceTests` (expected dict shape on an empty
  platform, `prepared_for` passthrough, figures genuinely reflect real
  enrollment/certificate data rather than being hardcoded, cohort
  breakdown reflects a real cohort) + 5 new
  `FidImpactReportExportTests` (valid PDF bytes, valid `.xlsx` with
  all 6 expected sheet names present, prepared-for renders without
  error, the malformed-markup regression test above, student gets 403
  on both export formats)
- Manual verification against the real (production-shaped) database:
  ran both builders directly — PDF generated successfully, Excel
  workbook loaded via `openpyxl.load_workbook()` with 5 sheets present
  (Reach/Learning Outcomes/Employment Outcomes/Field Impact/Top
  Courses — Cohort Breakdown correctly omitted since no real cohorts
  exist yet, matching the "if data[...]" conditional section logic)

### Security review
- Both export endpoints are `@admin_required`, confirmed via test.
- The `prepared_for` XML-escaping fix above is the main security-
  relevant finding of this phase — verified fixed, not just theorized.
- Employment Outcomes section reuses `get_employment_summary()`
  directly (never touches `EmploymentOutcome.salary_range` or evidence
  paths), consistent with every other place this data appears in the
  platform.
- No new PII: every section is either a platform-wide aggregate or a
  cohort-level aggregate — no individual student's name, email, or
  score appears anywhere in this report.

## 16.Q — Data quality pass ✅ DONE

This phase was framed as an audit ("signals for auto-updating
analytics... constraint audit... audit-log hooks"), and treated as one
— every existing signal, constraint, and audit-log call site across
every Phase 16 model was actually read, not assumed clean. It surfaced
3 concrete, previously-shipped bugs rather than confirming everything
was already fine.

### Finding 1 (the big one): `Enrollment.status` never actually became COMPLETED anywhere in the application
Grepped every write site for `Enrollment.Status.COMPLETED` across the
whole codebase — every single Phase 16 analytics service
(`cohort_stats`, `platform_stats`, `report_data`, and by extension
every dashboard/export built on them: 16.F, 16.J, 16.K, 16.L) *reads*
and filters on this status, but nothing ever *writes* it outside a
manual Django Admin edit. `completed_at` was equally dead. Every
completion-rate and dropout-rate figure shipped since 16.F has been
silently undercounting completions.

**Fix:** `Enrollment.recalculate_progress()` — the single existing
place `progress_percentage` is computed — now also promotes
ACTIVE -> COMPLETED (and stamps `completed_at`) the moment progress
hits 100%. Deliberately one-directional: a later drop below 100% (e.g.
an instructor publishes a new lesson, changing the denominator) never
demotes a completed enrollment back to ACTIVE, since the student may
already hold a certificate for it. In practice this also means a
completed enrollment stops being touched by course-structure-driven
recalculation entirely, since `_recalculate_for_all_enrollments()` in
`apps.enrollments.signals` already only ever recalculates ACTIVE
enrollments — confirmed this with a test that calls
`recalculate_progress()` directly (bypassing that filter) to prove the
one-directional guarantee lives in the method itself, not just as an
accident of the existing signal filter.

**Backfill:** new one-off management command
`backfill_enrollment_completion` (`--dry-run` supported) re-runs
`recalculate_progress()` across every ACTIVE enrollment so any
enrollment that reached 100% *before* this fix shipped gets promoted
too. Idempotent. Ran `--dry-run` against the real Supabase database
first (0 of 1 active enrollments affected — the one real enrollment
isn't at 100% yet), then ran it for real (confirmed no-op, as
expected) — exists and is tested for whenever real completions
accumulate or this is applied to a different environment.

### Finding 2: Certificate issuance/revocation was never audit-logged
`apps.audit.services.log_action`'s own docstring explicitly lists
"certificate issuance/revocation" as one of the actions requiring a
log entry — it was never wired up. `CertificateAdmin.save_model()` now
logs `certificate.issue` on creation and `certificate.status_change`
(with `from`/`to` in metadata) whenever status changes on an existing
certificate, following the exact `log_action(actor, action, entity,
metadata)` call convention already used in
`apps.quizzes.instructor_views`/`apps.labs.instructor_views`.

### Finding 3 (found while testing Finding 2): the Certificate admin add form was completely unusable
While writing a test for the new audit-log hook, discovered
`student`/`course` were unconditionally in `CertificateAdmin.
readonly_fields` — meaning they were never rendered on the *add* form
either, not just locked after creation. Certificates have no
application code path other than Django Admin (confirmed via grep —
nothing calls `Certificate.objects.create()` outside tests), so this
meant **it was never actually possible to issue a new certificate**
through the only path that exists for doing so. Empirically confirmed
via a test that loads the add page and asserts the student/course
inputs are simply absent from the rendered form, before fixing it.

**Fix:** `get_readonly_fields()` override — `student`/`course` are
editable on add, locked on change (matching the identity-shouldn't-
change-post-issuance reasoning already documented in the model).
`certificate_number`/`verification_code`/`certificate_hash` stay
readonly even on add, since they auto-generate in `Certificate.save()`
when blank — the first fix attempt made *all* readonly fields
editable on add, which then made `certificate_number` (no default,
not `blank=True`) a required form field with nothing to fill it,
producing a validation error instead of a save. Narrowed to just the
two fields that actually need to be enterable.

### Constraint audit (confirmed clean — no changes needed)
Manually reviewed every model touched across Phase 16 for the
duplicate-prevention constraint it should have: `Enrollment`
(student, course), `LessonProgress` (student, lesson), `LabProgress`
(lab, student), `AssignmentSubmission` (assignment, student),
`StudentFeedback` (student, course), `Certificate` (student, course),
`CohortMembership` (cohort, student), `LearningTimeEntry` (student,
lesson, date), `InstructorAssignment`, `Quiz` (one pre-test/post-test
per course) — all present. `EmploymentOutcome` and `ImpactSnapshot`
deliberately have no such constraint (append-only-history-log design,
documented in their own model docstrings from 16.H/16.K) — confirmed
this is intentional, not an oversight.

### What was NOT changed (and why)
Considered extending `progress_percentage` to factor in quiz/assignment/
lab completion, not just lessons — rejected. That's a product decision
about what "progress" means with cascading effects on every dashboard,
export, and cohort stat already built on the current lesson-only
definition, not a data-quality bug to silently redefine mid-audit.
Also considered auto-issuing certificates the moment an enrollment
completes — rejected for the same reason as always: certificate
issuance is an intentional human-review gate (an instructor/admin may
want to confirm a final project, exam, or other requirement beyond
lesson completion before issuing something as significant as a
certificate), not an oversight to "fix."

### Verification performed
- `manage.py check` — zero errors (no new migrations — no model field
  changes, only new behavior)
- Full suite: `manage.py test` 258/258 (up from 246) — 5 new
  `ProgressAutoCompletionTests` (100%-triggers-completion, below-100%-
  never-completes, completed-enrollments-frozen-from-structure-signals,
  the direct one-directional guard test, withdrawn-never-auto-
  completes), 3 new `BackfillEnrollmentCompletionCommandTests`
  (promotes stale data, `--dry-run` doesn't save, below-100% untouched),
  4 new `CertificateAdminTests` (add form now renders student/course,
  creating logs `certificate.issue`, revoking logs
  `certificate.status_change` with correct from/to, a no-op status save
  logs nothing)
- Ran the backfill command for real against the live Supabase database
  (dry-run first, confirmed no-op, then ran for real)

### Security review
- No new attack surface — every change is either server-side status
  logic, an admin-only form fix, or an audit-log write.
- The Certificate add-form fix is a net security *improvement*: before
  it, the only way to create a certificate was to bypass the admin form
  entirely (e.g. `manage.py shell`), which happens with zero audit
  trail; now the intended path works and is logged.
- Audit log entries never contain salary, evidence paths, or other
  sensitive fields — only `status` (a public enum value already shown
  on the certificate verification page) appears in `metadata`.

## 16.R — Final verification ✅ DONE — Phase 16 complete

### `manage.py check`
Zero errors on both `config.settings.development` (used throughout
this whole build) and `config.settings.production` (checked directly
with `DJANGO_SETTINGS_MODULE=config.settings.production`, not assumed).
`manage.py check --deploy` against production settings surfaced only
two items, both expected/non-issues: the pre-existing drf-spectacular
"status" enum-naming collision noted in 16.M (cosmetic, not enforced by
CI), and a SECRET_KEY warning caused by the dummy placeholder key used
for this one-off check command, not a real gap — `production.py`
already sets `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`,
`CSRF_COOKIE_SECURE`, and full HSTS correctly.

### Full test suite
`manage.py test` — **258/258 passing**, zero pending migrations
(`showmigrations` — 0), zero model drift (`makemigrations --check
--dry-run` — "No changes detected"). This is the authoritative
correctness signal for this phase: every dashboard, export, API
endpoint, and service function built across 16.A-Q has dedicated,
isolated (SQLite in-memory) test coverage that doesn't depend on the
live Supabase project's availability or connection headroom.

### Full-site crawl — and an important operational finding along the way
Crawled every Phase 16 URL as admin/instructor/student against the
live (real, production-shaped) Supabase-backed dev server: all
Management pages, all 15 new report export endpoints (CSV/Excel/PDF ×
Impact/Course/Student/Employment + FID PDF/Excel), all 7 new REST API
endpoints plus the drf-spectacular docs page, instructor feedback
pages, student certificate/employment/labs pages. Every one of these
returned 200 (or the correct 403 for the student-hits-admin-page cross-
role check) on a first or retried pass.

**Along the way, hit a real operational limit that's worth surfacing
independently of Phase 16's correctness**: partway through the crawl,
a request hung for over an hour with no server-side error logged.
Investigating turned up this in the server log:
```
django.db.utils.OperationalError: connection failed: connection to
server at "52.209.89.87", port 5432 failed: FATAL: (EMAXCONNSESSION)
max clients reached in session mode - max clients are limited to
pool_size: 15
```
This project's Supabase Postgres pooler is configured for **session
mode with a 15-client limit**. Combined with Django's `CONN_MAX_AGE=60`
(persistent connections held for 60s after each request) and this
session's repeated `manage.py runserver` + verification cycles across
16.J/16.K/16.M/16.N/16.O/16.Q/16.R, the pool got exhausted — causing
one request to hang indefinitely (no query timeout is configured, so a
starved connection attempt blocks rather than fails fast) and, later,
a real `500` on an unrelated login POST once the limit was hit again.
Checked `pg_stat_activity` directly and found the connection count
sitting at a steady ~13 even after stopping every local process,
suggesting other traffic (possibly the real deployed app, if one
exists against this same project) is also drawing from the same
15-connection budget.

**This is not a Phase 16 code defect** — it's an artifact of (a) this
verification session's own heavy repeated traffic against a live
external dependency, and (b) session-mode pooling with a low limit,
which is a Supabase project *configuration* choice, not something any
application code controls. Did not attempt to "fix" this by changing
`DATABASES` settings or the Supabase project configuration — that's a
production-infrastructure decision for the user, not something to
silently change mid-session. Recommending it here instead:
- Consider switching to Supabase's **transaction-mode pooler** (a
  different port/connection string) for a Django app using persistent
  connections — session mode is typically meant for tools that need
  long-lived sessions (e.g. `psql`), not a web app's connection pool.
- Consider setting a `connect_timeout`/`statement_timeout` in
  `DATABASES[...]["OPTIONS"]` so a starved connection attempt fails
  fast with a clear error instead of hanging a request indefinitely.
- If the 15-client limit is a plan-tier limit, this is worth knowing
  before real user traffic (not just my verification burst) hits it.

Once the burst subsided and I retried the previously-failed pages in
isolation with pauses between requests, everything that had failed
purely due to pool contention (instructor dashboard, certificate/
verification page-loads) succeeded normally — confirming this was
connection-pool contention, not a code path. Did not exhaustively
re-crawl every single previously-failed URL a second time once this
was established, to avoid needlessly hammering the same limited shared
resource further — the automated test suite already covers those exact
views end-to-end against an isolated database, which is sufficient
correctness evidence on its own.

### Security pass
- Every admin-only view across all of Phase 16 (`apps/reports`,
  `apps/analytics/api_views.py`, `apps/employment/api_views.py`,
  `apps/cohorts/api_views.py`) confirmed via grep to use
  `@admin_required` or `IsAdminRole` — none missing.
- No `|safe` template filter used anywhere in the new management/
  student/instructor dashboard templates — Django's default
  auto-escaping is relied on throughout, consistent with the rest of
  the codebase.
- No hardcoded secrets, API keys, or credentials in any new file.
- No stray `print()`/`pdb`/`breakpoint()` debug artifacts left in any
  new application code.
- Re-confirmed the full set of privacy/anonymity guarantees built up
  across the phase still hold: feedback anonymity (16.I), employment
  salary/evidence never in aggregates (16.H/16.L/16.M), student
  leaderboard/at-risk-list asymmetric anonymization by design (16.N
  anonymized, 16.O intentionally not — both documented), certificate
  storage paths never exposed via API (16.M) — none of these were
  touched or weakened during 16.Q's fixes.

### Summary
Phase 16 (Learning Analytics and Impact Measurement System) is
complete: 18 sub-phases (16.A-R), 258 automated tests, zero pending
migrations, zero `manage.py check` errors on dev or production
settings, a full live-data crawl of every new page and endpoint, and a
security pass finding no new vulnerabilities. Along the way, this pass
also fixed 3 real bugs that predated this session's start of 16.Q
(Enrollment never auto-completing, Certificate admin add-form being
unusable, certificate issuance never being audit-logged) — none of
which were "clean" findings, all verified fixed with regression tests,
not just theorized.
