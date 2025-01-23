<template>
  <div class="app-container">
    <router-view></router-view>
  </div>
</template>

<script setup>
// 使用组合式API，无需额外的setup函数
</script>

<style>
.app-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>