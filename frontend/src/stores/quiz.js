import { defineStore } from 'pinia';
import { api } from './auth'; // Import the shared Axios instance
import { useAuthStore } from './auth';

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
    statusMessage: null,
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
        if (!authStore.isAuthenticated) {
          this.error = 'Not authenticated';
          return;
        }
        const token = await authStore.validateToken();
        if (!token) {
          this.error = 'Invalid token';
          return;
        }
        const response = await api.get('/quizzes/'); // Use shared api instance
        if (Array.isArray(response.data)) {
          this.quizzes = response.data;
        } else {
          this.error = 'មិនមានតេស្តណាមួយទេ។ សូមទាក់ទងអ្នកគ្រប់គ្រងប្រព័ន្ធ។';
          this.quizzes = [];
        }
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to fetch quizzes.';
        console.error('Fetch quizzes error:', err.response?.data || err.message);
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
        if (!authStore.isAuthenticated) {
          this.error = 'Not authenticated';
          return;
        }
        const token = await authStore.validateToken();
        if (!token) {
          this.error = 'Invalid token';
          return;
        }
        const response = await api.get(`/quizzes/${quizId}/start/`);
        const data = response.data;
        console.log('Full API response:', data);

        // // Load saved answers from session storage  
        // const savedAnswers = sessionStorage.getItem(SESSION_STORAGE_KEY);
        // if (savedAnswers) {
        //   try {
        //     this.answers = JSON.parse(savedAnswers);
        //   } catch (e) {
        //     console.error('Failed to parse saved answers from session storage:', e);
        //     this.answers = {};
        //   }
        // }


        if (data.completed_at) {
          this.currentAttempt = { attempt_id: data.id, score: data.score };
          this.currentQuiz = data.quiz;
          this.questions = data.quiz.questions;
          this.isAttempted = true;
          this.answers = data.answers;
        } else {
          this.currentQuiz = data;
          this.currentAttempt = { attempt_id: data.attempt_id };
          this.questions = data.questions;
          this.remainingTime = data.remaining_time;
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
        console.error('Start quiz error:', err.response?.data || err.message);
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
        if (!authStore.isAuthenticated) {
          this.error = 'Not authenticated';
          return;
        }
        const token = await authStore.validateToken();
        if (!token) {
          this.error = 'Invalid token';
          return;
        }
        const payload = {
          attempt_id: this.currentAttempt.attempt_id,
          answers: this.answers,
        };
        const response = await api.post(`/quizzes/${this.currentQuiz.id}/submit/`, payload);
        this.currentAttempt.score = response.data.score;
        this.isAttempted = true;
        sessionStorage.removeItem(SESSION_STORAGE_KEY);
        router.push(`/quiz-review?quizId=${this.currentQuiz.id}&attemptId=${this.currentAttempt.attempt_id}`);
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to submit quiz.';
        console.error('Submit quiz error:', err.response?.data || err.message);
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
        if (!authStore.isAuthenticated) {
          this.error = 'Not authenticated';
          return;
        }
        const token = await authStore.validateToken();
        if (!token) {
          this.error = 'Invalid token';
          return;
        }
        const response = await api.get(`/quizzes/${quizId}/review/`);
        const data = response.data;
        console.log('Full API response:', data);

        this.currentQuiz = data.quiz_info || {};
        this.questions = Array.isArray(data.questions) ? data.questions : [];
        // Fallback: Derive questions from student_responses if no top-level questions
        if (this.questions.length === 0 && Array.isArray(data.student_responses) && data.student_responses.length > 0) {
          this.questions = data.student_responses.map(r => r.question);
          console.log('Derived questions from responses:', this.questions);
        }
        this.student_responses = Array.isArray(data.student_responses) ? data.student_responses : [];
        this.isAttempted = true;
        this.currentAttempt = { id: data.id, score: data.score || 0 };
        this.allowCheckAnswer = data.quiz_info?.allow_check_answer ?? false;
        this.allowSeeScore = data.quiz_info?.allow_see_score ?? false;

        this.answers = this.student_responses.reduce((acc, response) => {
          const questionId = response.question.id || response.question;  // Handle both object and ID
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
    },
  },
});