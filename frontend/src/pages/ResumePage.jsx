import { useEffect, useRef, useState } from 'react'
import { resumeApi } from '../api/endpoints'
import { Card, Button, Badge, Spinner, EmptyState } from '../components/Card'

export default function ResumePage() {
  const [resumes, setResumes] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [selected, setSelected] = useState(null)
  const [improvement, setImprovement] = useState('')
  const [targetCareer, setTargetCareer] = useState('')
  const [improving, setImproving] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)

  const load = () => {
    setLoading(true)
    resumeApi
      .listMine()
      .then(({ data }) => {
        setResumes(data)
        if (data.length > 0) setSelected((prev) => prev || data[0])
      })
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleUpload = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return
    setUploading(true)
    setError('')
    try {
      const { data } = await resumeApi.upload(file)
      setSelected(data)
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Only PDF and DOCX are supported.')
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleImprove = async () => {
    if (!selected) return
    setImproving(true)
    setImprovement('')
    try {
      const { data } = await resumeApi.improve(selected.id, targetCareer || null)
      setImprovement(data.improvement)
    } finally {
      setImproving(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Resume</h1>
          <p className="text-sm text-slate-500">Upload your resume for AI-assisted feedback and skill extraction.</p>
        </div>
        <div>
          <input ref={fileInputRef} type="file" accept=".pdf,.docx" onChange={handleUpload} className="hidden" id="resume-upload" />
          <Button onClick={() => fileInputRef.current?.click()} disabled={uploading}>
            {uploading ? 'Uploading...' : 'Upload resume'}
          </Button>
        </div>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}

      {loading ? (
        <Spinner />
      ) : resumes.length === 0 ? (
        <EmptyState title="No resumes uploaded yet" description="PDF and DOCX are supported." />
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <Card title="Your resumes" className="lg:col-span-1">
            <ul className="space-y-2">
              {resumes.map((resume) => (
                <li key={resume.id}>
                  <button
                    onClick={() => setSelected(resume)}
                    className={`w-full rounded-lg border px-3 py-2 text-left text-sm ${
                      selected?.id === resume.id ? 'border-brand-500 bg-brand-50' : 'border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    <p className="font-medium text-slate-800">{resume.file_name}</p>
                    <Badge tone={resume.analysis_status === 'completed' ? 'low' : 'medium'}>{resume.analysis_status}</Badge>
                  </button>
                </li>
              ))}
            </ul>
          </Card>

          <div className="space-y-6 lg:col-span-2">
            {selected && (
              <>
                <Card title="Extracted text" subtitle={selected.file_name}>
                  <pre className="max-h-64 overflow-auto whitespace-pre-wrap text-sm text-slate-600">
                    {selected.extracted_text || 'No text extracted yet.'}
                  </pre>
                </Card>

                <Card title="AI Resume Improvement">
                  <div className="mb-3 flex gap-3">
                    <input
                      placeholder="Target career (optional, e.g. Data Analyst)"
                      value={targetCareer}
                      onChange={(e) => setTargetCareer(e.target.value)}
                      className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                    />
                    <Button onClick={handleImprove} disabled={improving}>
                      {improving ? 'Analyzing...' : 'Get feedback'}
                    </Button>
                  </div>
                  {improvement && (
                    <div className="whitespace-pre-wrap rounded-lg bg-slate-50 p-4 text-sm text-slate-700">{improvement}</div>
                  )}
                </Card>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
