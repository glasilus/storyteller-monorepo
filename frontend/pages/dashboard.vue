<template>
  <div>
    <AppHeader />
    
    <main class="container mx-auto px-4 py-8 max-w-6xl">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold">Мои проекты</h1>
        <button class="btn btn-primary" @click="createNewProject">
          <span class="text-2xl">+</span> Новый проект
        </button>
      </div>

      <!-- Состояние загрузки -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 4" :key="i" class="card bg-base-200 shadow-xl">
          <div class="card-body">
            <div class="skeleton h-6 w-3/4 mb-2"></div>
            <div class="skeleton h-4 w-full mb-4"></div>
            <div class="skeleton h-10 w-full"></div>
          </div>
        </div>
      </div>

      <!-- Список проектов -->
      <div v-else-if="projects.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ProjectCard 
          v-for="project in projects" 
          :key="project.id" 
          :project="project"
          @delete="handleDeleteProject"
        />
      </div>

      <!-- Пустое состояние -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4 opacity-30">🎬</div>
        <h2 class="text-2xl font-bold mb-4">У вас пока нет проектов</h2>
        <p class="mb-6 opacity-70">Создайте ваш первый проект и начните генерировать сценарии</p>
        <button class="btn btn-primary btn-lg" @click="createNewProject">
          Создать проект
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
definePageMeta({
  layout: 'default'
})

const { requireAuth } = useSupabaseAuth()
const { getUserProjects, saveProject } = useApi()
const router = useRouter()

const loading = ref(true)
const projects = ref([])

// Проверка авторизации
onMounted(async () => {
  if (!requireAuth()) return
  await loadProjects()
})

const loadProjects = async () => {
  try {
    loading.value = true
    projects.value = await getUserProjects()
  } catch (error) {
    console.error('Ошибка загрузки проектов:', error)
    alert('Не удалось загрузить проекты')
  } finally {
    loading.value = false
  }
}

const createNewProject = async () => {
  try {
    const newProject = {
      title: 'Новый проект',
      description: 'Опишите вашу идею здесь...',
      script: null,
      scenes: []
    }
    
    const created = await saveProject(newProject)
    router.push(`/project/${created.id}`)
  } catch (error) {
    console.error('Ошибка создания проекта:', error)
    alert('Не удалось создать проект')
  }
}

const handleDeleteProject = async (projectId) => {
  try {
    // Здесь добавьте вызов API для удаления
    // await deleteProject(projectId)
    projects.value = projects.value.filter(p => p.id !== projectId)
  } catch (error) {
    console.error('Ошибка удаления проекта:', error)
  }
}
</script>