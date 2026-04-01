<template>
  <div class="max-w-3xl mx-auto p-8 bg-white rounded-3xl shadow-2xl">
    <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 mb-6 flex items-center gap-2">
      ← Back to Candidates
    </button>

    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-2xl font-bold">{{ candidate.name }}</h2>
        <p class="text-blue-600 font-medium">{{ matchScore }}% Match</p>
      </div>
    </div>

    <div v-if="insights" class="space-y-8">
      <!-- Summary -->
      <div>
        <h3 class="font-semibold text-lg mb-3 text-gray-700">Summary</h3>
        <p class="text-gray-600 leading-relaxed">{{ insights.summary || 'No summary available' }}</p>
      </div>

      <!-- Strengths -->
      <div>
        <h3 class="font-semibold text-lg mb-3 text-emerald-700">✅ Strengths</h3>
        <ul class="list-disc pl-6 space-y-2 text-gray-600">
          <li v-for="(strength, i) in insights.strengths" :key="i">{{ strength }}</li>
        </ul>
      </div>

      <!-- Weaknesses -->
      <div>
        <h3 class="font-semibold text-lg mb-3 text-amber-700">⚠️ Areas of Improvement</h3>
        <ul class="list-disc pl-6 space-y-2 text-gray-600">
          <li v-for="(weakness, i) in insights.weaknesses" :key="i">{{ weakness }}</li>
        </ul>
      </div>

      <!-- Skill Gaps -->
      <div>
        <h3 class="font-semibold text-lg mb-3 text-rose-700">🔍 Skill Gaps</h3>
        <ul class="list-disc pl-6 space-y-2 text-gray-600">
          <li v-for="(gap, i) in insights.skill_gaps" :key="i">{{ gap }}</li>
        </ul>
      </div>

      <!-- Explanation -->
      <div class="bg-gray-50 p-6 rounded-2xl">
        <h3 class="font-semibold text-lg mb-3">Why this score?</h3>
        <p class="text-gray-600 leading-relaxed">{{ insights.explanation || 'No explanation available' }}</p>
      </div>
    </div>

    <div v-else class="text-center py-12 text-gray-500">
      Loading AI insights...
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  candidate: { type: Object, required: true },
  insights: { type: Object, default: null },
  matchScore: { type: Number, required: true }
})

const emit = defineEmits(['close'])
</script>