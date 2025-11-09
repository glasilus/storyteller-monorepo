// middleware/auth.global.js
export default defineNuxtRouteMiddleware((to) => {
  const user = useSupabaseUser()
  
  // Публичные страницы - без авторизации
  const publicPages = ['/', '/login', '/register']
  
  console.log('🔍 Middleware:', to.path, 'User:', user.value)
  
  // Если страница публичная - пропускаем
  if (publicPages.includes(to.path)) {
    return
  }
  
  // Если неавторизован - редирект на логин
  if (!user.value) {
    return navigateTo('/login')
  }
})