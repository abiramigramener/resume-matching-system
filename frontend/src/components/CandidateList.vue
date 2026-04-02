<template>
  <div class="max-w-6xl mx-auto p-6">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold text-gray-800">Matched Candidates</h1>
      <button @click="$emit('back')" class="text-blue-600 hover:text-blue-700 font-medium">
        ← Back to Job Input
      </button>
    </div>

    <div v-if="matches.length === 0" class="text-center py-20 text-gray-500">
      No candidates found. Try uploading more resumes.
    </div>

    <div class="grid gap-6">
      <div
        v-for="(match, index) in matches"
        :key="match.candidate.id"
        class="bg-white rounded-2xl shadow border border-gray-100 overflow-hidden"
      >
        <div class="p-6 flex items-start justify-between">
          <div>
            <h3 class="text-xl font-semibold">{{ match.candidate.name }}</h3>
            <p class="text-gray-500 text-sm">{{ match.candidate.email }}</p>
          </div>
          <div class="text-right">
            <div class="text-4xl font-bold text-blue-600">{{ match.score }}<span class="text-lg">%</span></div>
            <p class="text-xs text-gray-400">Match Score</p>
          </div>
        </div>

        <div class="bg-gray-50 px-6 py-4 border-t">
          <button
            @click="showInsights(match)"
            class="w-full bg-white border border-gray-300 hover:border-blue-500 py-3 rounded-xl font-medium transition"
          >
            View AI Insights
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  matches: { type: Array, required: true }
})

const emit = defineEmits(['show-insight', 'back'])

const showInsights = (match) => {
  emit('show-insight', match)
}
</script>