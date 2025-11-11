<template>
  <header class="navbar bg-base-200 shadow-lg sticky top-0 z-50">
    <div class="navbar-start">
      <NuxtLink to="/dashboard" class="btn btn-ghost normal-case text-xl">
        <span class="text-primary">Storyteller</span>
        <span class="text-base-content">AI</span>
      </NuxtLink>
    </div>
    
    <div class="navbar-center hidden lg:flex">
      <ul class="menu menu-horizontal px-1">
        <li><NuxtLink to="/dashboard" class="active:bg-primary">Мои проекты</NuxtLink></li>
        <li><a href="#" @click.prevent="createNewProject">Новый проект</a></li>
      </ul>
    </div>
    
    <div class="navbar-end">
      <div class="dropdown dropdown-end" v-if="user">
        <label tabindex="0" class="btn btn-ghost btn-circle avatar">
          <div class="w-10 rounded-full bg-primary text-primary-content flex items-center justify-center">
            {{ user.email?.charAt(0).toUpperCase() }}
          </div>
        </label>
        <ul tabindex="0" class="mt-3 p-2 shadow menu menu-compact dropdown-content bg-base-200 rounded-box w-52">
          <li class="menu-title">
            <span>{{ user.email }}</span>
          </li>
          <li><a @click="signOut">Выйти</a></li>
        </ul>
      </div>
    </div>
  </header>
</template>

<script setup>
const { user, signOut } = useSupabaseAuth()
const router = useRouter()

const createNewProject = () => {
  router.push('/project/new')
}
</script>