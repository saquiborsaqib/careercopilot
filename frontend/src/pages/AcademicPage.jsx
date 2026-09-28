import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { academicApi } from '../api/endpoints'
import { Card, Button, EmptyState, Spinner } from '../components/Card'

const emptyForm = { qualification: '', institution: '', field_of_study: '', percentage_or_cgpa: '', start_year: '', end_year: '' }

export default function AcademicPage() {
  const { profile } = useAuth()
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState(emptyForm)
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    academicApi
      .listMine()
      .then(({ data }) => setRecords(data))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleChange = (field) => (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }))

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    try {
      await academicApi.create({
        student_id: profile.id,
        qualification: form.qualification,
        institution: form.institution,
        field_of_study: form.field_of_study || null,
        percentage_or_cgpa: form.percentage_or_cgpa ? Number(form.percentage_or_cgpa) : null,
        start_year: form.start_year ? Number(form.start_year) : null,
        end_year: form.end_year ? Number(form.end_year) : null,
      })
      setForm(emptyForm)
      setShowForm(false)
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not add academic record.')
    }
  }

  const handleDelete = async (id) => {
    await academicApi.remove(id)
    load()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Academic Records</h1>
          <p className="text-sm text-slate-500">Your qualifications and academic history.</p>
        </div>
        <Button onClick={() => setShowForm((v) => !v)}>{showForm ? 'Cancel' : 'Add record'}</Button>
      </div>

      {showForm && (
        <Card>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Field label="Qualification">
              <input required value={form.qualification} onChange={handleChange('qualification')} className={inputClass} />
            </Field>
            <Field label="Institution">
              <input required value={form.institution} onChange={handleChange('institution')} className={inputClass} />
            </Field>
            <Field label="Field of study">
              <input value={form.field_of_study} onChange={handleChange('field_of_study')} className={inputClass} />
            </Field>
            <Field label="Percentage / CGPA">
              <input type="number" step="0.01" value={form.percentage_or_cgpa} onChange={handleChange('percentage_or_cgpa')} className={inputClass} />
            </Field>
            <Field label="Start year">
              <input type="number" value={form.start_year} onChange={handleChange('start_year')} className={inputClass} />
            </Field>
            <Field label="End year">
              <input type="number" value={form.end_year} onChange={handleChange('end_year')} className={inputClass} />
            </Field>
            {error && <p className="sm:col-span-2 text-sm text-red-600">{error}</p>}
            <div className="sm:col-span-2">
              <Button type="submit">Save record</Button>
            </div>
          </form>
        </Card>
      )}

      {loading ? (
        <Spinner />
      ) : records.length === 0 ? (
        <EmptyState title="No academic records yet" description="Add your qualifications to strengthen your profile." />
      ) : (
        <div className="space-y-3">
          {records.map((record) => (
            <Card key={record.id}>
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-slate-900">{record.qualification}</p>
                  <p className="text-sm text-slate-600">{record.institution}</p>
                  {record.field_of_study && <p className="text-sm text-slate-500">{record.field_of_study}</p>}
                  <p className="mt-1 text-xs text-slate-400">
                    {record.start_year || '?'} – {record.end_year || 'present'}
                    {record.percentage_or_cgpa ? ` · ${record.percentage_or_cgpa}` : ''}
                  </p>
                </div>
                <Button variant="danger" onClick={() => handleDelete(record.id)}>
                  Delete
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

const inputClass =
  'mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500'

function Field({ label, children }) {
  return (
    <label className="block text-sm font-medium text-slate-700">
      {label}
      {children}
    </label>
  )
}
