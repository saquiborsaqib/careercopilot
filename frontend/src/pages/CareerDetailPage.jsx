import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { careerApi, roadmapApi, recommendationApi } from '../api/endpoints'
import { Card, Badge, Spinner, Button } from '../components/Card'

export default function CareerDetailPage() {
  const { careerId } = useParams()
  const navigate = useNavigate()
  const [career, setCareer] = useState(null)
  const [gap, setGap] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [message, setMessage] = useState('')

  const load = () => {
    setLoading(true)
    Promise.all([careerApi.get(careerId), careerApi.skillGap(careerId)])
      .then(([careerRes, gapRes]) => {
        setCareer(careerRes.data)
        setGap(gapRes.data)
      })
      .finally(() => setLoading(false))
  }

  useEffect(load, [careerId])

  const handleGenerateRoadmap = async () => {
    setGenerating(true)
    setMessage('')
    try {
      await roadmapApi.generate(careerId)
      setMessage('Roadmap generated! Check the Roadmap page.')
    } catch {
      setMessage('Could not generate roadmap.')
    } finally {
      setGenerating(false)
    }
  }

  const handleGenerateRecommendations = async () => {
    setGenerating(true)
    setMessage('')
    try {
      await Promise.all([
        recommendationApi.generateCourses(careerId),
        recommendationApi.generateCertifications(careerId),
      ])
      setMessage('Course and certification recommendations generated!')
    } catch {
      setMessage('Could not generate recommendations.')
    } finally {
      setGenerating(false)
    }
  }

  if (loading) return <Spinner />
  if (!career || !gap) return null

  return (
    <div className="space-y-6">
      <button onClick={() => navigate('/careers')} className="text-sm text-slate-500 hover:text-slate-700">
        &larr; Back to careers
      </button>

      <div>
        <h1 className="text-2xl font-bold text-slate-900">{career.title}</h1>
        <p className="mt-1 text-sm text-slate-500">{career.description}</p>
      </div>

      <Card title="Skill Coverage" subtitle={`${gap.coverage_percent}% weighted coverage`}>
        <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
          <div className="h-full bg-brand-500" style={{ width: `${gap.coverage_percent}%` }} />
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card title="Already Developed">
          {gap.developed.length === 0 ? (
            <p className="text-sm text-slate-500">No matching skills yet.</p>
          ) : (
            <ul className="space-y-2">
              {gap.developed.map((item) => (
                <li key={item.skill_id} className="flex items-center justify-between rounded-lg bg-emerald-50 px-3 py-2">
                  <span className="text-sm font-medium text-slate-700">{item.skill_name}</span>
                  <Badge tone="low">{item.student_level}</Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Skill Gaps">
          {gap.gaps.length === 0 ? (
            <p className="text-sm text-slate-500">No gaps — you meet every requirement!</p>
          ) : (
            <ul className="space-y-2">
              {gap.gaps.map((item) => (
                <li key={item.skill_id} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
                  <span className="text-sm font-medium text-slate-700">{item.skill_name}</span>
                  <Badge tone={item.priority}>{item.priority} priority</Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <Card title="Next Steps">
        <div className="flex flex-wrap gap-3">
          <Button onClick={handleGenerateRoadmap} disabled={generating}>
            Generate roadmap for this career
          </Button>
          <Button variant="secondary" onClick={handleGenerateRecommendations} disabled={generating}>
            Generate course & certification recommendations
          </Button>
          <Link to="/roadmap">
            <Button variant="secondary">View my roadmaps</Button>
          </Link>
        </div>
        {message && <p className="mt-3 text-sm text-brand-700">{message}</p>}
      </Card>
    </div>
  )
}
