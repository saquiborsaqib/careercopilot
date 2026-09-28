import { useEffect, useState } from 'react'
import { recommendationApi } from '../api/endpoints'
import { Card, Badge, Spinner, EmptyState, Button } from '../components/Card'

const TYPES = [
  { value: '', label: 'All' },
  { value: 'career', label: 'Careers' },
  { value: 'course', label: 'Courses' },
  { value: 'certification', label: 'Certifications' },
  { value: 'opportunity', label: 'Opportunities' },
]

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [type, setType] = useState('')
  const [generating, setGenerating] = useState(false)

  const load = () => {
    setLoading(true)
    recommendationApi
      .listMine(type || undefined)
      .then(({ data }) => setRecommendations(data))
      .finally(() => setLoading(false))
  }

  useEffect(load, [type])

  const handleGenerateCareers = async () => {
    setGenerating(true)
    try {
      await recommendationApi.generateCareers()
      load()
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Recommendations</h1>
          <p className="text-sm text-slate-500">Personalized suggestions based on your profile and skill gaps.</p>
        </div>
        <Button onClick={handleGenerateCareers} disabled={generating}>
          {generating ? 'Generating...' : 'Generate career recommendations'}
        </Button>
      </div>

      <div className="flex flex-wrap gap-3">
        {TYPES.map((t) => (
          <button
            key={t.value}
            onClick={() => setType(t.value)}
            className={`rounded-full border px-3 py-1.5 text-sm font-medium ${
              type === t.value ? 'border-brand-500 bg-brand-50 text-brand-700' : 'border-slate-300 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading ? (
        <Spinner />
      ) : recommendations.length === 0 ? (
        <EmptyState
          title="No recommendations yet"
          description="Generate career recommendations, or visit a career's skill gap page to generate course and certification recommendations."
        />
      ) : (
        <div className="space-y-3">
          {recommendations.map((rec) => (
            <Card key={rec.id}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-semibold text-slate-900">{rec.title}</p>
                  {rec.explanation && <p className="mt-1 text-sm text-slate-600">{rec.explanation}</p>}
                  {rec.source && <p className="mt-1 text-xs text-slate-400">Source: {rec.source}</p>}
                </div>
                <div className="flex shrink-0 flex-col items-end gap-2">
                  <Badge tone="brand">{rec.recommendation_type}</Badge>
                  {rec.score != null && <span className="text-sm font-semibold text-slate-700">{rec.score}%</span>}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
