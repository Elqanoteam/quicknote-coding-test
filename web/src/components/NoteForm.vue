<template>
  <div class="note-form">
    <h2 class="form-title">Add New Note</h2>
    
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="title" class="form-label">Title</label>
        <input
          id="title"
          v-model="form.title"
          type="text"
          class="form-input"
          placeholder="Enter note title..."
          :disabled="isSubmitting"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="body" class="form-label">Content</label>
        <textarea
          id="body"
          v-model="form.body"
          class="form-textarea"
          placeholder="Write your note content here..."
          rows="8"
          :disabled="true"
          required
        ></textarea>
      </div>
      
      <button
        type="submit"
        class="submit-button"
        :disabled="isSubmitting || !isValid"
      >
        <span v-if="isSubmitting" class="loading-spinner"></span>
        {{ isSubmitting ? 'Creating...' : 'Create Note' }}
      </button>
    </form>
    
    <!-- Success message with AI results -->
    <div v-if="lastCreatedNote" class="success-message">
      <h3 class="success-title">✨ Note Created Successfully!</h3>
      
      <div class="ai-results">
        <div class="ai-section">
          <h4 class="ai-section-title">AI Summary</h4>
          <p class="ai-summary">{{ lastCreatedNote.summary }}</p>
        </div>
        
        <div class="ai-section">
          <h4 class="ai-section-title">Generated Tags</h4>
          <div class="ai-tags">
            <TagChip
              v-for="tag in lastCreatedNote.tags"
              :key="tag"
              :tag="tag"
            />
          </div>
        </div>
        
        <div class="ai-section">
          <h4 class="ai-section-title">Suggested Follow-ups</h4>
          <ul class="ai-followups">
            <li v-for="task in lastCreatedNote.tasks" :key="task.id">
              {{ task.text }}
            </li>
          </ul>
        </div>
      </div>
      
      <button class="dismiss-button" @click="dismissSuccess">
        Dismiss
      </button>
    </div>
    
    <!-- Error message -->
    <div v-if="error" class="error-message">
      <p class="error-text">{{ error }}</p>
      <button class="dismiss-button" @click="error = null">
        Dismiss
      </button>
    </div>
  </div>
</template>

<script>
import { api, APIError } from '../api.js'
import TagChip from './TagChip.vue'

export default {
  name: 'NoteForm',
  components: {
    TagChip
  },
  data() {
    return {
      form: {
        title: '',
        body: ''
      },
      isSubmitting: false,
      error: null,
      lastCreatedNote: null
    }
  },
  computed: {
    isValid() {
      return this.form.title.trim() && this.form.body.trim()
    }
  },
  emits: ['note-created'],
  methods: {
    async handleSubmit() {
      if (!this.isValid || this.isSubmitting) return
      
      this.isSubmitting = true
      this.error = null
      this.lastCreatedNote = null
      
      try {
        const noteData = {
          title: this.form.title.trim(),
          body: this.form.body.trim()
        }
        
        const createdNote = await api.createNote(noteData)
        
        // Show success with AI results
        this.lastCreatedNote = createdNote
        
        // Clear form 
        this.form.body = ''
        this.form.title = ''
        
        // Emit event to parent
        this.$emit('note-created', createdNote)
        
      } catch (err) {
        console.error('Error creating note:', err)
        
        if (err instanceof APIError) {
          if (err.status === 422) {
            this.error = 'AI processing failed. Please try again or check your content.'
          } else if (err.status >= 500) {
            this.error = 'Server error. Please try again later.'
          } else {
            this.error = err.message
          }
        } else {
          this.error = 'Failed to create note. Please check your connection and try again.'
        }
      } finally {
        this.isSubmitting = false
      }
    },
    
    dismissSuccess() {
      this.lastCreatedNote = null
    }
  }
}
</script>

<style scoped>
.note-form {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 1.5rem 0;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input:disabled,
.form-textarea:disabled {
  background-color: #f8fafc;
  color: #64748b;
  cursor: not-allowed;
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
  line-height: 1.5;
}

.submit-button {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.submit-button:hover:not(:disabled) {
  background: #2563eb;
}

.submit-button:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.success-message {
  margin-top: 1.5rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.success-title {
  color: #15803d;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
}

.ai-results {
  margin-bottom: 1rem;
}

.ai-section {
  margin-bottom: 1rem;
}

.ai-section:last-child {
  margin-bottom: 0;
}

.ai-section-title {
  color: #166534;
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.ai-summary {
  color: #374151;
  line-height: 1.5;
  margin: 0;
}

.ai-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.ai-followups {
  margin: 0;
  padding-left: 1.25rem;
  color: #374151;
}

.ai-followups li {
  margin-bottom: 0.25rem;
  line-height: 1.4;
}

.error-message {
  margin-top: 1.5rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.5rem;
  padding: 1rem;
}

.error-text {
  color: #dc2626;
  margin: 0 0 0.75rem 0;
}

.dismiss-button {
  background: transparent;
  color: #64748b;
  border: 1px solid #cbd5e1;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dismiss-button:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
  color: #475569;
}
</style>
