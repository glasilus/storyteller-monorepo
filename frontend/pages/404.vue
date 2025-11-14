<template>
    <div 
      class="min-h-screen relative overflow-hidden"
      @mousemove="handleMouseMove"
      @mouseleave="handleMouseLeave"
    >
      <!-- Фон -->
      <div class="absolute inset-0 bg-gradient-to-br from-indigo-950 via-purple-950 to-blue-950"></div>
      
      <!-- Текстура мазков (base layer) -->
      <div 
        class="absolute inset-0 opacity-8"
        style="background-image: url('image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMDAgMzAwIj48ZyBmaWxsPSJub25lIj48cGF0aCBkPSJNNDAsODAgUTcwLDQwIDEyMCw3MCBRMTYwLDkwIDE5MCw2MCIgc3Ryb2tlPSJyZ2JhKDI1MywyMjQsMTE1LDAuMDgpIiBzdHJva2Utd2lkdGg9IjIiIG9wYWNpdHk9IjAuNiIvPjxwYXRoIGQ9Ik0yMCwxNTAgUTYwLDEyMCAxMDAsMTYwIFEyMDAsMTgwIDE4MCwxNDAiIHN0cm9rZT0icmdiYSgxMzksOTIsMjQ2LDAuMDYpIiBzdHJva2Utd2lkdGg9IjEuNSIgb3BhY2l0eT0iMC41Ii8+PHBhdGggZD0iTTYwLDIyMCBRMTAwLDIwMCAxNDAsMjMwIFE1MCwyNTAgMjIwLDIyMCIgc3Ryb2tlPSJyZ2JhKDU2LDE4OSwyNDgsMC4wNSkiIHN0cm9rZS13aWR0aD0iMSIgb3BhY2l0eT0iMC40Ii8+PHBhdGggZD0iTTI1MCwxMDAgUTIyMCwxMzAgMjYwLDE3MCBRMjgwLDIwMCAyNTAsMjMwIiBzdHJva2U9InJnYmEoMjUzLDIyNCwxMTUsMC4wNCkiIHN0cm9rZS13aWR0aD0iMS4yIiBvcGFjaXR5PSIwLjMiLz48L2c+PC9zdmc+'); background-size: 300px 300px;"
      ></div>
  
      <!-- Завихрения (медленные) -->
      <div class="absolute inset-0 overflow-hidden">
        <div class="swirl swirl-1"></div>
        <div class="swirl swirl-2"></div>
        <div class="swirl swirl-3"></div>
      </div>
  
      <!-- Параллакс-звёзды (foreground) -->
      <div class="absolute inset-0 overflow-hidden">
        <div 
          v-for="star in parallaxStars" 
          :key="star.id"
          class="parallax-star"
          :style="{
            left: `${star.x}%`,
            top: `${star.y}%`,
            transform: `translate(${star.offsetX}px, ${star.offsetY}px)`,
            opacity: star.opacity,
            width: `${star.size}px`,
            height: `${star.size}px`
          }"
        ></div>
      </div>
  
      <!-- Фрагменты сценария -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div 
          v-for="(fragment, i) in scriptFragments" 
          :key="i"
          class="script-fragment"
          :style="{
            left: `${fragment.x}%`,
            top: `${fragment.y}%`,
            transform: `translate(${fragment.offsetX}px, ${fragment.offsetY}px)`,
            opacity: fragment.opacity
          }"
        >
          {{ fragment.text }}
        </div>
      </div>
  
      <!-- Свечение под курсором -->
      <div 
        class="absolute inset-0 opacity-30"
        :style="{
          background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(253, 224, 71, 0.2) 0%, transparent 60%)`
        }"
      ></div>
  
      <!-- Контент -->
      <div class="relative z-10 flex flex-col justify-center min-h-screen px-4">
        <div class="max-w-md mx-auto text-center">
          <!-- Анимированный 404 -->
          <div 
            class="relative inline-flex items-center justify-center w-32 h-32 rounded-3xl mb-8 mx-auto cursor-pointer"
            @click="handle404Click"
          >
            <div 
              class="absolute inset-0 bg-gradient-to-br from-yellow-400/40 to-blue-500/40 backdrop-blur-sm rounded-3xl border border-yellow-400/50"
              :style="{
                transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
                boxShadow: `0 0 30px rgba(253, 224, 71, ${glowIntensity})`
              }"
            ></div>
            <span 
              class="text-6xl font-bold text-yellow-300 drop-shadow-[0_0_16px_rgba(253,224,71,0.7)] transition-all duration-300"
              :style="{ transform: `scale(${scale404})` }"
            >
              404
            </span>
          </div>
  
          <h1 class="text-4xl md:text-5xl font-bold mb-6">
            <span class="text-yellow-300">Страница</span>
            <span class="text-slate-100">затерялась в истории...</span>
          </h1>
  
          <p class="text-slate-200 mb-10 leading-relaxed">
            Похоже, вы забрели в уголок Storyteller AI, где даже ИИ делает перерыв на кофе.<br />
            Но не волнуйтесь — ваши проекты ждут вас дома. Или, может, пора создать что-то новое?
          </p>
  
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <NuxtLink 
              to="/"
              class="btn btn-van-gogh-primary btn-lg rounded-full transform hover:scale-105 transition-all duration-300 group"
            >
              <span class="group-hover:animate-pulse">Вернуться на главную</span>
            </NuxtLink>
            <NuxtLink 
              to="/dashboard"
              class="btn btn-van-gogh-outline btn-lg rounded-full group"
            >
              <span class="group-hover:animate-pulse">Мои проекты</span>
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  const mousePosition = reactive({ x: 0, y: 0 })
  const rotateX = ref(0)
  const rotateY = ref(0)
  const scale404 = ref(1)
  const glowIntensity = ref(0.5)
  
  // Параллакс-звёзды
  const parallaxStars = ref([])
  // Фрагменты сценария
  const scriptFragments = ref([
    { text: 'Интересные факты про электроовец', x: 10, y: 20, opacity: 0.7 },
    { text: 'Этот мужчина...', x: 80, y: 30, opacity: 0.6 },
    { text: 'Я бы лучше спаркурил', x: 20, y: 70, opacity: 0.8 },
    { text: 'Я мопс, мне..?', x: 75, y: 80, opacity: 0.5 }
  ])
  
  onMounted(() => {
    // Генерация звёзд
    for (let i = 0; i < 40; i++) {
      parallaxStars.value.push({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 3 + 1,
        opacity: 0.4 + Math.random() * 0.6,
        speed: 0.02 + Math.random() * 0.03,
        depth: Math.random() // 0 = ближе, 1 = дальше
      })
    }
  
    // Анимация фрагментов
    scriptFragments.value.forEach((frag, i) => {
      frag.x = Math.random() * 100
      frag.y = Math.random() * 100
      frag.speed = 0.01 + Math.random() * 0.02
    })
  })
  
  const handleMouseMove = (e) => {
    mousePosition.x = e.clientX
    mousePosition.y = e.clientY
  
    // Параллакс для звёзд и фрагментов
    parallaxStars.value.forEach(star => {
      const depthFactor = 1 - star.depth * 0.8
      star.offsetX = (e.clientX - window.innerWidth / 2) * star.speed * depthFactor
      star.offsetY = (e.clientY - window.innerHeight / 2) * star.speed * depthFactor
    })
  
    scriptFragments.value.forEach(frag => {
      frag.offsetX = (e.clientX - window.innerWidth / 2) * frag.speed
      frag.offsetY = (e.clientY - window.innerHeight / 2) * frag.speed
    })
  
    // 3D-эффект для 404
    const rect = e.currentTarget.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    const rotateFactor = 15
    rotateY.value = ((e.clientX - centerX) / rect.width) * rotateFactor
    rotateX.value = ((centerY - e.clientY) / rect.height) * rotateFactor
    scale404.value = 1.05
    glowIntensity.value = 0.8
  }
  
  const handleMouseLeave = () => {
    rotateX.value = 0
    rotateY.value = 0
    scale404.value = 1
    glowIntensity.value = 0.5
  }
  
  const handle404Click = () => {
    // Лёгкий "всплеск"
    scale404.value = 1.2
    glowIntensity.value = 1
    setTimeout(() => {
      scale404.value = 1
      glowIntensity.value = 0.5
    }, 300)
  }
  </script>
  
  <style scoped>
  /* Завихрения */
  .swirl {
    position: absolute;
    width: 240px;
    height: 120px;
    border-radius: 50%;
    background: radial-gradient(circle at 40% 50%, rgba(253, 224, 71, 0.06) 0%, transparent 80%);
    opacity: 0.8;
    filter: blur(1px);
    z-index: 1;
    animation: swirl 30s linear infinite;
  }
  .swirl-1 { top: 10%; left: 5%; animation-duration: 25s; }
  .swirl-2 { bottom: 15%; right: 10%; animation-duration: 35s; animation-direction: reverse; }
  .swirl-3 { top: 50%; right: 20%; animation-duration: 40s; }
  
  /* Параллакс-звёзды */
  .parallax-star {
    position: absolute;
    background: #fde047;
    border-radius: 50%;
    pointer-events: none;
    transition: transform 0.1s ease-out;
    box-shadow: 0 0 10px #fde047, 0 0 20px rgba(253, 224, 71, 0.5);
  }
  
  /* Фрагменты сценария */
  .script-fragment {
    position: absolute;
    color: rgba(253, 224, 71, 0.7);
    font-family: 'Courier New', monospace;
    font-size: 0.875rem;
    opacity: 0.7;
    pointer-events: none;
    transition: transform 0.1s ease-out;
    text-shadow: 0 0 8px rgba(253, 224, 71, 0.8);
  }
  
  @keyframes swirl {
    0% { transform: rotate(0deg) scale(1); }
    100% { transform: rotate(360deg) scale(1.05); }
  }
  </style>