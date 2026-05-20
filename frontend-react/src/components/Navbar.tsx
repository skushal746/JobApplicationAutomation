import {
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
} from '@mui/material'
import WorkIcon from '@mui/icons-material/Work'
import { NavLink } from 'react-router-dom'

const DRAWER_WIDTH = 250

const navItems = [
  { label: 'Upwork', path: '/dashboard/upwork', icon: <WorkIcon /> },
]

export default function Navbar() {
  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          background: 'linear-gradient(195deg, #42424a, #191919)',
          color: '#fff',
          borderRight: 'none',
          boxShadow: '2px 0 8px rgba(0,0,0,0.18)',
        },
      }}
    >
      <Box sx={{ px: 2.5, py: 2.5, borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#fff', letterSpacing: 0.5 }}>
          Job App
        </Typography>
      </Box>

      <List sx={{ px: 1, pt: 1.5 }}>
        {navItems.map(item => (
          <NavLink key={item.path} to={item.path} style={{ textDecoration: 'none' }}>
            {({ isActive }) => (
              <ListItemButton
                sx={{
                  borderRadius: '8px',
                  mb: 0.5,
                  background: isActive
                    ? 'linear-gradient(195deg, #49a3f1, #1A73E8)'
                    : 'transparent',
                  boxShadow: isActive
                    ? '0 4px 20px 0 rgba(0,0,0,0.14), 0 7px 10px -5px rgba(26,115,232,0.4)'
                    : 'none',
                  '&:hover': {
                    background: isActive
                      ? 'linear-gradient(195deg, #49a3f1, #1A73E8)'
                      : 'rgba(255,255,255,0.08)',
                  },
                }}
              >
                <ListItemIcon sx={{ color: '#fff', minWidth: 36 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <span style={{ fontSize: '0.875rem', fontWeight: isActive ? 600 : 400, color: '#fff' }}>
                      {item.label}
                    </span>
                  }
                />
              </ListItemButton>
            )}
          </NavLink>
        ))}
      </List>
    </Drawer>
  )
}
