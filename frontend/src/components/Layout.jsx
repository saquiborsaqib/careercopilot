import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: '▦' },
  { to: '/profile', label: 'Profile', icon: '▤' },
  { to: '/academic', label: 'Academics', icon: '▨' },
  { to: '/skills', label: 'Skills', icon: '✦' },
  { to: '/careers', label: 'Careers', icon: '⚑' },
  { to: '/roadmap', label: 'Roadmap', icon: '▲' },
  { to: '/resume', label: 'Resume', icon: '☷' },
  { to: '/interview', label: 'Mock Interview', icon: '⚙' },
  { to: '/opportunities', label: 'Opportunities', icon: '✦' },
  { to: '/recommendations', label: 'Recommendations', icon: '★' },
]

export default function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="hidden w-64 shrink-0 flex-col border-r border-slate-200 bg-white md:flex">
        <div className="px-6 py-5">
          <p className="text-lg font-bold text-brand-700">AI CareerPilot</p>
          <p className="text-xs text-slate-400">Campus to Corporate</p>
        </div>
        <nav className="flex-1 space-y-1 px-3">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-brand-50 text-brand-700'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`
              }
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-slate-200 p-4">
          <p className="truncate text-sm font-medium text-slate-700">{user?.name}</p>
          <p className="truncate text-xs text-slate-400">{user?.email}</p>
          <button
            onClick={logout}
            className="mt-3 w-full rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-100"
          >
            Log out
          </button>
        </div>
      </aside>

      <div className="flex min-h-screen flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 md:hidden">
          <p className="text-lg font-bold text-brand-700">AI CareerPilot</p>
          <button onClick={logout} className="text-sm font-medium text-slate-600">
            Log out
          </button>
        </header>
        <main className="flex-1 p-4 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
