import axios from 'axios'

export const api = axios.create({ baseURL: 'http://127.0.0.1:8000' })

// Если пользователь авторизован, автоматически добавляем его токен к HTTP-запросам.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Token ${token}`
  return config
})

// Преобразуем сообщения об ошибках, полученные от сервера в текст для отображения пользователю.
export function errorText(e) {
  const data = e.response?.data
  if (!data || typeof data !== 'object') return e.message
  return Object.entries(data)
    .map(([k, v]) => `${k === 'detail' || k === 'non_field_errors' ? '' : k + ': '}${[].concat(v).join(' ')}`)
    .join('\n')
}
