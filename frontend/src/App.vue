<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navbar -->
    <nav class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-bold text-blue-600">Resume Matcher</h1>
          <div class="flex gap-8 text-sm font-medium">
            <button
              @click="currentView = 'upload'"
              :class="currentView === 'upload' ? 'text-blue-600 border-b-2 border-blue-600 pb-1' : 'text-gray-600 hover:text-gray-800'"
            >
              1. Upload Resumes
            </button>
            <button
              @click="currentView = 'job'"
              :class="currentView === 'job' ? 'text-blue-600 border-b-2 border-blue-600 pb-1' : 'text-gray-600 hover:text-gray-800'"
            >
              2. Enter Job Description
            </button>
            <button
              @click="currentView = 'results'"
              :class="currentView === 'results' ? 'text-blue-600 border-b-2 border-blue-600 pb-1' : 'text-gray-600 hover:text-gray-800'"
              :disabled="store.matches.length === 0"
            >
              3. View Matches
            </button>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-6 py-8">
      <!-- View 1: Resume Upload -->
      <ResumeUpload v-if="currentView === 'upload'" />

      <!-- View 2: Job Input -->
      <JobInput 
        v-else-if="currentView === 'job'" 
        @job-submitted="goToResults"
      />

      <!-- View 3: Results -->
      <div v-else-if="currentView === 'results'">
        <CandidateList 
          :matches="store.matches" 
          @show-insight="showInsight"
          @back="currentView = 'job'"
        />
      </div>
    </div>

    <!-- Insight Modal -->
    <div 
      v-if="showModal" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    >
      <CandidateInsight 
        v-if="selectedMatch"
        :candidate="selectedMatch.candidate"
        :match-score="selectedMatch.score"
        @close="closeModal"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMatchingStore } from './stores/matchingStore'

// Import Components
import ResumeUpload from './components/ResumeUpload.vue'
import JobInput from './components/JobInput.vue'
import CandidateList from './components/CandidateList.vue'
import CandidateInsight from './components/CandidateInsight.vue'

const store = useMatchingStore()

const currentView = ref('upload')     // 'upload' | 'job' | 'results'
const showModal = ref(false)
const selectedMatch = ref(null)

// Go to results after job is submitted
const goToResults = () => {
  currentView.value = 'results'
}

// Show AI Insights in modal
const showInsight = (match) => {
  selectedMatch.value = match
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedMatch.value = null
}

// Optional: Auto load last matches if any
onMounted(() => {
  if (store.matches.length > 0) {
    currentView.value = 'results'
  }
})
</script>

<style>
/* Optional: Smooth transition */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>