<template>
  <div class="search-bar">
    <div class="search-input-container">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search notes..."
        class="search-input"
        @input="handleInput"
      />
      <div class="search-icon">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
      </div>
    </div>
    <div v-if="isSearching" class="search-status">
      Searching...
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchBar',
  data() {
    return {
      searchQuery: '',
      searchTimeout: null,
      isSearching: false
    }
  },
  emits: ['search'],
  methods: {
    handleInput() {
      // Clear existing timeout
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout)
      }
      
      // Show searching status for non-empty queries
      this.isSearching = this.searchQuery.trim() !== ''
      
      // Debounce search for 300ms
      this.searchTimeout = setTimeout(() => {
        this.performSearch()
      }, 300)
    },
    
    performSearch() {
      this.isSearching = false
      const query = this.searchQuery.trim()
      this.$emit('search', query || null)
    },
    
    clearSearch() {
      this.searchQuery = ''
      this.isSearching = false
      this.$emit('search', null)
    }
  },
  
  beforeUnmount() {
    if (this.searchTimeout) {
      clearTimeout(this.searchTimeout)
    }
  }
}
</script>

<style scoped>
.search-bar {
  margin-bottom: 1rem;
}

.search-input-container {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  padding-right: 2.5rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
}

.search-status {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #64748b;
  font-style: italic;
}

@media (max-width: 768px) {
  .search-bar {
    display: none;
  }
}
</style>
