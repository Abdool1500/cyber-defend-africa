/**
 * Tracks position within a frozen, server-provided list of question IDs
 * and per-question answered/flagged state for the quiz-taking UI.
 */
class QuestionNavigator {
  constructor(questionIds) {
    this.questionIds = [...questionIds];
    this.currentIndex = 0;
    this.answered = new Set();
    this.flagged = new Set();
  }

  get currentId() {
    return this.questionIds[this.currentIndex];
  }

  get total() {
    return this.questionIds.length;
  }

  canGoNext() {
    return this.currentIndex < this.questionIds.length - 1;
  }

  canGoPrevious() {
    return this.currentIndex > 0;
  }

  next() {
    if (this.canGoNext()) this.currentIndex += 1;
    return this.currentIndex;
  }

  previous() {
    if (this.canGoPrevious()) this.currentIndex -= 1;
    return this.currentIndex;
  }

  goTo(index) {
    if (index >= 0 && index < this.questionIds.length) {
      this.currentIndex = index;
    }
    return this.currentIndex;
  }

  markAnswered(questionId) {
    this.answered.add(questionId);
  }

  unmarkAnswered(questionId) {
    this.answered.delete(questionId);
  }

  isAnswered(questionId) {
    return this.answered.has(questionId);
  }

  toggleFlag(questionId) {
    if (this.flagged.has(questionId)) {
      this.flagged.delete(questionId);
    } else {
      this.flagged.add(questionId);
    }
    return this.flagged.has(questionId);
  }

  isFlagged(questionId) {
    return this.flagged.has(questionId);
  }

  unansweredCount() {
    return this.questionIds.filter((id) => !this.answered.has(id)).length;
  }
}

module.exports = { QuestionNavigator };
