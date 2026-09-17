import http from './http'

export interface SpotResult {
  id: string
  name: string
  name_en?: string
  city: string
  country?: string
  category: string
  address?: string
  latitude?: number
  longitude?: number
  rating: number
  ticket_info?: { price?: number; type?: string }
  description?: string
  recommend_duration?: number
  tags?: string[]
  relevance_score?: number
}

export function searchSpots(params: {
  q?: string
  city?: string
  category?: string
  top_k?: number
}) {
  return http.get<SpotResult[]>('/spots/search', { params })
}
