# Contributing

## Workflow

1. Create a branch off `main`: `git switch -c feature/short-description`
2. Make your change, keeping it focused — small, reviewable diffs over big
   rewrites.
3. Run the full check before pushing:
   ```bash
   ./scripts/test.sh
   ```
4. Open a pull request using the provided template. Fill in the test plan
   honestly — don't check a box you didn't actually verify.

## Commit messages

Focus on *why*, not just *what*. Example:

```
Fix multiple-select grading to reject partial-match answers

Selecting a subset of correct options was being scored as fully correct.
Grading now requires an exact set match, matching the spec's default
behavior for multiple-select questions.
```

## Code conventions

- Django apps are organized by domain (`apps/quizzes`, `apps/feedback`,
  etc.) — role-specific views live in separate modules within an app
  (`instructor_views.py`, `student_views.py`) rather than branching on role
  inside one view function.
- Role-based authorization always goes through `apps/accounts/permissions.py`
  (decorators/mixins) — never a bare `if request.user.role == "..."` check
  scattered in a view.
- Never trust client-submitted scores, correctness flags, or awarded
  points. Grading logic lives in `apps/quizzes/services/grading.py` and
  runs entirely server-side.
- Supabase Storage access always goes through
  `apps/core/services/storage.py` — never call the Storage REST API
  directly from a view.

## Tests

- New permission-sensitive code (grading, private storage, feedback
  anonymity, role boundaries) needs a corresponding test — see
  `apps/quizzes/tests.py` and `apps/feedback/tests.py` for the existing
  pattern.
- JavaScript modules under `static/js/modules/` should stay pure/testable
  (no direct DOM/fetch calls) so they can be unit tested under Jest; DOM
  wiring lives in separate non-module scripts like `static/js/quiz_attempt.js`.

## Reporting security issues

See [`SECURITY.md`](SECURITY.md) — please don't open a public issue for a
vulnerability.
