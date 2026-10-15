import {
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  IconButton,
  Tooltip,
} from '@mui/material'
import WorkIcon from '@mui/icons-material/Work'
import ListAltIcon from '@mui/icons-material/ListAlt'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import { NavLink } from 'react-router-dom'

const DRAWER_WIDTH = 250
const COLLAPSED_WIDTH = 65

const navItems = [
  { label: 'Upwork', path: '/dashboard/upwork', icon: <WorkIcon /> },
  { label: 'Job Entries', path: '/dashboard/job-entries', icon: <ListAltIcon /> },
]

interface NavbarProps {
  open: boolean
  onToggle: () => void
}

export default function Navbar({ open, onToggle }: NavbarProps) {
  return (
    <Drawer
      variant="permanent"
      sx={{
        width: open ? DRAWER_WIDTH : COLLAPSED_WIDTH,
        flexShrink: 0,
        transition: 'width 0.2s ease',
        '& .MuiDrawer-paper': {
          width: open ? DRAWER_WIDTH : COLLAPSED_WIDTH,
          boxSizing: 'border-box',
          background: 'linear-gradient(195deg, #42424a, #191919)',
          color: '#fff',
          borderRight: 'none',
          boxShadow: '2px 0 8px rgba(0,0,0,0.18)',
          overflowX: 'hidden',
          transition: 'width 0.2s ease',
        },
      }}
    >
      <Box
        sx={{
          px: open ? 2.5 : 1,
          py: 2.5,
          borderBottom: '1px solid rgba(255,255,255,0.08)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: open ? 'space-between' : 'center',
        }}
      >
        {open && (
          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#fff', letterSpacing: 0.5 }}>
            Job App
          </Typography>
        )}
        <IconButton onClick={onToggle} size="small" sx={{ color: 'rgba(255,255,255,0.7)', '&:hover': { color: '#fff' } }}>
          {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </Box>

      <List sx={{ px: 1, pt: 1.5 }}>
        {navItems.map(item => (
          <NavLink key={item.path} to={item.path} style={{ textDecoration: 'none' }}>
            {({ isActive }) => (
              <Tooltip title={!open ? item.label : ''} placement="right">
                <ListItemButton
                  sx={{
                    borderRadius: '8px',
                    mb: 0.5,
                    justifyContent: open ? 'initial' : 'center',
                    px: open ? 2 : 1.5,
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
                  <ListItemIcon sx={{ color: '#fff', minWidth: open ? 36 : 'auto' }}>
                    {item.icon}
                  </ListItemIcon>
                  {open && (
                    <ListItemText
                      primary={
                        <span style={{ fontSize: '0.875rem', fontWeight: isActive ? 600 : 400, color: '#fff' }}>
                          {item.label}
                        </span>
                      }
                    />
                  )}
                </ListItemButton>
              </Tooltip>
            )}
          </NavLink>
        ))}
      </List>
    </Drawer>
  )
}
