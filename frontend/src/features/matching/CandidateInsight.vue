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
        <span
          class="text-sm font-bold px-3 py-1 rounded-full"
          :class="matchScore >= 70 ? 'bg-emerald-100 text-emerald-700' : matchScore >= 45 ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'"
        >{{ matchScore }}% match</span>
        <a
          v-if="candidate.filename"
          :href="`http://localhost:8000/api/resumes/download/${candidate.id}`"
          target="_blank"
          class="flex items-center gap-1.5 text-xs font-medium text-slate-600 hover:text-indigo-600 bg-slate-100 hover:bg-indigo-50 px-3 py-1.5 rounded-lg transition"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
          </svg>
          Resume
        </a>
        <button @click="$emit('close')" class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition" aria-label="Close">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Scrollable Body -->
    <div class="overflow-y-auto flex-1 px-6 py-5 space-y-6">

      <!-- Contact + Profile -->
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
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Profile</p>
          <div class="space-y-1.5 text-sm text-slate-700">
            <p v-if="candidate.job_title"><span class="text-slate-400 text-xs">Role</span><br>{{ candidate.job_title }}</p>
            <p v-if="candidate.experience_years"><span class="text-slate-400 text-xs">Experience</span><br>{{ candidate.experience_years }} yr{{ candidate.experience_years !== 1 ? 's' : '' }}</p>
            <!-- Education: show structured if available -->
            <div v-if="educationList.length">
              <span class="text-slate-400 text-xs">Education</span>
              <div v-for="(edu, i) in educationList" :key="i" class="mt-0.5">
                <span class="font-medium">{{ edu.degree }}</span>
                <span v-if="edu.field" class="text-slate-500"> · {{ edu.field }}</span>
                <span v-if="edu.year" class="text-slate-400 text-xs"> ({{ edu.year }})</span>
                <div v-if="edu.institution" class="text-xs text-slate-400">{{ edu.institution }}</div>
              </div>
            </div>
            <p v-else-if="candidate.education"><span class="text-slate-400 text-xs">Education</span><br>{{ candidate.education }}</p>
          </div>
        </div>
      </div>

      <!-- ── Skills Section ─────────────────────────────────────────────── -->
      <div class="bg-slate-50 rounded-xl p-4">
        <div class="flex items-center justify-between mb-3">
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Skills ({{ editableSkills.length }})
          </p>
          <div class="flex items-center gap-2">
            <span v-if="skillSaveStatus" class="text-xs" :class="skillSaveStatus === 'Saved' ? 'text-emerald-600' : 'text-red-500'">
              {{ skillSaveStatus }}
            </span>
            <button
              v-if="!editingSkills"
              @click="startEditing"
              class="flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-2.5 py-1 rounded-lg transition"
            >
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931z" />
              </svg>
              Edit
            </button>
            <template v-else>
              <button @click="saveSkills" :disabled="skillSaving" class="text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 px-3 py-1 rounded-lg transition">
                {{ skillSaving ? 'Saving…' : 'Save' }}
              </button>
              <button @click="cancelEditing" class="text-xs font-medium text-slate-500 hover:text-slate-700 px-2 py-1 rounded-lg transition">
                Cancel
              </button>
            </template>
          </div>
        </div>

        <!-- View mode -->
        <div v-if="!editingSkills" class="flex flex-wrap gap-2">
          <span
            v-for="skill in editableSkills"
            :key="skill.name"
            class="inline-flex items-center gap-1.5 text-xs bg-white border border-slate-200 text-slate-700 px-2.5 py-1 rounded-lg font-medium"
          >
            {{ skill.name }}
            <span v-if="skill.years > 0" class="text-slate-400 font-normal">· {{ skill.years }} yr{{ skill.years !== 1 ? 's' : '' }}</span>
          </span>
          <span v-if="!editableSkills.length" class="text-xs text-slate-400">None extracted</span>
        </div>

        <!-- Edit mode -->
        <div v-else class="space-y-2">
          <div
            v-for="(skill, idx) in editableSkills"
            :key="idx"
            class="flex items-center gap-2"
          >
            <input
              v-model="skill.name"
              placeholder="Skill name"
              class="flex-1 text-sm px-3 py-1.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
            <div class="flex items-center gap-1 shrink-0">
              <input
                v-model.number="skill.years"
                type="number"
                min="0"
                max="50"
                step="0.5"
                placeholder="Yrs"
                class="w-16 text-sm px-2 py-1.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400 text-center"
              />
              <span class="text-xs text-slate-400">yrs</span>
            </div>
            <button @click="removeSkill(idx)" class="w-6 h-6 flex items-center justify-center text-slate-400 hover:text-red-500 transition shrink-0" title="Remove">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Add new skill row -->
          <div class="flex items-center gap-2 pt-1 border-t border-slate-200">
            <input
              v-model="newSkillName"
              placeholder="Add skill…"
              @keyup.enter="addSkill"
              class="flex-1 text-sm px-3 py-1.5 border border-dashed border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400 bg-white"
            />
            <input
              v-model.number="newSkillYears"
              type="number"
              min="0"
              max="50"
              step="0.5"
              placeholder="Yrs"
              class="w-16 text-sm px-2 py-1.5 border border-dashed border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400 text-center bg-white"
            />
            <span class="text-xs text-slate-400">yrs</span>
            <button @click="addSkill" class="w-6 h-6 flex items-center justify-center text-indigo-500 hover:text-indigo-700 transition shrink-0" title="Add">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Loading insights -->
      <div v-if="!insights && !error" class="flex flex-col items-center justify-center py-12 gap-3">
        <svg class="w-6 h-6 text-indigo-400 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
        </svg>
        <p class="text-sm text-slate-400">Generating AI insights…</p>
      </div>

      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-600">{{ error }}</div>

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
            <span v-for="skill in insights.overlapping_skills" :key="skill" class="text-xs bg-emerald-50 border border-emerald-200 text-emerald-700 px-2.5 py-1 rounded-lg font-medium">✓ {{ skill }}</span>
          </div>
        </div>

        <!-- Strengths + Gaps -->
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
              <span v-for="gap in insights.skill_gaps" :key="gap" class="text-xs bg-red-50 border border-red-200 text-red-600 px-2.5 py-1 rounded-lg font-medium">{{ gap }}</span>
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
import { ref, onMounted } from 'vue'
import axios from 'axios'
import apiClient from '../../shared/api/client'
import { useMatchingStore } from './matchingStore'

const props = defineProps({
  candidate: { type: Object, required: true },
  matchScore: { type: Number, required: true }
})
defineEmits(['close'])

const store = useMatchingStore()
const insights = ref(null)
const error = ref(null)

// ── Skill editing state ───────────────────────────────────────────────────────
const editableSkills = ref([])
const editingSkills = ref(false)
const skillSaving = ref(false)
const skillSaveStatus = ref('')
const newSkillName = ref('')
const newSkillYears = ref(0)
let skillsSnapshot = []

// ── Education state ───────────────────────────────────────────────────────────
const educationList = ref([])

async function loadSkills() {
  try {
    const res = await apiClient.get(`/api/resumes/${props.candidate.id}/skills`)
    editableSkills.value = res.data.skills.map(s => ({ name: s.name, years: s.years ?? 0 }))
  } catch {
    // Fallback: build from flat skills string
    editableSkills.value = (props.candidate.skills || '')
      .split(',').map(s => s.trim()).filter(Boolean)
      .map(name => ({ name, years: 0 }))
  }
}

function startEditing() {
  skillsSnapshot = editableSkills.value.map(s => ({ ...s }))
  editingSkills.value = true
  skillSaveStatus.value = ''
}

function cancelEditing() {
  editableSkills.value = skillsSnapshot.map(s => ({ ...s }))
  editingSkills.value = false
  newSkillName.value = ''
  newSkillYears.value = 0
}

function addSkill() {
  const name = newSkillName.value.trim()
  if (!name) return
  if (!editableSkills.value.find(s => s.name.toLowerCase() === name.toLowerCase())) {
    editableSkills.value.push({ name, years: newSkillYears.value || 0 })
  }
  newSkillName.value = ''
  newSkillYears.value = 0
}

function removeSkill(idx) {
  editableSkills.value.splice(idx, 1)
}

async function saveSkills() {
  skillSaving.value = true
  skillSaveStatus.value = ''
  try {
    await apiClient.put(`/api/resumes/${props.candidate.id}/skills`, {
      skills: editableSkills.value.filter(s => s.name.trim())
    })
    editingSkills.value = false
    skillSaveStatus.value = 'Saved'
    setTimeout(() => { skillSaveStatus.value = '' }, 2500)
  } catch (e) {
    skillSaveStatus.value = 'Save failed'
  } finally {
    skillSaving.value = false
  }
}

onMounted(async () => {
  // Load skills, education, and insights in parallel
  const [, , insightsRes] = await Promise.allSettled([
    loadSkills(),
    loadEducation(),
    axios.post('http://localhost:8000/api/matching/insights',
      (() => { const f = new FormData(); f.append('job_description', store.lastJobDescription || ''); f.append('candidate_id', props.candidate.id); f.append('score', props.matchScore); return f })(),
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
  ])
  if (insightsRes.status === 'fulfilled') {
    insights.value = insightsRes.value.data.insights
  } else {
    error.value = insightsRes.reason?.response?.data?.detail || insightsRes.reason?.message
  }
})

async function loadEducation() {
  try {
    const res = await apiClient.get(`/api/resumes/${props.candidate.id}/education`)
    educationList.value = res.data.education || []
  } catch {
    educationList.value = []
  }
}
</script>
