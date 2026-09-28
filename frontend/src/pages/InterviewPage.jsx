import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { careerApi, interviewApi } from '../api/endpoints'
import { Card, Button, Badge } from '../components/Card'

const SESSION_TYPES = ['general', 'technical', 'hr', 'behavioral']

export default function InterviewPage() {
  const { profile } = useAuth()
  const [careers, setCareers] = useState([])
  const [careerId, setCareerId] = useState('')
  const [sessionType, setSessionType] = useState('general')
  const [session, setSession] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [answerText, setAnswerText] = useState('')
  const [lastFeedback, setLastFeedback] = useState(null)
  const [history, setHistory] = useState([])
  const [busy, setBusy] = useState(false)
  const [completed, setCompleted] = useState(null)

  useEffect(() => {
    careerApi.listCatalog().then(({ data }) => setCareers(data))
  }, [])

  const startSession = async () => {
    setBusy(true)
    setCompleted(null)
    setHistory([])
    setLastFeedback(null)
    try {
      const { data } = await interviewApi.start({
        student_id: profile.id,
        career_id: careerId ? Number(careerId) : null,
        session_type: sessionType,
      })
      setSession(data)
      const { data: question } = await interviewApi.nextQuestion(data.id)
      setCurrentQuestion(question)
    } finally {
      setBusy(false)
    }
  }

  const submitAnswer = async () => {
    if (!answerText.trim()) return
    setBusy(true)
    try {
      const { data: answered } = await interviewApi.submitAnswer(currentQuestion.id, answerText)
      setLastFeedback(answered)
      setHistory((prev) => [...prev, answered])
      setAnswerText('')
    } finally {
      setBusy(false)
    }
  }

  const nextQuestion = async () => {
    setBusy(true)
    setLastFeedback(null)
    try {
      const { data: question } = await interviewApi.nextQuestion(session.id)
      setCurrentQuestion(question)
    } finally {
      setBusy(false)
    }
  }

  const finishSession = async () => {
    setBusy(true)
    try {
      const { data } = await interviewApi.complete(session.id)
      setCompleted(data)
      setCurrentQuestion(null)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Mock Interview</h1>
        <p className="text-sm text-slate-500">Practice with AI-generated questions and get instant feedback.</p>
      </div>

      {!session && (
        <Card title="Start a new session">
          <div className="flex flex-wrap items-end gap-4">
            <label className="text-sm font-medium text-slate-700">
              Career focus
              <select value={careerId} onChange={(e) => setCareerId(e.target.value)} className="mt-1 block rounded-lg border border-slate-300 px-3 py-2 text-sm">
                <option value="">General</option>
                {careers.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.title}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm font-medium text-slate-700">
              Interview type
              <select value={sessionType} onChange={(e) => setSessionType(e.target.value)} className="mt-1 block rounded-lg border border-slate-300 px-3 py-2 text-sm">
                {SESSION_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </label>
            <Button onClick={startSession} disabled={busy}>
              Start interview
            </Button>
          </div>
        </Card>
      )}

      {session && !completed && (
        <Card title={`Session #${session.id}`} subtitle={`${session.session_type} interview`}>
          {currentQuestion && (
            <div className="space-y-3">
              <p className="rounded-lg bg-brand-50 p-4 text-sm font-medium text-brand-900">{currentQuestion.question}</p>
              {!lastFeedback ? (
                <>
                  <textarea
                    rows={5}
                    value={answerText}
                    onChange={(e) => setAnswerText(e.target.value)}
                    placeholder="Type your answer..."
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                  />
                  <Button onClick={submitAnswer} disabled={busy}>
                    Submit answer
                  </Button>
                </>
              ) : (
                <div className="space-y-3">
                  <div className="rounded-lg bg-slate-50 p-4 text-sm">
                    <Badge tone={lastFeedback.score >= 70 ? 'low' : lastFeedback.score >= 40 ? 'medium' : 'high'}>
                      Score: {lastFeedback.score}/100
                    </Badge>
                    <pre className="mt-2 whitespace-pre-wrap text-sm text-slate-700">{lastFeedback.feedback}</pre>
                  </div>
                  <div className="flex gap-3">
                    <Button onClick={nextQuestion} disabled={busy}>
                      Next question
                    </Button>
                    <Button variant="secondary" onClick={finishSession} disabled={busy}>
                      Finish session
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
          {history.length > 0 && (
            <div className="mt-6 border-t border-slate-100 pt-4">
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Answered so far ({history.length})</p>
            </div>
          )}
        </Card>
      )}

      {completed && (
        <Card title="Session complete">
          <p className="text-lg font-semibold text-slate-900">Overall score: {completed.overall_score ?? '—'}/100</p>
          <p className="mt-2 text-sm text-slate-600">{completed.feedback}</p>
          <Button
            className="mt-4"
            onClick={() => {
              setSession(null)
              setCompleted(null)
            }}
          >
            Start another session
          </Button>
        </Card>
      )}
    </div>
  )
}
