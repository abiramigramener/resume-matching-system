import { defineStore } from 'pinia'
import axios from 'axios'

export const useMatchingStore = defineStore('matching', {
  state: () => ({
    matches: [],
    currentCandidate: null,
    currentInsights: null,
    lastJobDescription: ''
  }),

  actions: {
    async matchJob(formData) {
      // Always capture full job context for insights
      const title = formData.get('title') || ''
      const description = formData.get('description') || ''
      this.lastJobDescription = `${title}\n\n${description}`.trim() || title
      const response = await axios.post(
        'http://localhost:8000/api/matching/match',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      this.matches = response.data.matches || []
      return response
    },

    async fetchInsights(jobDescription, candidateId, score) {
      const form = new FormData()
      form.append('job_description', jobDescription)
      form.append('candidate_id', candidateId)
      form.append('score', score)
      const response = await axios.post(
        'http://localhost:8000/api/matching/insights',
        form,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      return response.data.insights
    },

    setCurrentCandidate(candidate, insights, score) {
      this.currentCandidate = candidate
      this.currentInsights = insights
      this.currentScore = score
    }
  }
})