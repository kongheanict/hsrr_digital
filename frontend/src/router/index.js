import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import { useAuthStore } from '../stores/auth'
import NotFound from '../views/NotFound.vue'
import Courses from '../views/Courses.vue'
import CourseDetail from '../views/CourseDetail.vue';
import QuizPage from '../views/QuizPage.vue';
import QuizResult from '../components/QuizResult.vue'
import Quizzes from '../views/Quizzes.vue'
import Home from '../views/Home.vue'

const routes = [
  { path: '/', name: 'HomePage', component: Home, meta: { requiresAuth: true } },
  { path: '/quizzes', name: 'Quizzes', component: Quizzes, meta: { requiresAuth: true } },
  { path: '/quiz', name: 'QuizPage', component: QuizPage, props: true, meta: { requiresAuth: true } },
  { path: '/quiz-review', name: 'QuizReviewPage', component: QuizPage, props: true, meta: { requiresAuth: true } },
  {
    path: '/quiz/:quizId/result',
    name: 'QuizResult',
    component: QuizResult,
    meta: { requiresAuth: true }
  },
  { path: '/courses', component: Courses, meta: { requiresAuth: true } },
  { path: '/courses/:id', component: CourseDetail, meta: { requiresAuth: true } },
  { path: '/resources', component: { template: '<div>Resources Page</div>' }, meta: { requiresAuth: true } },
  { path: '/grades', component: { template: '<div>Grades Page</div>' }, meta: { requiresAuth: true } },
  { path: '/profile', component: { template: '<div>Profile Page</div>' }, meta: { requiresAuth: true } },
  { path: '/section/:id', component: { template: '<div>Section Page</div>' }, meta: { requiresAuth: true } },
  { path: '/login', component: Login },
  { path: '/:pathMatch(.*)*', component: NotFound, meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else if (to.meta.requiresRole && authStore.user.role !== to.meta.requiresRole) {
    next('/not-authorized') // Add a new route for unauthorized access
  } else {
    next()
  }
})
export default router