import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { dashboardApi } from '../api/endpoints'
import { Card, Badge, Spinner, EmptyState, Button } from '../components/Card'
import ScoreRing from '../components/ScoreRing'

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    dashboardApi
      .getMine()
      .then(({ data }) => setDashboard(data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spinner />
  if (!dashboard) return null

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Your Career Readiness</h1>
        <p className="text-sm text-slate-500">A snapshot of where you stand on your Campus-to-Corporate journey.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card title="Career Readiness Score" className="lg:col-span-1">
          <div className="flex items-center justify-center py-2">
            <ScoreRing value={dashboard.career_readiness_score} label="Overall readiness" size={150} />
          </div>
          <div className="mt-4 space-y-1 text-sm text-slate-500">
            <p>Profile completeness: {dashboard.profile_completeness_percent}%</p>
            <p>Resume uploaded: {dashboard.resume_uploaded ? 'Yes' : 'Not yet'}</p>
          </div>
        </Card>

        <Card title="Recommended Career" className="lg:col-span-2">
          {dashboard.recommended_career ? (
            <div>
              <p className="text-lg font-semibold text-slate-900">{dashboard.recommended_career.title}</p>
              <p className="text-sm text-slate-500">Match score: {dashboard.recommended_career.overall_score}%</p>
              <div className="mt-4">
                <Link to="/careers">
                  <Button variant="secondary">Explore careers</Button>
                </Link>
              </div>
            </div>
          ) : (
            <EmptyState
              title="No recommendation yet"
              description="Add a few skills to your profile to get a personalized career recommendation."
              action={
                <Link to="/skills">
                  <Button>Add skills</Button>
                </Link>
              }
            />
          )}
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card title="Skill Gaps" subtitle="Toward your recommended career">
          {dashboard.skill_gaps.length === 0 ? (
            <p className="text-sm text-slate-500">No skill gaps identified yet.</p>
          ) : (
            <ul className="space-y-2">
              {dashboard.skill_gaps.map((gap) => (
                <li key={gap.skill_name} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
                  <span className="text-sm font-medium text-slate-700">{gap.skill_name}</span>
                  <Badge tone={gap.priority}>{gap.priority} priority</Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Recommended Courses">
          {dashboard.recommended_courses.length === 0 ? (
            <EmptyState
              title="No course recommendations yet"
              description="Generate recommendations from a career's skill gap page."
              action={
                <Link to="/recommendations">
                  <Button variant="secondary">Go to recommendations</Button>
                </Link>
              }
            />
          ) : (
            <ul className="space-y-2">
              {dashboard.recommended_courses.map((course) => (
                <li key={course.id} className="rounded-lg bg-slate-50 px-3 py-2">
                  <p className="text-sm font-medium text-slate-700">{course.title}</p>
                  {course.explanation && <p className="text-xs text-slate-500">{course.explanation}</p>}
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <Card title="Career Roadmap">
        {dashboard.roadmap ? (
          <div>
            <div className="mb-3 flex items-center justify-between">
              <p className="text-sm font-medium text-slate-700">{dashboard.roadmap.title}</p>
              <span className="text-sm text-slate-500">{dashboard.roadmap.progress_percent}% complete</span>
            </div>
            <ul className="space-y-2">
              {dashboard.roadmap.items.map((item) => (
                <li key={item.id} className="flex items-center gap-3 text-sm">
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${
                      item.status === 'completed'
                        ? 'bg-emerald-500'
                        : item.status === 'in_progress'
                          ? 'bg-amber-500'
                          : 'bg-slate-300'
                    }`}
                  />
                  <span className={item.status === 'completed' ? 'text-slate-400 line-through' : 'text-slate-700'}>
                    {item.title}
                  </span>
                </li>
              ))}
            </ul>
            <div className="mt-4">
              <Link to="/roadmap">
                <Button variant="secondary">Manage roadmap</Button>
              </Link>
            </div>
          </div>
        ) : (
          <EmptyState
            title="No roadmap yet"
            description="Generate a personalized roadmap from your recommended career's skill gap."
            action={
              <Link to="/careers">
                <Button>Explore careers</Button>
              </Link>
            }
          />
        )}
      </Card>
    </div>
  )
}
