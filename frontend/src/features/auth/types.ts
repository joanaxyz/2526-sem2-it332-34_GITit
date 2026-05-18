export type User = {
  id: number
  email: string
  student_id: string
  first_name: string
  last_name: string
}

export type AuthResponse = {
  access: string
  user: User
}
