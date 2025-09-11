<template>
  <div class="note-card">
    <div class="note-header">
      <h3 class="note-title">{{ note.title }}</h3>
      <div class="note-meta">
        <span class="note-date">{{ formatDate(note.created_at) }}</span>
        <span v-if="note.similarity !== null" class="similarity-score">
          {{ (note.similarity * 100).toFixed(1) }}% match
        </span>
      </div>
    </div>
    
    <p class="note-summary">{{ note.summary }}</p>
    
    <div class="note-tags">
      <TagChip
        v-for="tag in note.tags"
        :key="tag"
        :tag="tag"
        :clickable="true"
        @click="handleTagClick"
      />
    </div>
    
    <div class="note-actions">
      <button class="view-button" @click="viewNote">
        View Details
      </button>
      <span class="task-count">
        {{ note.tasks.length }} task{{ note.tasks.length !== 1 ? 's' : '' }}
      </span>
    </div>
  </div>
</template>

<script>
import TagChip from './TagChip.vue'

export default {
  name: 'NoteCard',
  components: {
    TagChip
  },
  props: {
    note: {
      type: Object,
      required: true
    }
  },
  emits: ['view-note', 'tag-click'],
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString)
      const now = new Date()
      const diffTime = Math.abs(now - date)
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) {
        return 'Today'
      } else if (diffDays === 1) {
        return 'Yesterday'
      } else if (diffDays < 7) {
        return `${diffDays} days ago`
      } else {
        return date.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
        })
      }
    },
    
    viewNote() {
      this.$emit('view-note', 1)
    },
    
    handleTagClick(tag) {
      this.$emit('tag-click', tag)
    }
  }
}
</script>

<style scoped>
.note-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.note-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.note-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  line-height: 1.3;
  flex: 1;
  margin-right: 1rem;
}

.note-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
  flex-shrink: 0;
}

.note-date {
  font-size: 0.875rem;
  color: #64748b;
}

.similarity-score {
  font-size: 0.75rem;
  color: #059669;
  background: #d1fae5;
  padding: 0.125rem 0.375rem;
  border-radius: 0.375rem;
  font-weight: 500;
}

.note-summary {
  color: #475569;
  line-height: 1.5;
  margin: 0 0 1rem 0;
}

.note-tags {
  margin-bottom: 1rem;
}

.note-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.view-button {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.view-button:hover {
  background: #2563eb;
}

.task-count {
  font-size: 0.875rem;
  color: #64748b;
}

@media (max-width: 640px) {
  .note-header {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .note-meta {
    align-items: flex-start;
    flex-direction: row;
    gap: 0.75rem;
  }
}
</style>
