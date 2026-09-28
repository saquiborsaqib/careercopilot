export default function ScoreRing({ value = 0, size = 128, label = 'Score' }) {
  const radius = (size - 14) / 2
  const circumference = 2 * Math.PI * radius
  const clamped = Math.max(0, Math.min(100, value))
  const offset = circumference - (clamped / 100) * circumference
  const color = clamped >= 70 ? '#16a34a' : clamped >= 40 ? '#d97706' : '#dc2626'

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="#e2e8f0" strokeWidth="10" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: 'stroke-dashoffset 0.6s ease' }}
        />
        <text x="50%" y="50%" textAnchor="middle" dy="0.1em" fontSize="26" fontWeight="700" fill="#1a1f2b">
          {Math.round(clamped)}%
        </text>
      </svg>
      <p className="mt-1 text-sm font-medium text-slate-500">{label}</p>
    </div>
  )
}
