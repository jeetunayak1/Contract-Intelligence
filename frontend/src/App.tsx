import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Box, AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemIcon, ListItemText, ListItemButton } from '@mui/material';
import { Dashboard as DashboardIcon, Description, Assessment, Warning, Notifications, Analytics as AnalyticsIcon, Security as SecurityIcon, Settings as SettingsIcon } from '@mui/icons-material';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Pages
import Dashboard from './pages/Dashboard';
import RiskReport from './pages/RiskReport';
import IntegrationConfig from './pages/IntegrationConfig';
import Settings from './pages/Settings';
import SOWManagement from './pages/SOWManagement';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const drawerWidth = 240;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Risk Report', icon: <SecurityIcon />, path: '/risk-report' },
  { text: 'Integration Setup', icon: <SettingsIcon />, path: '/integrations' },
  { text: 'API Settings', icon: <SettingsIcon />, path: '/settings' },
  { text: 'SOW Management', icon: <Description />, path: '/sows' },
  { text: 'Compliance', icon: <Assessment />, path: '/compliance' },
  { text: 'Scope Creep', icon: <Warning />, path: '/scope-creep' },
  { text: 'Alerts', icon: <Notifications />, path: '/alerts' },
  { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' },
];

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          {/* App Bar */}
          <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
            <Toolbar>
              <SecurityIcon sx={{ mr: 2 }} />
              <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold' }}>
                SOW Sentinel
              </Typography>
              <Typography variant="caption" sx={{ ml: 2, color: 'rgba(255,255,255,0.7)' }}>
                Preventing Revenue Leakage
              </Typography>
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
                    <ListItemButton component="a" href={item.path}>
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
              <Route path="/risk-report" element={<RiskReport sowId="SOW-2024-ACME-001" />} />
              <Route path="/integrations" element={<IntegrationConfig />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/sows" element={<SOWManagement />} />
              <Route path="/compliance" element={<div>Compliance - Coming Soon</div>} />
              <Route path="/scope-creep" element={<div>Scope Creep Detection - Coming Soon</div>} />
              <Route path="/alerts" element={<div>Alerts - Coming Soon</div>} />
              <Route path="/analytics" element={<div>Analytics - Coming Soon</div>} />
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
