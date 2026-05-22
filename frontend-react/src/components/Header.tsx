import { AppBar, Toolbar, Avatar, Box, Typography } from '@mui/material'

export default function Header() {
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
        </Box>
      </Toolbar>
    </AppBar>
  )
}
