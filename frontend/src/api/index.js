import request from '../utils/request'

export const login = (data) => request.post('/auth/login', data)
export const register = (data) => request.post('/auth/register', data)
export const getMe = () => request.get('/users/me')
export const getUsers = (params) => request.get('/users', { params })

export const getBuildings = () => request.get('/buildings')
export const createBuilding = (data) => request.post('/buildings', data)

export const getPermits = (params) => request.get('/permits', { params })
export const createPermit = (data) => request.post('/permits', data)
export const getPermit = (id) => request.get(`/permits/${id}`)
export const submitPermit = (id) => request.put(`/permits/${id}/submit`)
export const approvePermit = (id, data) => request.post(`/permits/${id}/approve`, data)
export const getApprovals = (id) => request.get(`/permits/${id}/approvals`)
export const startUsePermit = (id) => request.put(`/permits/${id}/start-use`)
export const requestDemolish = (id) => request.put(`/permits/${id}/request-demolish`)

export const getInspections = (params) => request.get('/inspections', { params })
export const createInspection = (data) => request.post('/inspections', data)
export const getOverdueAlert = () => request.get('/inspections/overdue-alert')

export const getHazards = (params) => request.get('/hazards', { params })
export const createHazard = (data) => request.post('/hazards', data)
export const assignHazard = (id, data) => request.put(`/hazards/${id}/assign`, data)
export const rectifyHazard = (id, data) => request.put(`/hazards/${id}/rectify`, data)
export const recheckHazard = (id, data) => request.put(`/hazards/${id}/recheck`, data)

export const getDemolitions = (params) => request.get('/demolitions', { params })
export const createDemolition = (data) => request.post('/demolitions', data)
export const confirmRestore = (id) => request.put(`/demolitions/${id}/confirm-restore`)
export const acceptDemolition = (id, data) => request.put(`/demolitions/${id}/accept`, data)

export const getAuditLogs = (params) => request.get('/audit-logs', { params })
