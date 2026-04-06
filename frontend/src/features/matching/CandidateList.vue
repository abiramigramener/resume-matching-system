<template>
  <div class="max-w-4xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900">Matched Candidates</h1>
        <p class="text-slate-500 text-sm mt-1">
          {{ matches.length }} candidate{{ matches.length !== 1 ? 's' : '' }} ranked by relevance
        </p>
      </div>
      <button @click="$emit('back')" class="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 transition">
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
        class="bg-white border border-slate-200 rounded-xl p-5 hover:border-indigo-200 hover:shadow-sm transition-all duration-150"
      >
        <div class="flex items-start gap-5">
          <!-- Rank badge -->
          <div
            class="w-9 h-9 rounded-lg flex items-center justify-center text-sm font-bold shrink-0 mt-0.5"
            :class="index === 0 ? 'bg-amber-100 text-amber-700' : index === 1 ? 'bg-slate-100 text-slate-600' : index === 2 ? 'bg-orange-100 text-orange-600' : 'bg-slate-100 text-slate-500'"
          >{{ index + 1 }}</div>

          <!-- Info -->
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-slate-900 text-[15px]">{{ match.candidate.name }}</h3>
            <p class="text-sm text-slate-400 mt-0.5 truncate">{{ match.candidate.email }}</p>

            <!-- Skills row -->
            <div class="flex flex-wrap items-center gap-1.5 mt-2.5">

              <!-- Matched skills (max 4 visible) -->
              <template v-if="matchedSkills(match).length">
                <span
                  v-for="skill in matchedSkills(match).slice(0, 4)"
                  :key="'m-' + skill"
                  class="text-xs bg-emerald-50 border border-emerald-200 text-emerald-700 px-2 py-0.5 rounded-md font-medium"
                >✓ {{ skill }}</span>

                <!-- +N more matched — tooltip on hover -->
                <span
                  v-if="matchedSkills(match).length > 4"
                  class="tooltip-trigger text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-md font-semibold cursor-default"
                >
                  +{{ matchedSkills(match).length - 4 }} more
                  <span class="tooltip">{{ matchedSkills(match).slice(4).join(', ') }}</span>
                </span>
              </template>

              <!-- Unmatched skills — only in tooltip, never shown directly -->
              <span
                v-if="unmatchedSkills(match).length"
                class="tooltip-trigger text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded-md font-medium cursor-default"
              >
                {{ unmatchedSkills(match).length }} unmatched
                <span class="tooltip tooltip-slate">{{ unmatchedSkills(match).join(', ') }}</span>
              </span>

              <!-- No skills at all -->
              <span v-if="!matchedSkills(match).length && !unmatchedSkills(match).length" class="text-xs text-slate-400">
                No skills extracted
              </span>
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
            <p v-if="match.score_breakdown" class="text-[10px] text-slate-400 mt-1">
              Skills <span class="font-semibold text-slate-600">{{ match.score_breakdown.skills }}%</span>
              · Title <span class="font-semibold text-slate-600">{{ match.score_breakdown.title }}%</span>
            </p>
          </div>

          <!-- Insights button -->
          <button
            @click="$emit('show-insight', match)"
            class="shrink-0 flex items-center gap-1.5 text-sm font-medium text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-4 py-2 rounded-lg transition-all duration-150 self-start"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
            </svg>
            Insights
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ matches: { type: Array, required: true } })
defineEmits(['show-insight', 'back'])

const matchedSkills = (match) => match.candidate.matched_skills || []
const unmatchedSkills = (match) => match.candidate.unmatched_skills || []
</script>

<style scoped>
/* Tooltip container */
.tooltip-trigger {
  position: relative;
}

.tooltip-trigger:hover .tooltip {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

/* Tooltip bubble */
.tooltip {
  position: absolute;
  bottom: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%) translateY(4px);
  background: #1e293b;
  color: #f1f5f9;
  font-size: 11px;
  font-weight: 500;
  padding: 6px 10px;
  border-radius: 8px;
  white-space: nowrap;
  max-width: 280px;
  white-space: normal;
  text-align: center;
  line-height: 1.5;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.15s ease, transform 0.15s ease;
  z-index: 50;
  pointer-events: none;
}

/* Arrow */
.tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: #1e293b;
}

/* Slate variant for unmatched */
.tooltip-slate {
  background: #475569;
}
.tooltip-slate::after {
  border-top-color: #475569;
}
</style>
