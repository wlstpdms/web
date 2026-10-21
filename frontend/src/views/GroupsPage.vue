<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { learningApi } from '../api/index.js'

const groups = ref([
  { id: 'lunch-club', name: '점심 영어 한 입', topic: '일상 회화', members: 6, activity: '오늘의 질문에 4명이 답했어요', color: 'mint', mark: '☀', joined: true },
  { id: 'weekend-talk', name: '주말엔 뭐 했어?', topic: '초급 말하기', members: 12, activity: '새로운 질문이 올라왔어요', color: 'blue', mark: '✳', joined: false },
  { id: 'word-garden', name: '하루 한 단어 정원', topic: '단어와 표현', members: 8, activity: '어제 새 표현 11개를 나눴어요', color: 'yellow', mark: '❋', joined: false },
])
const loading = ref(false)
const showCreate = ref(false)
const showJoinCode = ref(false)
const groupName = ref('')
const joinCode = ref('')
const note = ref('')

onMounted(async () => {
  loading.value = true
  try {
    const data = await learningApi.groups()
    const rows = Array.isArray(data) ? data : data?.items || data?.groups
    if (rows?.length) groups.value = rows.map((group, i) => ({ color: ['mint', 'blue', 'yellow'][i % 3], mark: ['☀', '✳', '❋'][i % 3], joined: false, ...group, members: group.member_count ?? group.members ?? 0 }))
  } catch { note.value = '체험용 모임을 보여드리고 있어요. 로그인 후 참여 정보를 저장할 수 있어요.' }
  finally { loading.value = false }
})

async function joinByCode() {
  const code = joinCode.value.trim()
  if (!code) return
  try {
    const joined = await learningApi.joinGroup(code)
    groups.value.unshift({ color: 'mint', mark: '✳', topic: '초대받은 모임', activity: '초대 코드로 참여했어요', joined: true, members: joined.member_count ?? 1, ...joined })
    note.value = `${joined.name} 모임에 참여했어요.`
  } catch {
    note.value = '모임 코드가 올바른지 확인하고 로그인 상태를 확인해 주세요.'
  }
  joinCode.value = ''
  showJoinCode.value = false
}
function join(group) { group.joined = !group.joined; note.value = group.joined ? `${group.name} 모임에 참여했어요. 체험 화면에서만 표시돼요.` : `${group.name} 모임 참여를 취소했어요.` }
async function createGroup() {
  const name = groupName.value.trim()
  if (!name) return
  try {
    const created = await learningApi.createGroup(name)
    groups.value.unshift({ color: 'mint', mark: '✳', members: 1, topic: '내가 만든 모임', activity: '첫 질문을 올려보세요', joined: true, ...created, name: created?.name || name })
    note.value = '모임을 만들었어요. 체험용으로 보여드려요.'
  } catch {
    groups.value.unshift({ id: `local-${Date.now()}`, name, topic: '내가 만든 모임', members: 1, activity: '첫 질문을 올려보세요', color: 'mint', mark: '✳', joined: true })
    note.value = '모임을 체험 화면에 추가했어요. 로그인 후 저장됩니다.'
  }
  groupName.value = ''; showCreate.value = false
}
</script>

<template>
  <section class="groups-page">
    <div class="groups-intro"><div><p class="panel-label">A LITTLE ENGLISH, TOGETHER</p><h1>오늘 한 문장,<br /><em>함께 나눠요.</em></h1><p>부담 없이 한마디. 서로의 작은 연습이 계속하게 해줘요.</p></div><div class="conversation-art" aria-hidden="true"><div class="bubble bubble-a">How was<br />your day?</div><div class="bubble bubble-b">Pretty good!<br />And yours?</div><span>✳</span></div></div>
    <div class="groups-toolbar"><div><h2>지금 열려 있는 모임</h2><p>관심 있는 모임에 들어가 오늘의 질문에 답해보세요.</p></div><div class="group-actions"><button class="outline-button" type="button" @click="showJoinCode = !showJoinCode">초대 코드 입력</button><button class="outline-button" type="button" @click="showCreate = !showCreate">＋ 모임 만들기</button></div></div>
    <form v-if="showCreate" class="create-group-form" @submit.prevent="createGroup"><label for="group-name">모임 이름</label><input id="group-name" v-model="groupName" maxlength="30" placeholder="예: 퇴근길 5분 영어" required /><button class="start-button" type="submit">모임 만들기 <span>→</span></button></form>
    <form v-if="showJoinCode" class="create-group-form" @submit.prevent="joinByCode"><label for="join-code">초대 코드</label><input id="join-code" v-model="joinCode" maxlength="16" placeholder="친구에게 받은 코드를 입력해요" required /><button class="start-button" type="submit">모임 참여하기 <span>→</span></button></form>
    <p v-if="note" class="notice-line" role="status">{{ note }}</p>
    <div class="group-list">
      <article v-for="(group, index) in groups" :key="group.id" class="group-row">
        <div class="group-index">{{ String(index + 1).padStart(2, '0') }}</div><div class="group-emblem" :class="group.color">{{ group.mark }}</div><div class="group-details"><div class="group-title-line"><h3>{{ group.name }}</h3><span class="topic-tag">{{ group.topic }}</span></div><p><span class="member-count">◎ {{ group.members }}명</span><span class="activity-dot">{{ group.activity }}</span></p><small v-if="group.join_code" class="invite-code">초대 코드 {{ group.join_code }}</small></div><button class="join-button" :class="{ joined: group.joined }" type="button" @click="join(group)">{{ group.joined ? '참여 중' : '함께하기' }} <span>{{ group.joined ? '✓' : '→' }}</span></button>
      </article>
    </div>
    <div class="groups-bottom"><span>사람마다 속도는 달라도, 같이 가면 더 멀리 가요.</span><RouterLink to="/practice">혼자 연습도 해보기 →</RouterLink></div>
  </section>
</template>
