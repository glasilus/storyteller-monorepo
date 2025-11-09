// nuxt.config.ts
export default defineNuxtConfig({
  modules: [
    '@nuxtjs/supabase',
    '@nuxtjs/tailwindcss'
  ],
  
  supabase: {
    url: process.env.SUPABASE_URL || '',
    key: process.env.SUPABASE_KEY || '',
    types: false,
    // ВАЖНО: Отключаем автоматические редиректы Supabase
    redirectOptions: {
      login: '/login',
      callback: '/confirm',
      exclude: ['/', '/login', '/register', '/dashboard']
    }
  },
  
  tailwindcss: {
    cssPath: '~/assets/css/main.css',
    configPath: 'tailwind.config.js',
    exposeConfig: false,
    editorSupport: true
  },
  
  runtimeConfig: {
    public: {
      apiBase: process.env.API_BASE_URL || 'http://localhost:8000/api/v1'
    }
  },
  
  devtools: { enabled: true },
  
  app: {
    head: {
      title: 'Storyboard AI - Генерация сценариев и раскадровок',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'AI-помощник для быстрого создания сценариев и визуальных раскадровок' }
      ]
    }
  }
})