import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AppBar, Toolbar, Avatar, Box, Typography, Menu, MenuItem, ListItemIcon } from '@mui/material'
import LogoutIcon from '@mui/icons-material/Logout'

export default function Header() {
  const navigate = useNavigate()
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)

  function handleAvatarClick(e: React.MouseEvent<HTMLElement>) {
    setAnchorEl(e.currentTarget)
  }

  function handleClose() {
    setAnchorEl(null)
  }

  function handleLogout() {
    localStorage.removeItem('token')
    handleClose()
    navigate('/login')
  }

  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        bgcolor: '#fff',
        borderBottom: '1px solid rgba(0,0,0,0.08)',
        color: '#344767',
      }}
    >
      <Toolbar sx={{ justifyContent: 'flex-end', minHeight: '56px !important' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box sx={{ textAlign: 'right' }}>
            <Typography variant="body2" sx={{ fontWeight: 600, color: '#344767', lineHeight: 1.2 }}>
              Kushal Sharma
            </Typography>
            <Typography variant="caption" sx={{ color: '#7b809a' }}>
              Admin
            </Typography>
          </Box>
          <Avatar
            onClick={handleAvatarClick}
            sx={{
              width: 36,
              height: 36,
              background: 'linear-gradient(195deg, #49a3f1, #1A73E8)',
              fontSize: '0.8rem',
              fontWeight: 700,
              cursor: 'pointer',
              boxShadow: '0 2px 8px rgba(26,115,232,0.35)',
            }}
          >
            KS
          </Avatar>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            slotProps={{
              paper: {
                elevation: 3,
                sx: { mt: 0.5, minWidth: 140, borderRadius: 2 },
              },
            }}
          >
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  )
}
