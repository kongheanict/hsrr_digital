import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import Login from '../views/Login.vue';
import NotFound from '../views/NotFound.vue';
import Courses from '../views/Courses.vue';
import CourseDetail from '../views/CourseDetail.vue';
import QuizPage from '../views/QuizPage.vue';
import QuizResult from '../components/QuizResult.vue';
import Quizzes from '../views/Quizzes.vue';
import Home from '../views/Home.vue';
import LeaveRequest from '../components/teachers/LeaveRequestForm.vue';
import Forbidden from '../views/Forbidden.vue'; // Create this view

const routes = [
  { path: '/', name: 'HomePage', component: Home, meta: { requiresAuth: true } },
  { path: '/quizzes', name: 'Quizzes', component: Quizzes, meta: { requiresAuth: true, roles: ['student', 'admin'] } },
  { path: '/quiz', name: 'QuizPage', component: QuizPage, props: true, meta: { requiresAuth: true } },
  { path: '/quiz-review', name: 'QuizReviewPage', component: QuizPage, props: true, meta: { requiresAuth: true, roles: ['student', 'admin'] } },
  { path: '/quiz/:quizId/result', name: 'QuizResult', component: QuizResult, meta: { requiresAuth: true , roles: ['student', 'admin']} },
  { path: '/courses', name: 'CoursePage', component: Courses, meta: { requiresAuth: true , roles: ['student', 'admin'] } },
  { path: '/courses/:id', name: 'CourseDetail', component: CourseDetail, meta: { requiresAuth: true , roles: ['student', 'admin']} },
  { path: '/ask-leave-form', name: 'AskLeave',component: LeaveRequest, meta: { requiresAuth: true, roles: ['teacher', 'admin'] } }, // Restrict to teachers
  { path: '/login', component: Login },
  { path: '/forbidden', name: 'Forbidden', component: Forbidden },
  { path: '/:pathMatch(.*)*', component: NotFound, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const userRole = authStore.getRole;

  if (to.meta.requiresAuth) {
    const token = await authStore.validateToken();
    if (!token) {
      next('/login');
    } else if (to.meta.roles && userRole && !to.meta.roles.includes(userRole)) {
      next('/forbidden');
    } else {
      next();
    }
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/');
  } else {
    next();
  }
});

export default router;