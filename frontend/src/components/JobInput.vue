<template>
  <div class="max-w-3xl mx-auto p-8 bg-white rounded-3xl shadow-lg">
    <h1 class="text-3xl font-bold text-gray-800 mb-8 text-center">Enter Job Description</h1>

    <div class="space-y-8">
      <!-- Job Title -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Job Title *</label>
        <input
          v-model="jobData.title"
          type="text"
          placeholder="e.g. Senior Backend Engineer"
          class="w-full px-5 py-3 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <!-- Required Experience -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Required Experience (years)</label>
        <input
          v-model.number="jobData.required_experience"
          type="number"
          min="0"
          class="w-full px-5 py-3 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <!-- Text JD -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Job Description (Text or Bullets)</label>
        <textarea
          v-model="jobData.description"
          rows="8"
          placeholder="Paste job requirements here..."
          class="w-full px-5 py-3 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500"
        ></textarea>
      </div>

      <!-- File Upload -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">OR Upload JD File (Any Format)</label>
        <input
          type="file"
          accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.png,.jpg,.jpeg,.tiff,.bmp,.txt"
          @change="handleFileUpload"
          class="block w-full text-sm text-gray-500 file:mr-4 file:py-4 file:px-8 file:rounded-2xl file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700"
        />
        <p v-if="selectedFileName" class="mt-3 text-green-600 text-sm">
          Selected: {{ selectedFileName }}
        </p>
      </div>

      <button
        @click="submitJob"
        :disabled="isLoading"
        class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-4 rounded-2xl text-lg"
      >
        {{ isLoading ? 'Processing...' : 'Find Matching Candidates' }}
      </button>
    </div>

    <p v-if="status" class="mt-6 text-center p-4 rounded-2xl" 
       :class="status.includes('✅') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ status }}
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useMatchingStore } from '../stores/matchingStore'

const store = useMatchingStore()
const emit = defineEmits(['job-submitted'])

const jobData = ref({
  title: '',
  description: '',
  required_experience: 0
})

const selectedFile = ref(null)
const selectedFileName = ref('')
const isLoading = ref(false)
const status = ref('')

const handleFileUpload = (e) => {
  selectedFile.value = e.target.files[0]
  selectedFileName.value = selectedFile.value ? selectedFile.value.name : ''
}

const submitJob = async () => {
  if (!jobData.value.title.trim()) {
    status.value = '❌ Job title is required'
    return
  }

  isLoading.value = true
  status.value = ''

  const form = new FormData()
  form.append('title', jobData.value.title)
  form.append('description', jobData.value.description)
  form.append('required_experience', jobData.value.required_experience)

  if (selectedFile.value) {
    form.append('file', selectedFile.value)
  }

  if (!selectedFile.value && !jobData.value.description.trim()) {
    status.value = '❌ Please provide a job description or upload a file'
    isLoading.value = false
    return
  }

  try {
    await store.matchJob(form)
    emit('job-submitted')
  } catch (err) {
    status.value = '❌ Failed to process job: ' + (err.response?.data?.detail || err.message)
  } finally {
    isLoading.value = false
  }
}
</script>