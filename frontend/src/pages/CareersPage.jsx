import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { careerApi } from '../api/endpoints'
import { Card, Badge, Spinner, Button } from '../components/Card'

export default function CareersPage() {
  const [careers, setCareers] = useState([])
  const [matches, setMatches] = useState(null)
  const [loading, setLoading] = useState(true)
  const [matchLoading, setMatchLoading] = useState(false)

  useEffect(() => {
    careerApi
      .listCatalog()
      .then(({ data }) => setCareers(data))
      .finally(() => setLoading(false))
  }, [])

  const handleGetMatches = () => {
    setMatchLoading(true)
    careerApi
      .recommendations(careers.length || 10)
      .then(({ data }) => setMatches(data))
      .finally(() => setMatchLoading(false))
  }

  const scoreByCareerId = Object.fromEntries((matches || []).map((m) => [m.career.id, m]))

  if (loading) return <Spinner />

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Explore Careers</h1>
          <p className="text-sm text-slate-500">Pick a career to see your skill gap and generate a roadmap.</p>
        </div>
        <Button onClick={handleGetMatches} disabled={matchLoading}>
          {matchLoading ? 'Scoring...' : 'Score against my profile'}
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {careers.map((career) => {
          const match = scoreByCareerId[career.id]
          return (
            <Card key={career.id}>
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-slate-900">{career.title}</p>
                  <p className="mt-1 text-xs uppercase tracking-wide text-slate-400">{career.industry}</p>
                </div>
                {career.demand_level && <Badge tone={career.demand_level === 'high' ? 'low' : 'medium'}>{career.demand_level} demand</Badge>}
              </div>
              {career.description && <p className="mt-2 line-clamp-2 text-sm text-slate-500">{career.description}</p>}
              {match && (
                <p className="mt-2 text-sm font-medium text-brand-700">Match score: {match.overall_score}%</p>
              )}
              <div className="mt-4">
                <Link to={`/careers/${career.id}`}>
                  <Button variant="secondary" className="w-full">
                    View skill gap
                  </Button>
                </Link>
              </div>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
