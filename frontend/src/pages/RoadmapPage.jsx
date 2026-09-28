import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { roadmapApi } from '../api/endpoints'
import { Card, Spinner, EmptyState, Button } from '../components/Card'

const STATUS_CYCLE = {
  not_started: 'in_progress',
  in_progress: 'completed',
  completed: 'not_started',
}

const STATUS_LABEL = {
  not_started: 'Not started',
  in_progress: 'In progress',
  completed: 'Completed',
}

export default function RoadmapPage() {
  const [roadmaps, setRoadmaps] = useState([])
  const [loading, setLoading] = useState(true)
  const [narratives, setNarratives] = useState({})

  const load = () => {
    setLoading(true)
    roadmapApi
      .listMine()
      .then(({ data }) => setRoadmaps(data))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleCycleStatus = async (roadmapId, item) => {
    const nextStatus = STATUS_CYCLE[item.status]
    await roadmapApi.updateItemStatus(item.id, nextStatus)
    load()
  }

  const handleNarrative = async (roadmapId) => {
    const { data } = await roadmapApi.narrative(roadmapId)
    setNarratives((prev) => ({ ...prev, [roadmapId]: data.narrative }))
  }

  if (loading) return <Spinner />

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Your Roadmaps</h1>
        <p className="text-sm text-slate-500">Step-by-step plans generated from your skill gaps.</p>
      </div>

      {roadmaps.length === 0 ? (
        <EmptyState
          title="No roadmaps yet"
          description="Generate one from a career's skill gap page."
          action={
            <Link to="/careers">
              <Button>Explore careers</Button>
            </Link>
          }
        />
      ) : (
        <div className="space-y-6">
          {roadmaps.map((roadmap) => {
            const total = roadmap.items.length
            const completed = roadmap.items.filter((i) => i.status === 'completed').length
            const progress = total ? Math.round((completed / total) * 100) : 0

            return (
              <Card
                key={roadmap.id}
                title={roadmap.title}
                subtitle={`${progress}% complete · ${roadmap.status}`}
                actions={
                  <Button variant="secondary" onClick={() => handleNarrative(roadmap.id)}>
                    Summarize
                  </Button>
                }
              >
                {narratives[roadmap.id] && (
                  <p className="mb-4 rounded-lg bg-brand-50 p-3 text-sm text-brand-800">{narratives[roadmap.id]}</p>
                )}
                <div className="mb-4 h-2 w-full overflow-hidden rounded-full bg-slate-100">
                  <div className="h-full bg-brand-500 transition-all" style={{ width: `${progress}%` }} />
                </div>
                <ol className="space-y-2">
                  {roadmap.items
                    .slice()
                    .sort((a, b) => a.sequence - b.sequence)
                    .map((item) => (
                      <li key={item.id} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
                        <div>
                          <p className={`text-sm font-medium ${item.status === 'completed' ? 'text-slate-400 line-through' : 'text-slate-800'}`}>
                            {item.sequence}. {item.title}
                          </p>
                          {item.description && <p className="text-xs text-slate-500">{item.description}</p>}
                        </div>
                        <button
                          onClick={() => handleCycleStatus(roadmap.id, item)}
                          className="shrink-0 rounded-full border border-slate-300 px-3 py-1 text-xs font-medium text-slate-600 hover:bg-white"
                        >
                          {STATUS_LABEL[item.status]}
                        </button>
                      </li>
                    ))}
                </ol>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
