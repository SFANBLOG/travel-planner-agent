import http from './http'

export interface UserInfo {
  id: string
  username: string
  email: string
  created_at?: string
}

export interface TokenResp {
  access_token: string
  user: UserInfo
}

export function register(data: { username: string; email: string; password: string }) {
  return http.post<TokenResp>('/auth/register', data)
}

export function login(identifier: string, password: string) {
  return http.post<TokenResp>('/auth/login', { identifier, password })
}

export function me() {
  return http.get<UserInfo>('/auth/me')
}
