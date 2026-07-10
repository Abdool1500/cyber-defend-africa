/* Wires the QuizTimer/QuestionNavigator/Autosave modules to the DOM for
 * the student quiz-taking page (templates/student/attempts/take.html).
 * Loaded as a plain <script> (non-module) so it can run without a bundler;
 * the shared logic itself lives in static/js/modules/*.js and is unit
 * tested independently under Jest.
 */
(function () {
  const root = document.getElementById("quiz-attempt-root");
  if (!root) return;

  const attemptId = root.dataset.attemptId;
  const expiresAt = root.dataset.expiresAt || null;
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

  const questionCards = Array.from(document.querySelectorAll(".attempt-question"));
  const questionIds = questionCards.map((el) => el.dataset.attemptQuestionId);

  function api(path, body) {
    return fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
      body: JSON.stringify(body),
    }).then((res) => {
      if (!res.ok) throw new Error("Request failed");
      return res.json();
    });
  }

  function showQuestion(index) {
    questionCards.forEach((el, i) => el.classList.toggle("d-none", i !== index));
    document.querySelectorAll(".question-nav-item").forEach((el, i) => {
      el.classList.toggle("active", i === index);
    });
  }

  let currentIndex = 0;
  function goTo(index) {
    if (index < 0 || index >= questionCards.length) return;
    currentIndex = index;
    showQuestion(currentIndex);
  }

  document.getElementById("btn-next")?.addEventListener("click", () => goTo(currentIndex + 1));
  document.getElementById("btn-prev")?.addEventListener("click", () => goTo(currentIndex - 1));
  document.querySelectorAll(".question-nav-item").forEach((el, i) => {
    el.addEventListener("click", () => goTo(i));
  });

  const autosaveTimers = {};
  function scheduleAutosave(attemptQuestionId, payload) {
    clearTimeout(autosaveTimers[attemptQuestionId]);
    const statusEl = document.querySelector(`[data-save-status="${attemptQuestionId}"]`);
    if (statusEl) statusEl.textContent = "Saving...";
    autosaveTimers[attemptQuestionId] = setTimeout(() => {
      api(`/student/attempts/${attemptId}/answer/`, {
        attempt_question_id: attemptQuestionId,
        ...payload,
      })
        .then(() => {
          if (statusEl) statusEl.textContent = "Saved";
        })
        .catch(() => {
          if (statusEl) statusEl.textContent = "Save failed — retrying on next change";
        });
    }, 700);
  }

  questionCards.forEach((card) => {
    const attemptQuestionId = card.dataset.attemptQuestionId;
    card.querySelectorAll("input[type=checkbox], input[type=radio]").forEach((input) => {
      input.addEventListener("change", () => {
        const checked = Array.from(
          card.querySelectorAll("input[type=checkbox]:checked, input[type=radio]:checked")
        ).map((el) => el.value);
        scheduleAutosave(attemptQuestionId, { option_ids: checked });
      });
    });
    card.querySelectorAll("textarea").forEach((textarea) => {
      textarea.addEventListener("input", () => {
        scheduleAutosave(attemptQuestionId, { text_answer: textarea.value });
      });
    });
  });

  const submitButton = document.getElementById("btn-submit");
  submitButton?.addEventListener("click", () => {
    if (!confirm("Submit this quiz? You will not be able to change your answers afterwards.")) return;
    api(`/student/attempts/${attemptId}/submit/`, {}).then((data) => {
      window.location.href = data.redirect_url;
    });
  });

  const timerEl = document.getElementById("quiz-timer");
  if (expiresAt && timerEl) {
    const remaining = Math.max(0, Math.floor((new Date(expiresAt) - new Date()) / 1000));
    let secondsLeft = remaining;
    const format = (s) => {
      const m = Math.floor(s / 60).toString().padStart(2, "0");
      const sec = (s % 60).toString().padStart(2, "0");
      return `${m}:${sec}`;
    };
    timerEl.textContent = format(secondsLeft);
    const interval = setInterval(() => {
      secondsLeft -= 1;
      timerEl.textContent = format(secondsLeft);
      if (secondsLeft <= 0) {
        clearInterval(interval);
        api(`/student/attempts/${attemptId}/submit/`, {}).then((data) => {
          window.location.href = data.redirect_url;
        });
      }
    }, 1000);
  }

  showQuestion(0);
})();
