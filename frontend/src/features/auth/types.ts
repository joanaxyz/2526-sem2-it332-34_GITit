export type User = {
  id: number
  email: string
  display_name: string
}

export type AuthResponse = {
  access: string
  user: User
}
