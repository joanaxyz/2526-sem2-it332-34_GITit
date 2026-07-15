export type User = {
  id: number
  username: string
  email: string
  is_staff: boolean
}

export type AuthResponse = {
  access: string
  user: User
}
