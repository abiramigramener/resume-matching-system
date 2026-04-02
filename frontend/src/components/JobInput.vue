<template>
  <div class="max-w-2xl mx-auto">
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-semibold text-slate-900">Job Description</h1>
      <p class="text-slate-500 mt-1 text-sm">Describe the role and we'll rank candidates by relevance.</p>
    </div>

    <div class="bg-white border border-slate-200 rounded-xl shadow-sm p-6 space-y-5">
      <!-- Job Title -->
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1.5" for="job-title">
          Job Title <span class="text-red-400">*</span>
        </label>
        <input
          id="job-title"
          v-model="jobData.title"
          type="text"
          placeholder="e.g. Senior Data Scientist"
          class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
        />
      </div>

      <!-- Experience -->
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1.5" for="exp">
          Minimum Experience (years)
        </label>
        <input
          id="exp"
          v-model.number="jobData.required_experience"
          type="number"
          min="0"
          max="30"
          class="w-32 px-4 py-2.5 text-sm border border-slate-300 rounded-lg bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
        />
      </div>

      <!-- Divider with OR -->
      <div class="relative">
        <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-slate-200"></div></div>
        <div class="relative flex justify-start">
          <span class="bg-white pr-3 text-xs font-medium text-slate-400 uppercase tracking-wider">Description</span>
        </div>
      </div>

      <!-- Description textarea -->
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1.5" for="jd-text">
          Paste job requirements
        </label>
        <textarea
          id="jd-text"
          v-model="jobData.description"
          rows="7"
          placeholder="List required skills, responsibilities, qualifications..."
          class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition resize-none"
        ></textarea>
      </div>

      <!-- File upload -->
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1.5">Or upload a JD file</label>
        <label
          class="flex items-center gap-3 px-4 py-2.5 border border-slate-300 rounded-lg cursor-pointer hover:bg-slate-50 transition group"
        >
          <svg class="w-4 h-4 text-slate-400 group-hover:text-indigo-500 transition shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 01-6.364-6.364l10.94-10.94A3 3 0 1119.5 7.372L8.552 18.32m.009-.01l-.01.01m5.699-9.941l-7.81 7.81a1.5 1.5 0 002.112 2.13" />
          </svg>
          <span class="text-sm text-slate-500 group-hover:text-slate-700 transition truncate">
            {{ selectedFileName || 'Choose file (PDF, DOCX, TXT…)' }}
          </span>
          <input
            type="file"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.png,.jpg,.jpeg,.tiff,.bmp,.txt"
            class="hidden"
            @change="handleFileUpload"
          />
        </label>
      </div>

      <!-- Error -->
      <p v-if="error" class="flex items-center gap-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-2.5">
        <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
        </svg>
        {{ error }}
      </p>

      <!-- Submit -->
      <button
        @click="submitJob"
        :disabled="isLoading"
        class="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white text-sm font-semibold py-3 rounded-lg transition-all duration-150"
      >
        <svg v-if="isLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
        </svg>
        {{ isLoading ? 'Finding matches…' : 'Find Matching Candidates' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useMatchingStore } from '../stores/matchingStore'

const store = useMatchingStore()
const emit = defineEmits(['job-submitted'])

const jobData = ref({ title: '', description: '', required_experience: 0 })
const selectedFile = ref(null)
const selectedFileName = ref('')
const isLoading = ref(false)
const error = ref('')

const handleFileUpload = (e) => {
  selectedFile.value = e.target.files[0]
  selectedFileName.value = selectedFile.value?.name || ''
}

const submitJob = async () => {
  error.value = ''
  if (!jobData.value.title.trim()) { error.value = 'Job title is required'; return }
  if (!selectedFile.value && !jobData.value.description.trim()) {
    error.value = 'Please provide a job description or upload a file'
    return
  }

  isLoading.value = true
  const form = new FormData()
  form.append('title', jobData.value.title)
  form.append('description', jobData.value.description)
  form.append('required_experience', jobData.value.required_experience)
  if (selectedFile.value) form.append('file', selectedFile.value)

  try {
    await store.matchJob(form)
    emit('job-submitted')
  } catch (err) {
    error.value = 'Failed: ' + (err.response?.data?.detail || err.message)
  } finally {
    isLoading.value = false
  }
}
</script>
