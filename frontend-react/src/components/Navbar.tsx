import { NavLink } from 'react-router-dom'

const navItems = [
  { label: 'Upwork', path: '/dashboard/upwork' },
]

export default function Navbar() {
  return (
    <nav className="sidebar">
      <div className="sidebar-brand">Job App</div>
      <ul className="sidebar-nav">
        {navItems.map(item => (
          <li key={item.path}>
            <NavLink
              to={item.path}
              className={({ isActive }) =>
                'sidebar-link' + (isActive ? ' sidebar-link--active' : '')
              }
            >
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}
