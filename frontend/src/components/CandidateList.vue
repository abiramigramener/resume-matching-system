<template>
  <div class="max-w-4xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900">Matched Candidates</h1>
        <p class="text-slate-500 text-sm mt-1">{{ matches.length }} candidate{{ matches.length !== 1 ? 's' : '' }} ranked by relevance</p>
      </div>
      <button
        @click="$emit('back')"
        class="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 transition"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
        </svg>
        Back
      </button>
    </div>

    <!-- Empty state -->
    <div v-if="matches.length === 0" class="bg-white border border-slate-200 rounded-xl p-16 text-center">
      <div class="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center mx-auto mb-4">
        <svg class="w-6 h-6 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
        </svg>
      </div>
      <p class="font-medium text-slate-700">No candidates found</p>
      <p class="text-sm text-slate-400 mt-1">Try uploading more resumes or adjusting the job description.</p>
    </div>

    <!-- Candidate Cards -->
    <div class="space-y-3">
      <div
        v-for="(match, index) in matches"
        :key="match.candidate.id"
        class="bg-white border border-slate-200 rounded-xl p-5 flex items-center gap-5 hover:border-indigo-200 hover:shadow-sm transition-all duration-150 group"
      >
        <!-- Rank badge -->
        <div
          class="w-9 h-9 rounded-lg flex items-center justify-center text-sm font-bold shrink-0"
          :class="index === 0 ? 'bg-amber-100 text-amber-700' : index === 1 ? 'bg-slate-100 text-slate-600' : index === 2 ? 'bg-orange-100 text-orange-600' : 'bg-slate-100 text-slate-500'"
        >
          {{ index + 1 }}
        </div>

        <!-- Info -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <h3 class="font-semibold text-slate-900 text-[15px]">{{ match.candidate.name }}</h3>
          </div>
          <p class="text-sm text-slate-400 mt-0.5 truncate">{{ match.candidate.email }}</p>
          <!-- Skill chips (top 4) -->
          <div v-if="topSkills(match).length" class="flex flex-wrap gap-1.5 mt-2">
            <span
              v-for="skill in topSkills(match)"
              :key="skill"
              class="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md font-medium"
            >{{ skill }}</span>
            <span v-if="skillCount(match) > 4" class="text-xs text-slate-400 px-1 py-0.5">+{{ skillCount(match) - 4 }} more</span>
          </div>
        </div>

        <!-- Score -->
        <div class="text-right shrink-0">
          <div
            class="text-2xl font-bold tabular-nums"
            :class="match.score >= 70 ? 'text-emerald-600' : match.score >= 45 ? 'text-amber-600' : 'text-slate-500'"
          >{{ match.score }}<span class="text-sm font-medium">%</span></div>
          <div class="w-20 h-1.5 bg-slate-100 rounded-full mt-1.5 overflow-hidden">
            <div
              class="h-full rounded-full transition-all"
              :class="match.score >= 70 ? 'bg-emerald-500' : match.score >= 45 ? 'bg-amber-400' : 'bg-slate-400'"
              :style="{ width: match.score + '%' }"
            ></div>
          </div>
          <p class="text-xs text-slate-400 mt-1">match score</p>
        </div>

        <!-- Action -->
        <button
          @click="$emit('show-insight', match)"
          class="shrink-0 flex items-center gap-1.5 text-sm font-medium text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-4 py-2 rounded-lg transition-all duration-150"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
          Insights
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ matches: { type: Array, required: true } })
defineEmits(['show-insight', 'back'])

const topSkills = (match) =>
  (match.candidate.skills || '').split(',').map(s => s.trim()).filter(Boolean).slice(0, 4)

const skillCount = (match) =>
  (match.candidate.skills || '').split(',').filter(s => s.trim()).length
</script>
