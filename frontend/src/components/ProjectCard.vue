<template>
  <div class="project-card">
    <h2>{{ project.title }}</h2>
    <p>{{ project.description }}</p>
    <p><strong>Created on:</strong> {{ project.createdAt }}</p>
    <p><strong>Status:</strong> {{ project.status }}</p>
    <button @click="viewProject">View Project</button>
  </div>
</template>

<script>
export default {
  name: 'ProjectCard',
  props: {
    project: {
      type: Object,
      required: true
    }
  },
  methods: {
    viewProject() {
      // Logic to view project goes here
    }
  }
}
</script>

<style scoped>
.project-card {
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 16px;
  margin: 16px;
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
}
</style>