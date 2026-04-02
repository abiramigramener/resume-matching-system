<template>
  <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[88vh] flex flex-col overflow-hidden">

    <!-- Modal Header -->
    <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 shrink-0">
      <div class="flex items-center gap-3 min-w-0">
        <div class="w-9 h-9 rounded-lg bg-indigo-100 flex items-center justify-center shrink-0">
          <svg class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
          </svg>
        </div>
        <div class="min-w-0">
          <h2 class="font-semibold text-slate-900 text-[15px] truncate">{{ candidate.name }}</h2>
          <p class="text-xs text-slate-400 truncate">{{ candidate.email }}</p>
        </div>
      </div>
      <div class="flex items-center gap-3 shrink-0">
        <!-- Score pill -->
        <span
          class="text-sm font-bold px-3 py-1 rounded-full"
          :class="matchScore >= 70 ? 'bg-emerald-100 text-emerald-700' : matchScore >= 45 ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'"
        >{{ matchScore }}% match</span>
        <!-- Download -->
        <a
          v-if="candidate.filename"
          :href="`http://localhost:8000/api/resumes/download/${candidate.id}`"
          target="_blank"
          class="flex items-center gap-1.5 text-xs font-medium text-slate-600 hover:text-indigo-600 bg-slate-100 hover:bg-indigo-50 px-3 py-1.5 rounded-lg transition"
          title="Download resume"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
          </svg>
          Resume
        </a>
        <!-- Close -->
        <button
          @click="$emit('close')"
          class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition"
          aria-label="Close"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Scrollable Body -->
    <div class="overflow-y-auto flex-1 px-6 py-5 space-y-6">

      <!-- Contact + Skills row -->
      <div class="grid grid-cols-2 gap-4">
        <div class="bg-slate-50 rounded-xl p-4">
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Contact</p>
          <div class="space-y-2">
            <div class="flex items-center gap-2 text-sm text-slate-700">
              <svg class="w-3.5 h-3.5 text-slate-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
              </svg>
              <span class="truncate">{{ candidate.email || '—' }}</span>
            </div>
            <div class="flex items-center gap-2 text-sm text-slate-700">
              <svg class="w-3.5 h-3.5 text-slate-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 002.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 01-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 00-1.091-.852H4.5A2.25 2.25 0 002.25 4.5v2.25z" />
              </svg>
              <span>{{ candidate.phone || '—' }}</span>
            </div>
          </div>
        </div>

        <div class="bg-slate-50 rounded-xl p-4">
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Skills ({{ skillList.length }})</p>
          <div class="flex flex-wrap gap-1.5">
            <span
              v-for="skill in skillList"
              :key="skill"
              class="text-xs bg-white border border-slate-200 text-slate-600 px-2 py-0.5 rounded-md font-medium"
            >{{ skill }}</span>
            <span v-if="!skillList.length" class="text-xs text-slate-400">None extracted</span>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="!insights && !error" class="flex flex-col items-center justify-center py-12 gap-3">
        <svg class="w-6 h-6 text-indigo-400 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
        </svg>
        <p class="text-sm text-slate-400">Generating AI insights…</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-600">{{ error }}</div>

      <!-- Insights -->
      <template v-else-if="insights">

        <!-- Summary -->
        <div class="bg-indigo-50 border border-indigo-100 rounded-xl p-4">
          <p class="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-2">Summary</p>
          <p class="text-sm text-slate-700 leading-relaxed">{{ insights.summary }}</p>
        </div>

        <!-- Matched Skills -->
        <div v-if="insights.overlapping_skills?.length">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Matched Skills</span>
            <span class="text-xs bg-emerald-100 text-emerald-700 font-semibold px-2 py-0.5 rounded-full">{{ insights.overlapping_skills.length }}</span>
          </div>
          <div class="flex flex-wrap gap-1.5">
            <span
              v-for="skill in insights.overlapping_skills"
              :key="skill"
              class="text-xs bg-emerald-50 border border-emerald-200 text-emerald-700 px-2.5 py-1 rounded-lg font-medium"
            >✓ {{ skill }}</span>
          </div>
        </div>

        <!-- Two-col: Strengths + Gaps -->
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-slate-50 rounded-xl p-4">
            <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Strengths</p>
            <ul class="space-y-2">
              <li v-for="(s, i) in insights.strengths" :key="i" class="flex items-start gap-2 text-sm text-slate-700">
                <span class="text-emerald-500 mt-0.5 shrink-0">✓</span>{{ s }}
              </li>
            </ul>
          </div>
          <div class="bg-slate-50 rounded-xl p-4">
            <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Skill Gaps</p>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="gap in insights.skill_gaps"
                :key="gap"
                class="text-xs bg-red-50 border border-red-200 text-red-600 px-2.5 py-1 rounded-lg font-medium"
              >{{ gap }}</span>
              <span v-if="!insights.skill_gaps?.length" class="text-xs text-slate-400">None identified</span>
            </div>
          </div>
        </div>

        <!-- Weaknesses -->
        <div v-if="insights.weaknesses?.length">
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Areas to Improve</p>
          <ul class="space-y-1.5">
            <li v-for="(w, i) in insights.weaknesses" :key="i" class="flex items-start gap-2 text-sm text-slate-600">
              <span class="text-amber-400 mt-0.5 shrink-0">⚠</span>{{ w }}
            </li>
          </ul>
        </div>

        <!-- Score explanation -->
        <div class="border-t border-slate-100 pt-4">
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Why this score?</p>
          <p class="text-sm text-slate-600 leading-relaxed">{{ insights.match_reason || insights.explanation }}</p>
        </div>

      </template>
    </div>
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
  (props.candidate.skills || '').split(',').map(s => s.trim()).filter(Boolean)
)

onMounted(async () => {
  try {
    const form = new FormData()
    form.append('job_description', store.lastJobDescription || '')
    form.append('candidate_id', props.candidate.id)
    form.append('score', props.matchScore)
    const res = await axios.post('http://localhost:8000/api/matching/insights', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    insights.value = res.data.insights
  } catch (e) {
    error.value = e.response?.data?.detail || e.message
  }
})
</script>
