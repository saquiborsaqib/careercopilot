import { useEffect, useMemo, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { skillApi } from '../api/endpoints'
import { Card, Button, Badge, Spinner, EmptyState } from '../components/Card'

const LEVELS = ['beginner', 'intermediate', 'advanced', 'expert']

export default function SkillsPage() {
  const { profile } = useAuth()
  const [mySkills, setMySkills] = useState([])
  const [catalog, setCatalog] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedSkillId, setSelectedSkillId] = useState('')
  const [level, setLevel] = useState('beginner')
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    Promise.all([skillApi.listMine(), skillApi.listCatalog()])
      .then(([mine, cat]) => {
        setMySkills(mine.data)
        setCatalog(cat.data)
      })
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const catalogById = useMemo(() => Object.fromEntries(catalog.map((s) => [s.id, s])), [catalog])
  const assignedIds = useMemo(() => new Set(mySkills.map((s) => s.skill_id)), [mySkills])
  const filteredCatalog = useMemo(
    () =>
      catalog
        .filter((s) => !assignedIds.has(s.id))
        .filter((s) => s.name.toLowerCase().includes(search.toLowerCase()))
        .slice(0, 8),
    [catalog, assignedIds, search],
  )

  const handleAssign = async (event) => {
    event.preventDefault()
    setError('')
    if (!selectedSkillId) {
      setError('Select a skill first.')
      return
    }
    try {
      await skillApi.assign({
        student_id: profile.id,
        skill_id: Number(selectedSkillId),
        proficiency_level: level,
        source: 'profile',
      })
      setSelectedSkillId('')
      setSearch('')
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not add skill.')
    }
  }

  const handleRemove = async (studentSkillId) => {
    await skillApi.remove(studentSkillId)
    load()
  }

  if (loading) return <Spinner />

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Your Skills</h1>
        <p className="text-sm text-slate-500">These power your career match, skill gap and roadmap.</p>
      </div>

      <Card title="Add a skill">
        <form onSubmit={handleAssign} className="space-y-3">
          <input
            placeholder="Search skills (e.g. Python, SQL)"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setSelectedSkillId('')
            }}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
          {search && (
            <div className="flex flex-wrap gap-2">
              {filteredCatalog.length === 0 && <p className="text-sm text-slate-400">No matching skills.</p>}
              {filteredCatalog.map((skill) => (
                <button
                  type="button"
                  key={skill.id}
                  onClick={() => {
                    setSelectedSkillId(String(skill.id))
                    setSearch(skill.name)
                  }}
                  className={`rounded-full border px-3 py-1 text-sm ${
                    String(skill.id) === selectedSkillId
                      ? 'border-brand-500 bg-brand-50 text-brand-700'
                      : 'border-slate-300 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {skill.name}
                </button>
              ))}
            </div>
          )}
          <div className="flex items-center gap-3">
            <select value={level} onChange={(e) => setLevel(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
              {LEVELS.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
            <Button type="submit">Add skill</Button>
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </form>
      </Card>

      {mySkills.length === 0 ? (
        <EmptyState title="No skills added yet" description="Search above to add your first skill." />
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {mySkills.map((skill) => (
            <Card key={skill.id}>
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-slate-900">{catalogById[skill.skill_id]?.name || `Skill #${skill.skill_id}`}</p>
                  <div className="mt-1 flex gap-2">
                    <Badge tone="brand">{skill.proficiency_level}</Badge>
                    <Badge>{skill.source}</Badge>
                  </div>
                </div>
                <button onClick={() => handleRemove(skill.id)} className="text-xs text-slate-400 hover:text-red-600">
                  Remove
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
