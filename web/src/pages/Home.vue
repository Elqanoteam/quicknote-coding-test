<template>
  <div class="home-page">
    <header class="page-header">
      <h1 class="page-title">📝 Notes Copilot</h1>
      <p class="page-subtitle">AI-powered note taking with semantic search</p>
    </header>
    
    <div class="home-layout">
      <!-- Left column: Note form -->
      <div class="form-column">
        <NoteForm @note-created="handleNoteCreated" />
      </div>
      
      <!-- Right column: Search and notes list -->
      <div class="notes-column">
        <SearchBar @search="handleSearch" />
        
        <!-- Loading state -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner large"></div>
          <p>{{ searchQuery ? 'Searching notes...' : 'Loading notes...' }}</p>
        </div>
        
        <!-- Error state -->
        <div v-else-if="error" class="error-state">
          <p class="error-text">{{ error }}</p>
          <button class="retry-button" @click="loadNotes">
            Try Again
          </button>
        </div>
        
        <!-- Empty state -->
        <div v-else-if="notes.length === 0" class="empty-state">
          <div class="empty-icon">📝</div>
          <p class="empty-text">
            {{ searchQuery ? 'No notes found for your search.' : 'No notes yet. Create your first note!' }}
          </p>
        </div>
        
        <!-- Notes list -->
        <div v-else class="notes-list">
          <div v-if="searchQuery" class="search-results-header">
            <p class="search-info">
              Found {{ totalNotes }} result{{ totalNotes !== 1 ? 's' : '' }} for "{{ searchQuery }}"
            </p>
          </div>
          
          <NoteCard
            v-for="note in notes"
            :key="note.id"
            :note="note"
            @view-note="viewNote"
            @tag-click="searchByTag"
            @note-deleted="handleNoteDeleted"
          />
          
          <!-- Load more button -->
          <div v-if="hasMore" class="load-more">
            <button 
              class="load-more-button"
              @click="loadMore"
              :disabled="isLoadingMore"
            >
              <span v-if="isLoadingMore" class="loading-spinner"></span>
              {{ isLoadingMore ? 'Loading...' : 'Load More' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api, APIError } from '../api.js'
import NoteForm from '../components/NoteForm.vue'
import SearchBar from '../components/SearchBar.vue'
import NoteCard from '../components/NoteCard.vue'

export default {
  name: 'Home',
  components: {
    NoteForm,
    SearchBar,
    NoteCard
  },
  data() {
    return {
      notes: [],
      isLoading: false,
      isLoadingMore: false,
      error: null,
      searchQuery: null,
      totalNotes: 0,
      currentOffset: 0,
      limit: 10
    }
  },
  computed: {
    hasMore() {
      return this.notes.length < this.totalNotes
    }
  },
  async mounted() {
    await this.loadNotes()
  },
  methods: {
    async loadNotes(reset = true) {
      if (reset) {
        this.isLoading = true
        this.currentOffset = 0
        this.notes = []
      } else {
        this.isLoadingMore = true
      }
      
      this.error = null
      
      try {
        const response = await api.listNotes({
          search: this.searchQuery,
          limit: this.limit,
          offset: this.currentOffset
        })
        
        if (reset) {
          this.notes = response.notes
        } else {
          this.notes.push(...response.notes)
        }
        
        this.totalNotes = response.total
        this.currentOffset += response.notes.length
        
      } catch (err) {
        console.error('Error loading notes:', err)
        
        if (err instanceof APIError) {
          if (err.status === 422) {
            this.error = 'Search failed. Please try a different query.'
          } else if (err.status >= 500) {
            this.error = 'Server error. Please try again later.'
          } else {
            this.error = err.message
          }
        } else {
          this.error = 'Failed to load notes. Please check your connection.'
        }
      } finally {
        this.isLoading = false
        this.isLoadingMore = false
      }
    },
    
    async loadMore() {
      if (this.hasMore && !this.isLoadingMore) {
        await this.loadNotes(false)
      }
    },
    
    async handleSearch(query) {
      this.searchQuery = query
      await this.loadNotes()
    },
    
    async handleNoteCreated(note) {
      // If not searching, add the new note to the top of the list
      if (!this.searchQuery) {
        this.notes.unshift(note)
        this.totalNotes += 1
      }
      // If searching, refresh the search results
      else {
        await this.loadNotes()
      }
    },
    
    viewNote(noteId) {
      this.$router.push({ name: 'NoteDetail', params: { id: noteId } })
    },
    
    async searchByTag(tag) {
      this.searchQuery = tag
      await this.loadNotes()
    },

    handleNoteDeleted(noteId) {
      // Remove the note from the local list
      this.notes = this.notes.filter(note => note.id !== noteId)
      this.totalNotes -= 1
    }
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f8fafc;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 2rem;
  text-align: center;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.page-subtitle {
  font-size: 1.125rem;
  color: #64748b;
  margin: 0;
}

.home-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.form-column,
.notes-column {
  min-height: 500px;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-spinner.large {
  width: 32px;
  height: 32px;
  border-width: 3px;
  color: #3b82f6;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-text {
  color: #dc2626;
  margin: 0 0 1rem 0;
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

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-text {
  color: #64748b;
  font-size: 1.125rem;
  margin: 0;
}

.search-results-header {
  margin-bottom: 1rem;
}

.search-info {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
  font-style: italic;
}

.notes-list {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.load-more {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.load-more-button {
  background: #e2e8f0;
  color: #475569;
  border: 1px solid #cbd5e1;
  padding: 0.75rem 2rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.load-more-button:hover:not(:disabled) {
  background: #cbd5e1;
  border-color: #94a3b8;
}

.load-more-button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

@media (max-width: 1024px) {
  .home-layout {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

@media (max-width: 640px) {
  .page-header {
    padding: 1.5rem 1rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .home-layout {
    padding: 1rem;
    gap: 1rem;
  }
}
</style>
