import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { studentApi } from '../api/endpoints'
import { Card, Button } from '../components/Card'

const FIELDS = [
  { key: 'college', label: 'College' },
  { key: 'degree', label: 'Degree' },
  { key: 'branch', label: 'Branch' },
  { key: 'graduation_year', label: 'Graduation year', type: 'number' },
  { key: 'semester', label: 'Semester', type: 'number' },
  { key: 'cgpa', label: 'CGPA', type: 'number', step: '0.01' },
  { key: 'location', label: 'Current location' },
  { key: 'preferred_location', label: 'Preferred work location' },
  { key: 'career_interest', label: 'Career interest' },
]

export default function ProfilePage() {
  const { profile, refreshProfile } = useAuth()
  const [form, setForm] = useState(() =>
    Object.fromEntries(FIELDS.map((f) => [f.key, profile?.[f.key] ?? ''])),
  )
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  if (!profile) return null

  const handleChange = (key) => (event) => setForm((prev) => ({ ...prev, [key]: event.target.value }))

  const handleSave = async (event) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      const payload = {}
      FIELDS.forEach(({ key, type }) => {
        const value = form[key]
        payload[key] = value === '' ? null : type === 'number' ? Number(value) : value
      })
      await studentApi.updateProfile(profile.id, payload)
      await refreshProfile()
      setEditing(false)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not update profile.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Your Profile</h1>
        <p className="text-sm text-slate-500">Keep this up to date for the most accurate recommendations.</p>
      </div>

      <Card
        actions={
          !editing && (
            <Button variant="secondary" onClick={() => setEditing(true)}>
              Edit
            </Button>
          )
        }
      >
        {editing ? (
          <form onSubmit={handleSave} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {FIELDS.map((field) => (
              <label key={field.key} className="block text-sm font-medium text-slate-700">
                {field.label}
                <input
                  type={field.type || 'text'}
                  step={field.step}
                  value={form[field.key] ?? ''}
                  onChange={handleChange(field.key)}
                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
              </label>
            ))}
            {error && <p className="sm:col-span-2 text-sm text-red-600">{error}</p>}
            <div className="flex gap-3 sm:col-span-2">
              <Button type="submit" disabled={saving}>
                {saving ? 'Saving...' : 'Save changes'}
              </Button>
              <Button type="button" variant="secondary" onClick={() => setEditing(false)}>
                Cancel
              </Button>
            </div>
          </form>
        ) : (
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {FIELDS.map((field) => (
              <div key={field.key}>
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">{field.label}</dt>
                <dd className="mt-0.5 text-sm text-slate-800">{profile[field.key] ?? '—'}</dd>
              </div>
            ))}
          </dl>
        )}
      </Card>
    </div>
  )
}
