<template>
  <div class="max-w-3xl w-full mx-auto p-8 bg-white rounded-3xl shadow-2xl overflow-y-auto max-h-[90vh]">
    <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 mb-6 flex items-center gap-2">
      ← Back to Candidates
    </button>

    <!-- Header -->
    <div class="flex items-start justify-between mb-6">
      <div>
        <h2 class="text-2xl font-bold text-gray-800">{{ candidate.name }}</h2>
        <p class="text-blue-600 font-semibold text-lg">{{ matchScore }}% Match</p>
      </div>
      <a
        v-if="candidate.filename"
        :href="`http://localhost:8000/api/resumes/download/${candidate.id}`"
        target="_blank"
        class="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-blue-700 transition"
      >
        ⬇ Download Resume
      </a>
    </div>

    <!-- Contact Details -->
    <div class="bg-gray-50 rounded-2xl p-5 mb-6 space-y-2">
      <h3 class="font-semibold text-gray-700 mb-3">Contact Details</h3>
      <p class="text-sm text-gray-600">
        <span class="font-medium">Email:</span> {{ candidate.email || '—' }}
      </p>
      <p class="text-sm text-gray-600">
        <span class="font-medium">Phone:</span> {{ candidate.phone || '—' }}
      </p>
    </div>

    <!-- Skills -->
    <div class="mb-6">
      <h3 class="font-semibold text-gray-700 mb-3">Skills</h3>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="skill in skillList"
          :key="skill"
          class="bg-blue-100 text-blue-700 text-xs font-medium px-3 py-1 rounded-full"
        >
          {{ skill }}
        </span>
        <span v-if="skillList.length === 0" class="text-gray-400 text-sm">No skills extracted</span>
      </div>
    </div>

    <!-- AI Insights -->
    <div v-if="insights" class="space-y-6">
      <div>
        <h3 class="font-semibold text-lg mb-2 text-gray-700">Summary</h3>
        <p class="text-gray-600 leading-relaxed">{{ insights.summary || 'No summary available' }}</p>
      </div>

      <!-- Overlapping Skills -->
      <div v-if="insights.overlapping_skills && insights.overlapping_skills.length">
        <h3 class="font-semibold text-lg mb-2 text-emerald-700">✅ Matched Skills ({{ insights.overlapping_skills.length }})</h3>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="skill in insights.overlapping_skills"
            :key="skill"
            class="bg-emerald-100 text-emerald-700 text-xs font-medium px-3 py-1 rounded-full"
          >{{ skill }}</span>
        </div>
      </div>

      <div>
        <h3 class="font-semibold text-lg mb-2 text-emerald-700">💪 Strengths</h3>
        <ul class="list-disc pl-6 space-y-1 text-gray-600">
          <li v-for="(s, i) in insights.strengths" :key="i">{{ s }}</li>
        </ul>
      </div>

      <div>
        <h3 class="font-semibold text-lg mb-2 text-amber-700">⚠️ Areas of Improvement</h3>
        <ul class="list-disc pl-6 space-y-1 text-gray-600">
          <li v-for="(w, i) in insights.weaknesses" :key="i">{{ w }}</li>
        </ul>
      </div>

      <div>
        <h3 class="font-semibold text-lg mb-2 text-rose-700">🔍 Skill Gaps</h3>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="gap in insights.skill_gaps"
            :key="gap"
            class="bg-rose-100 text-rose-700 text-xs font-medium px-3 py-1 rounded-full"
          >{{ gap }}</span>
        </div>
      </div>

      <div class="bg-gray-50 p-5 rounded-2xl">
        <h3 class="font-semibold text-lg mb-2">Why this score?</h3>
        <p class="text-gray-600 leading-relaxed">{{ insights.match_reason || insights.explanation || 'No explanation available' }}</p>
      </div>
    </div>

    <div v-else-if="error" class="text-center py-10 text-red-500">{{ error }}</div>
    <div v-else class="text-center py-10 text-gray-400">Loading AI insights...</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useMatchingStore } from '../stores/matchingStore'

const props = defineProps({
  candidate: { type: Object, required: true },
  matchScore: { type: Number, required: true }
})

defineEmits(['close'])

const store = useMatchingStore()
const insights = ref(null)
const error = ref(null)

const skillList = computed(() =>
  props.candidate.skills
    ? props.candidate.skills.split(',').map(s => s.trim()).filter(Boolean)
    : []
)

onMounted(async () => {
  try {
    const form = new FormData()
    form.append('job_description', store.lastJobDescription || '')
    form.append('candidate_id', props.candidate.id)
    form.append('score', props.matchScore)
    const response = await axios.post(
      'http://localhost:8000/api/matching/insights',
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    insights.value = response.data.insights
  } catch (e) {
    error.value = 'Failed to load insights: ' + (e.response?.data?.detail || e.message)
  }
})
</script>
