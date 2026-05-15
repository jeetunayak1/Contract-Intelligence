import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Box, AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemIcon, ListItemText, ListItemButton } from '@mui/material';
import { Dashboard as DashboardIcon, Description, Assessment, Warning, Notifications, Analytics as AnalyticsIcon, Security as SecurityIcon, Settings as SettingsIcon, Gavel, Shield } from '@mui/icons-material';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Dashboard from './pages/Dashboard';
import TransformationHub from './pages/TransformationHub';
import ContractIntelligence from './pages/ContractIntelligence';
import WarRoom from './pages/WarRoom';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00e676',
      light: '#33eb91',
      dark: '#00a152',
    },
    secondary: {
      main: '#f48fb1',
      light: '#f6a5c1',
      dark: '#aa647b',
    },
    background: {
      default: '#0a0a0c',
      paper: '#151518'
    },
    text: {
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)',
    }
  },
  typography: {
    fontFamily: '"Inter", "Outfit", sans-serif',
    h1: { fontFamily: 'Outfit' },
    h2: { fontFamily: 'Outfit' },
    h3: { fontFamily: 'Outfit' },
    h4: { fontFamily: 'Outfit', fontWeight: 600 },
    h5: { fontFamily: 'Outfit', fontWeight: 600 },
    h6: { fontFamily: 'Outfit', fontWeight: 600 },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          borderRadius: 16,
          border: '1px solid rgba(255, 255, 255, 0.08)',
          backgroundColor: '#151518',
        }
      }
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(10, 10, 12, 0.8)',
          backdropFilter: 'blur(12px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          boxShadow: 'none',
        }
      }
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#0a0a0c',
          borderRight: '1px solid rgba(255, 255, 255, 0.08)',
        }
      }
    }
  }
});

const drawerWidth = 240;

const menuItems = [
  { text: 'Command Center', icon: <DashboardIcon />, path: '/' },
  { text: 'Transformation Hub', icon: <Description />, path: '/sows' },
  { text: 'Contract Intelligence', icon: <Gavel />, path: '/contracts' },
  { text: 'AI War Room', icon: <Shield />, path: '/warroom' },
];

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          {/* App Bar */}
          <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
            <Toolbar sx={{ justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <SecurityIcon sx={{ mr: 2, color: 'primary.main', fontSize: 32 }} />
                <Typography variant="h5" noWrap component="div" sx={{ fontWeight: 800, letterSpacing: -1 }}>
                  SOW <span style={{ color: '#00e676' }}>SENTINEL</span>
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase', letterSpacing: 1.5, fontWeight: 600 }}>
                  Agentic Governance Active
                </Typography>
                <Box className="agent-pulse" sx={{ width: 8, height: 8, bgcolor: 'primary.main' }} />
              </Box>
            </Toolbar>
          </AppBar>

          {/* Sidebar */}
          <Drawer
            variant="permanent"
            sx={{
              width: drawerWidth,
              flexShrink: 0,
              '& .MuiDrawer-paper': {
                width: drawerWidth,
                boxSizing: 'border-box',
              },
            }}
          >
            <Toolbar />
            <Box sx={{ overflow: 'auto' }}>
              <List>
                {menuItems.map((item) => (
                  <ListItem key={item.text} disablePadding>
                    <ListItemButton component={Link} to={item.path}>
                      <ListItemIcon>{item.icon}</ListItemIcon>
                      <ListItemText primary={item.text} />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            </Box>
          </Drawer>

          {/* Main Content */}
          <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
            <Toolbar />
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/sows" element={<TransformationHub />} />
              <Route path="/contracts" element={<ContractIntelligence />} />
              <Route path="/warroom" element={<WarRoom />} />
            </Routes>
          </Box>
        </Box>
        <ToastContainer position="top-right" autoClose={3000} />
      </Router>
    </ThemeProvider>
  );
}

export default App;

// Made with Bob
