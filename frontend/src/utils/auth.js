const TOKEN_KEY = 'scaffold_token'
const USER_KEY = 'scaffold_user'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export function getUser() {
  const data = localStorage.getItem(USER_KEY)
  return data ? JSON.parse(data) : null
}

export function setUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function removeUser() {
  localStorage.removeItem(USER_KEY)
}

export function logout() {
  removeToken()
  removeUser()
}

export const roleMap = {
  constructor: '施工单位',
  inspector: '巡检员',
  heritage: '文保员',
  safety: '安监员',
}

export const statusMap = {
  applied: '已申请',
  approving: '审批中',
  can_scaffold: '可搭设',
  in_use: '使用中',
  pending_demolish: '待拆除',
  accepted: '已验收',
  rejected: '已驳回',
}

export const statusTagType = {
  applied: 'info',
  approving: 'warning',
  can_scaffold: '',
  in_use: 'success',
  pending_demolish: 'danger',
  accepted: 'success',
  rejected: 'danger',
}

export const hazardLevelMap = {
  minor: '一般隐患',
  major: '较大隐患',
  critical: '重大隐患',
}

export const hazardLevelTagType = {
  minor: 'info',
  major: 'warning',
  critical: 'danger',
}

export const hazardStatusMap = {
  open: '待派单',
  assigned: '已派单',
  rectifying: '整改中',
  recheck: '待复查',
  closed: '已关闭',
}
