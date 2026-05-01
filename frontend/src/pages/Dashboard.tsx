import React from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  Warning,
  CheckCircle,
  Error,
  Description,
  Assessment,
} from '@mui/icons-material';

const Dashboard: React.FC = () => {
  // Mock data - will be replaced with real API calls
  const stats = {
    totalContracts: 24,
    activeContracts: 18,
    expiringSoon: 3,
    slaCompliance: 95.8,
    criticalAlerts: 2,
    highRisks: 5,
  };

  const recentAlerts = [
    {
      id: 1,
      severity: 'critical',
      title: 'SLA Breach Imminent',
      contract: 'CTR-2024-001',
      time: '5 minutes ago',
    },
    {
      id: 2,
      severity: 'high',
      title: 'Response Time Threshold',
      contract: 'CTR-2024-015',
      time: '1 hour ago',
    },
    {
      id: 3,
      severity: 'medium',
      title: 'Contract Renewal Due',
      contract: 'CTR-2024-008',
      time: '3 hours ago',
    },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Contract Intelligence Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Real-time SLA monitoring and compliance tracking
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Description color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Contracts</Typography>
              </Box>
              <Typography variant="h3">{stats.totalContracts}</Typography>
              <Typography variant="body2" color="text.secondary">
                {stats.activeContracts} active
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircle color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">SLA Compliance</Typography>
              </Box>
              <Typography variant="h3">{stats.slaCompliance}%</Typography>
              <LinearProgress
                variant="determinate"
                value={stats.slaCompliance}
                color="success"
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Warning color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Expiring Soon</Typography>
              </Box>
              <Typography variant="h3">{stats.expiringSoon}</Typography>
              <Typography variant="body2" color="text.secondary">
                Within 30 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Error color="error" sx={{ mr: 1 }} />
                <Typography variant="h6">Critical Alerts</Typography>
              </Box>
              <Typography variant="h3">{stats.criticalAlerts}</Typography>
              <Typography variant="body2" color="text.secondary">
                {stats.highRisks} high risks
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Recent Alerts */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Alerts
            </Typography>
            <Box sx={{ mt: 2 }}>
              {recentAlerts.map((alert) => (
                <Alert
                  key={alert.id}
                  severity={getSeverityColor(alert.severity) as any}
                  sx={{ mb: 2 }}
                  icon={<Warning />}
                >
                  <Box>
                    <Typography variant="subtitle2">{alert.title}</Typography>
                    <Typography variant="body2">
                      Contract: {alert.contract} • {alert.time}
                    </Typography>
                  </Box>
                </Alert>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* Compliance Overview */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Compliance Overview
            </Typography>
            <Box sx={{ mt: 3 }}>
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">System Uptime</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    99.95%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={99.95}
                  color="success"
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Response Time</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    98.2%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={98.2}
                  color="success"
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Resolution Time</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    92.5%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={92.5}
                  color="warning"
                />
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Risk Summary */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Risk Summary
            </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={3}>
                <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'error.light', borderRadius: 1 }}>
                  <Typography variant="h4" color="error.dark">
                    2
                  </Typography>
                  <Typography variant="body2" color="error.dark">
                    Critical Risks
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'warning.light', borderRadius: 1 }}>
                  <Typography variant="h4" color="warning.dark">
                    5
                  </Typography>
                  <Typography variant="body2" color="warning.dark">
                    High Risks
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
                  <Typography variant="h4" color="info.dark">
                    8
                  </Typography>
                  <Typography variant="body2" color="info.dark">
                    Medium Risks
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
                  <Typography variant="h4" color="success.dark">
                    12
                  </Typography>
                  <Typography variant="body2" color="success.dark">
                    Low Risks
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;

// Made with Bob
