export type User = {
  id: number
  username: string
  email: string
}

export type AuthResponse = {
  access: string
  user: User
}
