import http from './http'

export interface ItinerarySpot {
  id: string
  spot_id?: string
  name?: string
  order_index: number
  start_time?: string | null
  end_time?: string | null
  duration_minutes: number
  transport_to_next?: string | null
  estimated_cost: number
  notes?: string | null
}

export interface ItineraryDay {
  id: string
  day_number: number
  date?: string | null
  theme?: string | null
  summary?: string | null
  weather_info?: any
  spots: ItinerarySpot[]
}

export interface Trip {
  id: string
  user_id: string
  title: string
  destination: string
  start_date?: string | null
  end_date?: string | null
  budget: number
  status: string
  requirements?: any
  generated_plan?: any
  days: ItineraryDay[]
  created_at?: string | null
}

export interface TripListItem {
  id: string
  title: string
  destination: string
  start_date?: string | null
  end_date?: string | null
  budget: number
  status: string
  created_at?: string | null
}

export function listTrips() {
  return http.get<TripListItem[]>('/trips')
}

export function getTrip(id: string) {
  return http.get<Trip>(`/trips/${id}`)
}

export function deleteTrip(id: string) {
  return http.delete<{ ok: boolean }>(`/trips/${id}`)
}

export function updateTripStatus(id: string, status: string) {
  return http.post<Trip>(`/trips/${id}/status`, { status })
}

export interface GenerateTripPayload {
  user_message: string
  destination?: string
  start_date?: string
  end_date?: string
  budget?: number
  travelers?: number
  travel_style?: string
  title?: string
}

export function generateTrip(payload: GenerateTripPayload) {
  return http.post<Trip>('/agent/generate-trip', payload)
}

export function chat(message: string) {
  return http.post<any>('/agent/chat', { message })
}
