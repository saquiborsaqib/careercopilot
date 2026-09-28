import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { studentApi } from '../api/endpoints'
import { Button } from '../components/Card'

const emptyForm = {
  college: '',
  degree: '',
  branch: '',
  graduation_year: '',
  semester: '',
  cgpa: '',
  location: '',
  career_interest: '',
  preferred_location: '',
}

export default function OnboardingPage() {
  const { user, refreshProfile } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (field) => (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }))

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const payload = {
        user_id: user.id,
        college: form.college || null,
        degree: form.degree || null,
        branch: form.branch || null,
        graduation_year: form.graduation_year ? Number(form.graduation_year) : null,
        semester: form.semester ? Number(form.semester) : null,
        cgpa: form.cgpa ? Number(form.cgpa) : null,
        location: form.location || null,
        career_interest: form.career_interest || null,
        preferred_location: form.preferred_location || null,
      }
      await studentApi.createProfile(payload)
      await refreshProfile()
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save your profile. Please check the details.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
      <div className="w-full max-w-2xl rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-xl font-semibold text-slate-900">Tell us about yourself, {user?.name?.split(' ')[0]}</h1>
        <p className="mt-1 text-sm text-slate-500">
          This builds the foundation for your career recommendations, skill gaps and roadmap.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="College">
            <input value={form.college} onChange={handleChange('college')} className={inputClass} />
          </Field>
          <Field label="Degree">
            <input value={form.degree} onChange={handleChange('degree')} placeholder="B.Tech" className={inputClass} />
          </Field>
          <Field label="Branch">
            <input value={form.branch} onChange={handleChange('branch')} placeholder="CSE" className={inputClass} />
          </Field>
          <Field label="Graduation year">
            <input
              type="number"
              value={form.graduation_year}
              onChange={handleChange('graduation_year')}
              className={inputClass}
            />
          </Field>
          <Field label="Semester">
            <input type="number" value={form.semester} onChange={handleChange('semester')} className={inputClass} />
          </Field>
          <Field label="CGPA (0-10)">
            <input
              type="number"
              step="0.01"
              min="0"
              max="10"
              value={form.cgpa}
              onChange={handleChange('cgpa')}
              className={inputClass}
            />
          </Field>
          <Field label="Current location">
            <input value={form.location} onChange={handleChange('location')} className={inputClass} />
          </Field>
          <Field label="Preferred work location">
            <input value={form.preferred_location} onChange={handleChange('preferred_location')} className={inputClass} />
          </Field>
          <Field label="Career interest" full>
            <input
              value={form.career_interest}
              onChange={handleChange('career_interest')}
              placeholder="e.g. Data Analyst"
              className={inputClass}
            />
          </Field>

          {error && <p className="sm:col-span-2 text-sm text-red-600">{error}</p>}
          <div className="sm:col-span-2">
            <Button type="submit" disabled={submitting} className="w-full">
              {submitting ? 'Saving...' : 'Save profile and continue'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

const inputClass =
  'mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500'

function Field({ label, children, full }) {
  return (
    <label className={`block text-sm font-medium text-slate-700 ${full ? 'sm:col-span-2' : ''}`}>
      {label}
      {children}
    </label>
  )
}
