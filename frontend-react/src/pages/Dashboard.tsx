import { Box } from '@mui/material'
import { Outlet } from 'react-router-dom'
import Navbar from '../components/Navbar'

export default function Dashboard() {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f0f2f5' }}>
      <Navbar />
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Outlet />
      </Box>
    </Box>
  )
}
