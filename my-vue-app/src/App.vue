<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">⏱️ Tablet</div>
      <nav class="nav">
        <RouterLink to="/">Start</RouterLink>
        <RouterLink to="/scan">Rejestracja</RouterLink>
        <RouterLink to="/status">Status</RouterLink>
      </nav>
    </header>

    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>
