export type User = {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
}

export type AuthResponse = {
  access: string
  user: User
}
