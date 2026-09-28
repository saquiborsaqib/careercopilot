import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { authApi, studentApi } from '../api/endpoints'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('careerpilot_token'))
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadCurrentUser = useCallback(async () => {
    if (!localStorage.getItem('careerpilot_token')) {
      setUser(null)
      setProfile(null)
      setLoading(false)
      return
    }
    try {
      const { data: currentUser } = await authApi.me()
      setUser(currentUser)
      try {
        const { data: currentProfile } = await studentApi.getMyProfile()
        setProfile(currentProfile)
      } catch {
        setProfile(null)
      }
    } catch {
      localStorage.removeItem('careerpilot_token')
      setToken(null)
      setUser(null)
      setProfile(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadCurrentUser()
  }, [loadCurrentUser])

  const login = async (email, password) => {
    const { data } = await authApi.login(email, password)
    localStorage.setItem('careerpilot_token', data.access_token)
    setToken(data.access_token)
    setUser(data.user)
    try {
      const { data: currentProfile } = await studentApi.getMyProfile()
      setProfile(currentProfile)
    } catch {
      setProfile(null)
    }
    return data.user
  }

  const register = async (payload) => {
    await authApi.register(payload)
    return login(payload.email, payload.password)
  }

  const logout = () => {
    localStorage.removeItem('careerpilot_token')
    setToken(null)
    setUser(null)
    setProfile(null)
  }

  const refreshProfile = async () => {
    try {
      const { data: currentProfile } = await studentApi.getMyProfile()
      setProfile(currentProfile)
      return currentProfile
    } catch {
      setProfile(null)
      return null
    }
  }

  const value = {
    token,
    user,
    profile,
    loading,
    isAuthenticated: Boolean(token && user),
    hasProfile: Boolean(profile),
    login,
    register,
    logout,
    refreshProfile,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
