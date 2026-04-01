import { defineStore } from 'pinia'
import axios from 'axios'

export const useMatchingStore = defineStore('matching', {
  state: () => ({
    matches: [],
    currentCandidate: null,
    currentInsights: null
  }),

  actions: {
    async matchJob(formData) {
      const response = await axios.post(
        'http://localhost:8000/api/matching/match',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      this.matches = response.data.matches || []
      return response
    },

    setCurrentCandidate(candidate, insights, score) {
      this.currentCandidate = candidate
      this.currentInsights = insights
      this.currentScore = score
    }
  }
})