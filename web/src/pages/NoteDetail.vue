<template>
  <div class="note-detail-page">
    <!-- Header with back button -->
    <header class="detail-header">
      <button class="back-button" @click="goBack">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15,18 9,12 15,6"></polyline>
        </svg>
        Back to Notes
      </button>
    </header>
    
    <!-- Loading state -->
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner large"></div>
      <p>Loading note...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="error-state">
      <h2 class="error-title">Note Not Found</h2>
      <p class="error-text">{{ error }}</p>
      <button class="retry-button" @click="loadNote">
        Try Again
      </button>
    </div>
    
    <!-- Note content -->
    <div v-else-if="note" class="note-content">
      <div class="note-header">
        <h1 class="note-title">{{ note.title }}</h1>
        <div class="note-meta">
          <span class="note-date">{{ formatDate(note.created_at) }}</span>
        </div>
      </div>
      
      <!-- AI Summary -->
      <div class="note-section">
        <h2 class="section-title">📄 AI Summary</h2>
        <p class="note-summary">{{ note.summary }}</p>
      </div>
      
      <!-- Full Content -->
      <div class="note-section">
        <h2 class="section-title">📝 Full Content</h2>
        <div class="note-body">{{ note.body }}</div>
      </div>
      
      <!-- Tags -->
      <div class="note-section">
        <h2 class="section-title">🏷️ Tags</h2>
        <div class="tags-container">
          <TagChip
            v-for="tag in note.tags"
            :key="tag"
            :tag="tag"
            :clickable="true"
            @click="searchByTag"
          />
        </div>
      </div>
      
      <!-- Tasks -->
      <div class="note-section">
        <h2 class="section-title">✅ Follow-up Tasks</h2>
        <div v-if="note.tasks.length === 0" class="no-tasks">
          No tasks for this note.
        </div>
        <div v-else class="tasks-list">
          <div
            v-for="task in note.tasks"
            :key="task.id"
            class="task-item"
            :class="{ completed: task.status === 'done' }"
          >
            <label class="task-checkbox-label">
              <input
                type="checkbox"
                :checked="task.status === 'done'"
                @change="toggleTask(task)"
                class="task-checkbox"
              />
              <span class="task-text">{{ task.text }}</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api, APIError } from '../api.js'
import TagChip from '../components/TagChip.vue'

export default {
  name: 'NoteDetail',
  components: {
    TagChip
  },
  props: {
    id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      note: null,
      isLoading: false,
      error: null
    }
  },
  async mounted() {
    await this.loadNote()
  },
  async beforeRouteUpdate(to, from, next) {
    // Called when the route changes but the same component is reused
    if (to.params.id !== from.params.id) {
      await this.loadNote(to.params.id)
    }
    next()
  },
  methods: {
    async loadNote(noteId = null) {
      const id = noteId || this.id
      this.isLoading = true
      this.error = null
      
      try {
        this.note = await api.getNote(id)
      } catch (err) {
        console.error('Error loading note:', err)
        
        if (err instanceof APIError) {
          if (err.status === 404) {
            this.error = 'This note could not be found. It may have been deleted.'
          } else if (err.status >= 500) {
            this.error = 'Server error. Please try again later.'
          } else {
            this.error = err.message
          }
        } else {
          this.error = 'Failed to load note. Please check your connection.'
        }
      } finally {
        this.isLoading = false
      }
    },
    
    async toggleTask(task) {
      const newStatus = task.status === 'done' ? 'open' : 'done'
      
      try {
        await api.updateTask(task.id, { status: newStatus })
        
        // Update local state
        task.status = newStatus
        
      } catch (err) {
        console.error('Error updating task:', err)
        
        // Show a simple error message (could be enhanced with a toast)
        alert('Failed to update task. Please try again.')
      }
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    goBack() {
      this.$router.push({ name: 'Home' })
    },
    
    searchByTag(tag) {
      this.$router.push({ 
        name: 'Home', 
        query: { search: tag } 
      })
    }
  }
}
</script>

<style scoped>
.note-detail-page {
  min-height: 100vh;
  background: #f8fafc;
}

.detail-header {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 1rem 2rem;
}

.back-button {
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #64748b;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.back-button:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #475569;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid transparent;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-title {
  color: #dc2626;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.error-text {
  color: #64748b;
  margin: 0 0 1.5rem 0;
  font-size: 1.125rem;
}

.retry-button {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.retry-button:hover {
  background: #2563eb;
}

.note-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.note-header {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.note-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 1rem 0;
  line-height: 1.3;
}

.note-meta {
  color: #64748b;
  font-size: 0.875rem;
}

.note-date {
  font-weight: 500;
}

.note-section {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.note-summary {
  color: #475569;
  line-height: 1.6;
  font-size: 1.125rem;
  margin: 0;
}

.note-body {
  color: #374151;
  line-height: 1.6;
  white-space: pre-wrap;
  font-size: 1rem;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.no-tasks {
  color: #64748b;
  font-style: italic;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.task-item {
  transition: opacity 0.2s ease;
}

.task-item.completed {
  opacity: 0.6;
}

.task-checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1.5;
}

.task-checkbox {
  margin-top: 0.125rem;
  width: 1.125rem;
  height: 1.125rem;
  cursor: pointer;
}

.task-text {
  flex: 1;
  color: #374151;
}

.task-item.completed .task-text {
  text-decoration: line-through;
  color: #6b7280;
}

@media (max-width: 768px) {
  .detail-header {
    padding: 1rem;
  }
  
  .note-content {
    padding: 1rem;
  }
  
  .note-header {
    padding: 1.5rem;
  }
  
  .note-title {
    font-size: 1.5rem;
  }
  
  .note-section {
    padding: 1rem;
  }
}
</style>
