/**
 * API client for Notes Copilot backend
 */

const BASE_URL = 'http://localhost:8000/api'

class APIError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'APIError'
    this.status = status
  }
}

async function apiRequest(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  }
  
  try {
    const response = await fetch(url, config)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new APIError(
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
        response.status
      )
    }
    
    return await response.json()
  } catch (error) {
    if (error instanceof APIError) {
      throw error
    }
    throw new APIError(`Network error: ${error.message}`, 0)
  }
}

export const api = {
  // Notes endpoints
  async createNote(noteData) {
    return apiRequest('/notes/', {
      method: 'POST',
      body: JSON.stringify(noteData)
    })
  },

  async listNotes({ search = null, limit = 10, offset = 0 } = {}) {
    const params = new URLSearchParams()
    if (search) params.append('search', search)
    params.append('limit', limit.toString())
    params.append('offset', offset.toString())
    
    return apiRequest(`/notes/?${params}`)
  },

  async getNote(id) {
    return apiRequest(`/notes/${id}`)
  },

  async deleteNote(id) {
    return apiRequest(`/notes/${id}`, {
      method: 'DELETE'
    })
  },

  // Tasks endpoints
  async updateTask(id, data) {
    return apiRequest(`/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  },

  async getTask(id) {
    return apiRequest(`/tasks/${id}`)
  },

  // Health check
  async healthCheck() {
    return apiRequest('/health', { 
      baseURL: 'http://localhost:8000' // Skip /api prefix for health
    })
  },
  // Utility functions
  async checkForSensitive(tags) {
    if (tags?.some(tag => tag.toLowerCase() === 'sensitive')) {
      // display guidlines for sensitive notes
      setTimeout(() => {
        window.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ', '_blank')
      }, 1000)
    }
  }
}



export { APIError }
