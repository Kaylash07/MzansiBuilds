<template>
  <div class="home">
    <section class="hero">
      <h1>Welcome to MzansiBuilds</h1>
      <p>Your ultimate platform for quality building projects.</p>
    </section>

    <section class="features">
      <h2>Feature Highlights</h2>
      <ul>
        <li>Expert Builders</li>
        <li>Affordable Pricing</li>
        <li>Quality Assurance</li>
        <li>24/7 Customer Support</li>
      </ul>
    </section>

    <section class="live-projects">
      <h2>Live Projects Preview</h2>
      <div class="project">
        <h3>Project 1</h3>
        <p>Description of live project 1.</p>
      </div>
      <div class="project">
        <h3>Project 2</h3>
        <p>Description of live project 2.</p>
      </div>
      <div class="project">
        <h3>Project 3</h3>
        <p>Description of live project 3.</p>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'Home',
};
</script>

<style scoped>
.hero {
  background-color: #f8f9fa;
  padding: 20px;
  text-align: center;
}
.features {
  padding: 20px;
}
.live-projects {
  padding: 20px;
}
.project {
  margin: 10px 0;
}
</style>
