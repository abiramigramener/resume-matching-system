<template>
  <div class="max-w-2xl mx-auto p-8 bg-white rounded-3xl shadow-lg">
    <h1 class="text-3xl font-bold mb-8 text-center">Upload Resumes</h1>
    <p class="text-gray-500 text-center mb-8">Supports PDF, DOCX, Excel, PPTX, Images, TXT</p>

    <input
      type="file"
      multiple
      accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.png,.jpg,.jpeg,.tiff,.bmp,.txt"
      @change="uploadResumes"
      class="block w-full text-sm text-gray-500 file:mr-4 file:py-4 file:px-8 file:rounded-2xl file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer"
    />

    <div v-if="uploadStatus" class="mt-6 p-4 bg-green-50 rounded-2xl text-green-700">
      {{ uploadStatus }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const uploadStatus = ref('')

const uploadResumes = async (e) => {
  const files = e.target.files
  if (!files.length) return

  uploadStatus.value = 'Uploading...'

  for (let file of files) {
    const formData = new FormData()
    formData.append('file', file)

    try {
      await axios.post('http://localhost:8000/api/resumes/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      uploadStatus.value = `✅ ${file.name} uploaded successfully`
    } catch (err) {
      uploadStatus.value = `❌ Failed to upload ${file.name}`
      console.error(err)
    }
  }
}
</script>