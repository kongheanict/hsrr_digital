<template>
  <div class="container mx-auto px-4 py-18 md:py-8 max-w-4xl">
    <!-- Loading State -->
    <div v-if="quizStore.loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-blue-500"></div>
      <p class="ml-4 text-lg text-gray-600">{{ $t('Loading quiz data...') }}</p>
    </div>

    <!-- Error / Status -->
    <div
      v-else-if="quizStore.error || quizStore.statusMessage"
      class="text-center py-10 text-lg text-red-600"
    >
      <p>{{ quizStore.error || quizStore.statusMessage }}</p>
    </div>

    <!-- Quiz Content -->
    <div
      v-else-if="quizStore.currentQuiz && quizStore.questions?.length"
      class="bg-white rounded-xl shadow-lg p-6"
    >
      <!-- Header -->
      <div class="flex flex-col md:flex-row justify-center items-center mb-10">
        <h1 class="text-2xl font-bold text-gray-800">
          {{ quizStore.currentQuiz.title || $t('Untitled Quiz') }}
        </h1>
        <!-- Timer + Progress -->
        <div
          v-if="!quizStore.isAttempted"
          class="flex items-center space-x-4 mt-4 md:mt-0"
        >
          <div
            v-if="quizStore.remainingTime !== null"
            class="bg-gray-100 px-4 py-2 rounded-full text-sm font-semibold text-gray-700 flex items-center"
          >
            <i class="fas fa-clock mr-2"></i> {{ formattedTime }}
          </div>
          <div class="w-48 bg-gray-200 rounded-full h-3">
            <div
              class="bg-blue-500 h-3 rounded-full transition-all duration-300"
              :style="{ width: progressBarWidth }"
            ></div>
          </div>
        </div>
      </div>

      <!-- Question Nav -->
      <div class="flex flex-wrap justify-center gap-2 mb-4">
        <button
          v-for="(question, index) in quizStore.questions"
          :key="question.id"
          @click="goToQuestion(index)"
          :class="[
            'w-6 h-6 rounded-full flex items-center justify-center text-sm font-semibold transition-colors',
            quizStore.currentQuestionIndex === index
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
            isAnswered(question.id) ? 'ring-2 ring-green-500' : ''
          ]"
        >
          {{ index + 1 }}
        </button>
      </div>

      <!-- Review Mode -->
      <div v-if="quizStore.isAttempted" class="space-y-6">
        <div class="text-center py-8">
          <h2 class="text-lg md:text-3xl font-bold text-green-600 mb-4">
            {{ $t('កម្រងតេស្តបានបញ្ចប់ !') }}
          </h2>
          <p
            v-if="quizStore.allowSeeScore"
            class="text-lg md:text-xl font-semibold text-gray-800"
          >
            {{ $t('ពិន្ទុបានសរុប:') }}
            <span v-if="quizStore.currentAttempt?.score > totalScore/2 " class="text-green-700 ml-2">{{ quizStore.currentAttempt?.score || 0 }} / {{ totalScore }}</span>
            <span v-else class="text-red-400 ml-2">{{ quizStore.currentAttempt?.score || 0 }} / {{ totalScore }}</span>
          </p>
        </div>

        <!-- Review Questions -->
        <div v-if="quizStore.allowCheckAnswer">
          <div
            v-for="(question, index) in quizStore.questions"
            :key="question.id"
            class="border-t border-gray-200 pt-6"
          >
            <div class="flex justify-between items-center mb-4">
              <h3
                class="text-sm md:text-md font-semibold text-gray-800"
                v-html="question.text || $t('Question text unavailable')"
              />
              <div  v-if="quizStore.allowSeeScore" class="text-xs md:text-sm font-medium text-gray-600">
                {{ $t('ពិន្ទុ:') }} {{ getQuestionScore(question) }} /
                {{ question.points || 0 }}
              </div>
            </div>

            <!-- MCQ -->
            <div
              v-if="question.question_type === 'MCQ_SINGLE' || question.question_type === 'MCQ_MULTI'"
              class="space-y-3 text-sm"
            >
              <div
                v-for="option in question.options || []"
                :key="option.id"
                class="flex items-center p-3 border border-gray-300 rounded-lg bg-gray-50"
              >
                <input
                  :type="question.question_type === 'MCQ_SINGLE'
                    ? 'radio'
                    : 'checkbox'"
                  :checked="isOptionSelected(question.id, option.id)"
                  disabled
                  class="mr-3 text-blue-600 focus:ring-blue-500"
                />
                <span
                  v-if="quizStore.allowSeeScore"
                  :class="{
                    'text-green-600 font-medium': isCorrectAnswer(question.id, option.id),
                    'text-red-600 line-through': !isCorrectAnswer(question.id, option.id) && isOptionSelected(question.id, option.id),
                    'text-gray-700': !isCorrectAnswer(question.id, option.id) && !isOptionSelected(question.id, option.id)
                  }"
                >
                  {{ option.text || $t('Option unavailable') }}
                </span>
                <span v-else>
                  {{ option.text || $t('Option unavailable') }}
                </span>

                <i
                  v-if="isCorrectAnswer(question.id, option.id) && quizStore.allowSeeScore"
                  class="ml-2 fas fa-check text-green-600"
                ></i>
                <i
                  v-if="!isCorrectAnswer(question.id, option.id) && isOptionSelected(question.id, option.id) && quizStore.allowSeeScore"
                  class="ml-2 fas fa-times text-red-600"
                ></i>
              </div>
            </div>

            <!-- Short Answer -->
            <div v-else-if="question.question_type === 'SHORT'" class="space-y-3">
              <div class="p-3 border border-gray-300 rounded-lg bg-gray-50">
                <p class="font-medium text-sm text-gray-800">{{ $t('ចម្លើយរបស់អ្នក:') }}
                  {{ quizStore.answers[question.id] || $t('គ្មានចម្លើយ') }}
                </p> 
              </div>
              <div v-if="quizStore.allowSeeScore" class="p-3 border border-gray-300 rounded-lg bg-green-50">
                <p class="font-medium text-sm text-gray-800">
                  {{ $t('ចម្លើយត្រឹមត្រូវ:') }}  {{ question.options?.find(opt => opt.is_correct)?.text || $t('គ្មានចម្លើយកំណត់') }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- If Review Not Allowed -->
        <div v-else class="text-center text-lg text-gray-600 py-8">
          {{ $t('Answer review is not allowed for this quiz.') }}
        </div>
      </div>

      <!-- Taking Mode -->
      <div v-else class="space-y-6">
        <div v-if="currentQuestion" class="border-t border-gray-200 pt-6">
          <h3
            class="text-lg font-semibold text-gray-800 mb-4"
            v-html="currentQuestion.text || $t('Question text unavailable')"
          />
          <p v-if="quizStore.allowSeeScore" class="text-sm text-gray-600 mb-4">
            {{ $t('ពិន្ទុ:') }} {{ currentQuestion.points || 0 }}
          </p>

          <!-- MCQ Single -->
          <div v-if="currentQuestion.question_type === 'MCQ_SINGLE'" class="space-y-3">
            <label
              v-for="option in currentQuestion.options || []"
              :key="option.id"
              class="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-100 transition"
            >
              <input
                type="radio"
                :name="'question-' + currentQuestion.id"
                :value="option.id"
                v-model="quizStore.answers[currentQuestion.id]"
                class="mr-3 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-gray-700">{{ option.text || $t('Option unavailable') }}</span>
            </label>
          </div>

          <!-- MCQ Multi -->
          <div v-else-if="currentQuestion.question_type === 'MCQ_MULTI'" class="space-y-3">
            <label
              v-for="option in currentQuestion.options || []"
              :key="option.id"
              class="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-100 transition"
            >
              <input
                type="checkbox"
                :name="'question-' + currentQuestion.id"
                :value="option.id"
                v-model="quizStore.answers[currentQuestion.id]"
                class="mr-3 text-blue-600 rounded focus:ring-blue-500"
              />
              <span class="text-gray-700">{{ option.text || $t('Option unavailable') }}</span>
            </label>
          </div>

          <!-- Short Answer -->
          <div v-else-if="currentQuestion.question_type === 'SHORT'">
            <textarea
              v-model="quizStore.answers[currentQuestion.id]"
              class="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
              :placeholder="$t('Type your answer here')"
              rows="4"
            ></textarea>
          </div>
        </div>

        <!-- Navigation -->
        <div class="flex justify-between mt-8 pt-4 border-t border-gray-200">
          <button
            @click="quizStore.previousQuestion()"
            :disabled="quizStore.currentQuestionIndex === 0"
            class="px-6 py-2 bg-gray-300 text-gray-800 font-semibold rounded-full hover:bg-gray-400 disabled:bg-gray-200 disabled:cursor-not-allowed transition"
          >
            {{ $t('សំណួរមុន') }}
          </button>
          <button
            v-if="quizStore.currentQuestionIndex < quizStore.questions.length - 1"
            @click="quizStore.nextQuestion()"
            class="px-6 py-2 bg-blue-600 text-white font-semibold rounded-full hover:bg-blue-700 transition"
          >
            {{ $t('បន្ទាប់') }}
          </button>
          <button
            v-else
            @click="handleSubmitQuiz"
            class="px-6 py-2 bg-green-600 text-white font-semibold rounded-full hover:bg-green-700 transition"
          >
            {{ $t('ដាក់បញ្ជូនកម្រងសំណួរ') }}
          </button>
        </div>
      </div>
    </div>

    <!-- No Quiz Selected -->
    <div v-else class="text-center text-lg text-gray-600 py-10">
      {{ $t('Please select a quiz to start.') }}
    </div>
  </div>
</template>

<script setup>
import { computed, watch, onUnmounted, onMounted } from 'vue'
import { useQuizStore } from '../stores/quiz'
import { useRoute, useRouter } from 'vue-router'
import Swal from 'sweetalert2'  // Import SweetAlert2
import { useI18n } from 'vue-i18n'

const quizStore = useQuizStore()
const route = useRoute()
const router = useRouter()
const { t: $t } = useI18n()

// Current Question
const currentQuestion = computed(() =>
  quizStore.questions?.length
    ? quizStore.questions[quizStore.currentQuestionIndex] || null
    : null
)

// Total Score
const totalScore = computed(() =>
  quizStore.questions?.reduce((sum, q) => sum + (q.points || 0), 0) || 0
)

// Timer
const formattedTime = computed(() => {
  if (!quizStore.remainingTime || quizStore.remainingTime <= 0) return '00:00'
  const m = Math.floor(quizStore.remainingTime / 60)
  const s = Math.floor(quizStore.remainingTime % 60)
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

const progressBarWidth = computed(() =>
  quizStore.questions?.length
    ? `${((quizStore.currentQuestionIndex + 1) / quizStore.questions.length) * 100}%`
    : '0%'
)

// Handle submit with SweetAlert confirmation
const handleSubmitQuiz = async () => {
  const result = await Swal.fire({
    title: $t('សូមបញ្ជាក់!'),
    text: $t('តើអ្នកពិតជាចង់បញ្ចប់កម្រងសំណួររបស់អ្នកមែនទេ? អ្នកនឹងមិនអាចកែប្រែចម្លើយរបស់អ្នកបន្ថែមទៀតបានឡើយ.'),
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: $t('សម្រេចបញ្ចប់!'),
    cancelButtonText: $t('ត្រឡប់')
  });

  if (result.isConfirmed) {
    try {
      await quizStore.submitQuiz();
      Swal.fire({
        title: $t('ការបញ្ជូនតេស្តបានជោគជ័យ!'),
        text: $t('ចម្លើយរបស់អ្នកបានរក្សាទុក និងគណនាពិន្ទុរួចរាល់.'),
        icon: 'success',
        confirmButtonText: $t('យល់ព្រម')
      }).then(() => {
        // Navigate to quizzes list after success
        location.href = '/quizzes';
      });
    } catch (err) {
      // Error already set in store, show alert
      Swal.fire({
        title: $t('ការបញ្ជូនបរាជ័យ!'),
        text: quizStore.error || $t('មានបញ្ហាពេលបញ្ជូនទិន្នន័យ, សូមព្យាយាមម្ដងទៀត.'),
        icon: 'error',
        confirmButtonText: $t('យល់ព្រម')
      });
      console.error('Submit failed:', err);
    }
  }
}

// Helpers
const isAnswered = id => {
  const ans = quizStore.answers[id]
  return Array.isArray(ans) ? ans.length > 0 : ans !== null && ans !== undefined && ans !== ''
}

const goToQuestion = idx => {
  if (quizStore.questions?.[idx]) quizStore.currentQuestionIndex = idx
}

const isOptionSelected = (qid, oid) => {
  const ans = quizStore.answers[qid]
  return Array.isArray(ans) ? ans.includes(oid) : ans === oid
}

const isCorrectAnswer = (qid, oid) => {
  const q = quizStore.questions.find(q => q.id === qid)
  return q?.options?.find(opt => opt.id === oid)?.is_correct || false
}

const getQuestionScore = q => {
  if (!q || !quizStore.isAttempted) return 0
  const r = quizStore.student_responses?.find(r => r.question.id === q.id)
  return r?.points_earned || 0
}

// Timer logic
let timerInterval = null
watch(
  () => quizStore.remainingTime,
  newTime => {
    if (timerInterval) clearInterval(timerInterval)
    if (newTime !== null && !quizStore.isAttempted) {
      timerInterval = setInterval(() => {
        if (quizStore.remainingTime > 0) quizStore.remainingTime--
        else {
          clearInterval(timerInterval)
          if (!quizStore.isAttempted){
            quizStore.submitQuiz().then(() => {
              Swal.fire({
                title: $t('ពេលវេលាបញ្ចប់!'),
                text: $t('ពេលវេលារបស់អ្នកបានបញ្ចប់. កម្រងសំណួររបស់អ្នកត្រូវបានដាក់ស្នើដោយស្វ័យប្រវត្តិ.'),
                icon: 'info',
                confirmButtonText: $t('យល់ព្រម')
              }).then(() => {
                location.href = '/quizzes';
              });
            }).catch(() => {
              Swal.fire({
                title: $t('ការបញ្ជូនបរាជ័យ!'),
                text: quizStore.error || $t('មានបញ្ហាពេលបញ្ជូនទិន្នន័យ, សូមព្យាយាមម្ដងទៀត.'),
                icon: 'error',
                confirmButtonText: $t('យល់ព្រម')
              });
            });
          }
        }
      }, 1000)
    }
  },
  { immediate: true }
)

// BeforeUnload for taking mode (confirm leave/reload)
let beforeUnloadHandler = null
onMounted(() => {
  if (!quizStore.isAttempted && quizStore.questions?.length > 0) {
    beforeUnloadHandler = (e) => {
      const hasUnsaved = Object.values(quizStore.answers).some(ans => ans !== null && ans !== undefined && ans !== '')
      if (hasUnsaved) {
        e.preventDefault()
        e.returnValue = $t('You have unsaved answers. Are you sure you want to leave?')
        return $t('You have unsaved answers. Are you sure you want to leave?')
      }
    }
    window.addEventListener('beforeunload', beforeUnloadHandler)
  }
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
  if (beforeUnloadHandler) {
    window.removeEventListener('beforeunload', beforeUnloadHandler)
  }
})

// Init Quiz / Review
watch(
  () => [route.query.quizId, route.name],
  ([id, name]) => {
    if (!id) return
    quizStore.error = null
    if (name === 'QuizReviewPage') quizStore.reviewAnswers(id).catch(() => (quizStore.error = $t('Failed to load quiz review.')))
    else quizStore.startQuiz(id).catch(() => (quizStore.error = $t('Failed to start quiz.')))
  },
  { immediate: true }
)

// Multi-choice answers must be arrays
watch(
  currentQuestion,
  q => {
    if (q?.question_type === 'MCQ_MULTI' && !Array.isArray(quizStore.answers[q.id])) {
      quizStore.answers[q.id] = []
    }
  },
  { immediate: true }
)
</script>

<style scoped>
/* TailwindCSS is used directly in the template, so no additional CSS is needed here */
</style>