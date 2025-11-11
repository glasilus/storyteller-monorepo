<template>
  <NuxtLayout name="auth">
    <div class="hero min-h-screen bg-base-200">
      <div class="hero-content flex-col lg:flex-row-reverse">
        <!-- Левая часть -->
        <div class="text-center lg:text-left">
          <h1 class="text-5xl font-bold">Регистрация</h1>
          <p class="py-6">Создайте аккаунт, чтобы начать создавать истории</p>
        </div>
        
        <!-- Правая часть (форма) -->
        <div class="card flex-shrink-0 w-full max-w-sm shadow-2xl bg-base-100">
          <div class="card-body">
            <!-- ВКЛАДКИ -->
            <AuthTabs />
            
            <!-- ФОРМА РЕГИСТРАЦИИ -->
            <form @submit.prevent="handleRegister">
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Email</span>
                </label>
                <input 
                  v-model="email" 
                  type="email" 
                  placeholder="you@example.com" 
                  class="input input-bordered"
                  required
                />
              </div>
              
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Пароль</span>
                  <span class="label-text-alt">Минимум 6 символов</span>
                </label>
                <input 
                  v-model="password" 
                  type="password" 
                  placeholder="••••••••" 
                  class="input input-bordered"
                  required
                  minlength="6"
                />
              </div>
              
              <div class="form-control mt-6">
                <button class="btn btn-primary btn-block" type="submit" :disabled="loading">
                  <span class="loading loading-spinner" v-if="loading"></span>
                  {{ loading ? 'Регистрация...' : 'Создать аккаунт' }}
                </button>
              </div>
              
              <div v-if="error" class="alert alert-error mt-4">
                <span>{{ error }}</span>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
definePageMeta({
  layout: 'auth'
})

const { signUp } = useSupabaseAuth()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)

const handleRegister = async () => {
  loading.value = true
  error.value = null
  
  try {
    await signUp(email.value, password.value)
    alert('Проверьте email для подтверждения регистрации!')
    navigateTo('/login')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>