import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from './auth';

const API_URL = 'http://127.0.0.1:8000/api';
const SESSION_STORAGE_KEY = 'quiz-answers';

export const useQuizStore = defineStore('quiz', {
  state: () => ({
    quizzes: [],
    currentQuiz: null,
    currentAttempt: { attempt_id: null, score: null },
    questions: [],
    answers: {},
    currentQuestionIndex: 0,
    loading: false,
    error: null,
    statusMessage: null, // New state for status messages
    remainingTime: null,
    timer: null,
    isAttempted: false,
    allowCheckAnswer: false,
    allowSeeScore: false,
  }),
  actions: {
    async fetchQuizzes() {
      this.loading = true;
      this.error = null;
      try {
        const authStore = useAuthStore();
        if (!authStore.isAuthenticated) return;
        const token = await authStore.validateToken();
        const response = await axios.get(`${API_URL}/quizzes/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.quizzes = response.data;
      } catch (err) {
        this.error = 'Failed to fetch quizzes.';
      } finally {
        this.loading = false;
      }
    },
    
    async startQuiz(quizId) {
      this.loading = true;
      this.error = null;
      this.statusMessage = null;
      this.clearQuiz();
      try {
        const authStore = useAuthStore();
        if (!authStore.isAuthenticated) return;
        const token = await authStore.validateToken();
        const response = await axios.get(`${API_URL}/quizzes/${quizId}/start/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = response.data;

        if (data.completed_at) {
          // This path is for completed quizzes, so we should handle it to prevent unexpected behavior.
          this.currentAttempt = { attempt_id: data.id, score: data.score };
          this.currentQuiz = data.quiz;
          this.questions = data.quiz.questions;
          // ... rest of the completed quiz logic
          this.isAttempted = true;
          this.answers = data.answers;
        } else {
          // This path is for in-progress quizzes.
          this.currentQuiz = data;
          this.currentAttempt = { attempt_id: data.attempt_id };
          this.questions = data.questions;
          this.remainingTime = data.remaining_time;
          // ... rest of the in-progress logic
          this.isAttempted = false;
        }
        this.allowCheckAnswer = data.allow_check_answer;
        this.allowSeeScore = data.allow_see_score;
      } catch (err) {
        if (err.response && err.response.data && err.response.data.status) {
          this.statusMessage = err.response.data.error;
        } else {
          this.error = err.response?.data?.error || 'Failed to start quiz.';
        }
      } finally {
        this.loading = false;
      }
    },
    
    setAnswer(questionId, answer) {
      this.answers[questionId] = answer;
      sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(this.answers));
    },

    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++;
      }
    },

    previousQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--;
      }
    },

    clearQuiz() {
      this.currentQuiz = null;
      this.currentAttempt = { attempt_id: null, score: null };
      this.questions = [];
      this.answers = {};
      this.currentQuestionIndex = 0;
      this.remainingTime = null;
      this.isAttempted = false;
      this.allowCheckAnswer = false;
      this.allowSeeScore = false;
      sessionStorage.removeItem(SESSION_STORAGE_KEY);
    },

    async submitQuiz() {
      this.loading = true;
      this.error = null;
      try {
        const authStore = useAuthStore();
        if (!authStore.isAuthenticated) return;
        const token = await authStore.validateToken();
        const payload = {
          attempt_id: this.currentAttempt.attempt_id,
          answers: this.answers,
        };
        const response = await axios.post(`${API_URL}/quizzes/${this.currentQuiz.id}/submit/`, payload, {
          headers: { Authorization: `Bearer ${token}` },
        });
        
        this.currentAttempt.score = response.data.score;
        this.isAttempted = true;
        sessionStorage.removeItem(SESSION_STORAGE_KEY);
        // Navigate to review page
        router.push(`/quiz-review?quizId=${this.currentQuiz.id}&attemptId=${this.currentAttempt.attempt_id}`);

      } catch (err) {
        this.error = 'Failed to submit quiz.';
      } finally {
        this.loading = false;
      }
    },
    async reviewAnswers(quizId) {
      this.loading = true;
      this.error = null;
      this.clearQuiz();
      try {
        const authStore = useAuthStore();
        if (!authStore.isAuthenticated) return;
        const token = await authStore.validateToken();
        const response = await axios.get(`${API_URL}/quizzes/${quizId}/review/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = response.data;
        console.log('Full API response:', data);

        this.currentQuiz = data.quiz_info || {};
        this.questions = Array.isArray(data.questions) ? data.questions : [];
        this.student_responses = Array.isArray(data.student_responses) ? data.student_responses : [];
        this.isAttempted = true;
        this.currentAttempt = { id: data.id, score: data.score || 0 };
        this.allowCheckAnswer = data.quiz_info?.allow_check_answer ?? false;
        this.allowSeeScore = data.quiz_info?.allow_see_score ?? false;

        this.answers = this.student_responses.reduce((acc, response) => {
          const questionId = response.question;
          const selectedOptions = Array.isArray(response.selected_options) ? response.selected_options : [];
          const textAnswer = response.text_answer;

          if (selectedOptions.length > 0) {
            acc[questionId] = selectedOptions;
          } else if (textAnswer !== null && textAnswer !== undefined) {
            acc[questionId] = textAnswer;
          }
          return acc;
        }, {});

        if (this.questions.length === 0) {
          this.error = 'No questions available for this quiz. Please contact support.';
        }
      } catch (err) {
        console.error('Review error:', err);
        console.error('Error response:', err.response?.data);
        this.error = err.response?.data?.error || 'Failed to load quiz review. Server error occurred.';
        this.questions = [];
      } finally {
        this.loading = false;
      }
    }
  },
  
});