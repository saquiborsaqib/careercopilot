import { useEffect, useState } from 'react'
import { opportunityApi } from '../api/endpoints'
import { Card, Badge, Spinner, EmptyState, Button } from '../components/Card'

const TYPES = [
  { value: '', label: 'All' },
  { value: 'internship', label: 'Internships' },
  { value: 'job', label: 'Jobs' },
  { value: 'government', label: 'Government' },
]

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState([])
  const [loading, setLoading] = useState(true)
  const [type, setType] = useState('')
  const [matchedOnly, setMatchedOnly] = useState(false)

  const load = (opportunityType, useMatches) => {
    setLoading(true)
    const call = useMatches ? opportunityApi.matches(opportunityType || undefined) : opportunityApi.list(opportunityType || undefined)
    call.then(({ data }) => setOpportunities(data)).finally(() => setLoading(false))
  }

  useEffect(() => load(type, matchedOnly), [type, matchedOnly])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Opportunities</h1>
        <p className="text-sm text-slate-500">Internships, jobs and government opportunities.</p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
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
        <Button variant={matchedOnly ? 'primary' : 'secondary'} onClick={() => setMatchedOnly((v) => !v)}>
          {matchedOnly ? 'Showing matches for me' : 'Show matches for me'}
        </Button>
      </div>

      {loading ? (
        <Spinner />
      ) : opportunities.length === 0 ? (
        <EmptyState title="No opportunities found" />
      ) : (
        <div className="space-y-3">
          {opportunities.map((opportunity) => (
            <Card key={opportunity.id}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-semibold text-slate-900">{opportunity.title}</p>
                  <p className="text-sm text-slate-600">{opportunity.organization}</p>
                  {opportunity.description && <p className="mt-1 text-sm text-slate-500">{opportunity.description}</p>}
                  {opportunity.eligibility && (
                    <p className="mt-1 text-xs text-slate-400">Eligibility: {opportunity.eligibility}</p>
                  )}
                  <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-400">
                    {opportunity.location && <span>{opportunity.location}</span>}
                    {opportunity.deadline && <span>· Deadline {new Date(opportunity.deadline).toLocaleDateString()}</span>}
                  </div>
                </div>
                <div className="flex shrink-0 flex-col items-end gap-2">
                  <Badge tone="brand">{opportunity.opportunity_type}</Badge>
                  {opportunity.application_url && (
                    <a
                      href={opportunity.application_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs font-medium text-brand-600 hover:underline"
                    >
                      Apply &rarr;
                    </a>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
