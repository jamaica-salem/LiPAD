<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const message = ref('Loading...')

onMounted(() => {
  axios.get('http://127.0.0.1:8000/api/hello/')
    .then(response => {
      message.value = response.data.message
    })
    .catch(error => {
      console.error(error)
      message.value = 'Error fetching data'
    })
})
</script>

<template>
  <div>
    <h1>{{ message }}</h1>
  </div>
</template>
