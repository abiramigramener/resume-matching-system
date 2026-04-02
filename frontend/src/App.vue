<template>
  <div class="min-h-screen bg-slate-50">

    <!-- Top Nav -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-40">
      <div class="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <!-- Logo -->
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
            <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span class="font-semibold text-slate-900 text-[15px] tracking-tight">ResumeMatch</span>
        </div>

        <!-- Step Nav -->
        <nav class="flex items-center gap-1" role="tablist">
          <button
            v-for="(step, i) in steps"
            :key="step.id"
            role="tab"
            :aria-selected="currentView === step.id"
            :disabled="step.id === 'results' && store.matches.length === 0"
            @click="currentView = step.id"
            class="relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed"
            :class="currentView === step.id
              ? 'bg-indigo-50 text-indigo-700'
              : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100'"
          >
            <span
              class="w-5 h-5 rounded-full text-xs flex items-center justify-center font-semibold shrink-0"
              :class="currentView === step.id ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-500'"
            >{{ i + 1 }}</span>
            {{ step.label }}
          </button>
        </nav>
      </div>
    </header>

    <!-- Page Content -->
    <main class="max-w-6xl mx-auto px-6 py-10">
      <Transition name="fade" mode="out-in">
        <ResumeUpload v-if="currentView === 'upload'" key="upload" />
        <JobInput v-else-if="currentView === 'job'" key="job" @job-submitted="goToResults" />
        <CandidateList
          v-else-if="currentView === 'results'"
          key="results"
          :matches="store.matches"
          @show-insight="showInsight"
          @back="currentView = 'job'"
        />
      </Transition>
    </main>

    <!-- Insight Modal -->
    <Transition name="fade">
      <div
        v-if="showModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        style="background: rgba(15,23,42,0.55); backdrop-filter: blur(4px);"
        @click.self="closeModal"
        role="dialog"
        aria-modal="true"
      >
        <Transition name="slide-up">
          <CandidateInsight
            v-if="selectedMatch"
            :candidate="selectedMatch.candidate"
            :match-score="selectedMatch.score"
            @close="closeModal"
          />
        </Transition>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMatchingStore } from './stores/matchingStore'
import ResumeUpload from './components/ResumeUpload.vue'
import JobInput from './components/JobInput.vue'
import CandidateList from './components/CandidateList.vue'
import CandidateInsight from './components/CandidateInsight.vue'

const store = useMatchingStore()
const currentView = ref('upload')
const showModal = ref(false)
const selectedMatch = ref(null)

const steps = [
  { id: 'upload', label: 'Upload Resumes' },
  { id: 'job',    label: 'Job Description' },
  { id: 'results', label: 'View Matches' },
]

const goToResults = () => { currentView.value = 'results' }
const showInsight = (match) => { selectedMatch.value = match; showModal.value = true }
const closeModal = () => { showModal.value = false; selectedMatch.value = null }

onMounted(() => {
  if (store.matches.length > 0) currentView.value = 'results'
})
</script>
