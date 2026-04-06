<template>
  <div class="max-w-2xl mx-auto">
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-semibold text-slate-900">Upload Resumes</h1>
      <p class="text-slate-500 mt-1 text-sm">Add candidate resumes to build your talent pool. Supports PDF, DOCX, Excel, PPTX, images and TXT.</p>
    </div>

    <!-- Drop Zone -->
    <div
      class="relative border-2 border-dashed rounded-xl p-10 text-center transition-all duration-200 cursor-pointer"
      :class="isDragging ? 'border-indigo-400 bg-indigo-50' : 'border-slate-300 bg-white hover:border-indigo-300 hover:bg-slate-50'"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="onDrop"
      @click="$refs.fileInput.click()"
    >
      <input
        ref="fileInput"
        type="file"
        multiple
        accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.png,.jpg,.jpeg,.tiff,.bmp,.txt"
        class="hidden"
        @change="uploadResumes"
      />
      <div class="flex flex-col items-center gap-3 pointer-events-none">
        <div class="w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center">
          <svg class="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
          </svg>
        </div>
        <div>
          <p class="font-medium text-slate-700">Drop files here or <span class="text-indigo-600">browse</span></p>
          <p class="text-xs text-slate-400 mt-1">PDF, DOCX, XLSX, PPTX, PNG, JPG, TXT</p>
        </div>
      </div>
    </div>

    <!-- Upload Queue -->
    <div v-if="queue.length" class="mt-6 space-y-2">
      <h2 class="text-sm font-medium text-slate-600 mb-3">Upload progress</h2>
      <div
        v-for="item in queue"
        :key="item.name"
        class="flex items-center gap-3 bg-white border border-slate-200 rounded-xl px-4 py-3"
      >
        <!-- File icon -->
        <div class="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center shrink-0">
          <svg class="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-slate-700 truncate">{{ item.name }}</p>
          <p class="text-xs mt-0.5" :class="{
            'text-slate-400': item.status === 'uploading',
            'text-emerald-600': item.status === 'done',
            'text-red-500': item.status === 'error'
          }">{{ item.message }}</p>
        </div>
        <!-- Status icon -->
        <div class="shrink-0">
          <svg v-if="item.status === 'done'" class="w-5 h-5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
          <svg v-else-if="item.status === 'error'" class="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
          <svg v-else class="w-5 h-5 text-slate-300 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Summary -->
    <div v-if="doneCount > 0" class="mt-4 flex items-center gap-2 text-sm text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-xl px-4 py-3">
      <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
      </svg>
      {{ doneCount }} resume{{ doneCount > 1 ? 's' : '' }} uploaded successfully
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import apiClient from '../../shared/api/client'

const fileInput = ref(null)
const isDragging = ref(false)
const queue = ref([])

const doneCount = computed(() => queue.value.filter(i => i.status === 'done').length)

const onDrop = (e) => {
  isDragging.value = false
  processFiles(e.dataTransfer.files)
}

const uploadResumes = (e) => processFiles(e.target.files)

const processFiles = async (files) => {
  if (!files.length) return
  for (const file of files) {
    const item = { name: file.name, status: 'uploading', message: 'Uploading...' }
    queue.value.push(item)
    try {
      const fd = new FormData()
      fd.append('file', file)
      await apiClient.post('/api/resumes/upload', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      item.status = 'done'
      item.message = 'Uploaded successfully'
    } catch (err) {
      item.status = 'error'
      item.message = err.response?.data?.detail || 'Upload failed'
    }
  }
}
</script>
