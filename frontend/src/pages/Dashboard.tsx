import React, { useEffect, useState } from 'react';
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
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp,
  Warning,
  CheckCircle,
  Error,
  Description,
  Assessment,
} from '@mui/icons-material';

interface DashboardSummary {
  active_sows: number;
  total_obligations: number;
  at_risk_obligations: number;
  critical_alerts: number;
  total_penalty_exposure: number;
  immediate_risk: number;
  penalties_avoided_ytd: number;
  scope_creep_detected: number;
  potential_revenue_recovery: number;
  overall_compliance_rate: number;
  sla_status: {
    compliant: number;
    at_risk: number;
    breached: number;
  };
}

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  // Mock recent alerts data
  const recentAlerts = [
    {
      id: 1,
      severity: 'critical',
      title: 'SLA Breach Imminent',
      contract: 'SOW-2024-ACME-001',
      time: '2 hours ago'
    },
    {
      id: 2,
      severity: 'high',
      title: 'Response Time Approaching Limit',
      contract: 'SOW-2024-ACME-001',
      time: '5 hours ago'
    },
    {
      id: 3,
      severity: 'medium',
      title: 'Scope Creep Detected',
      contract: 'SOW-2024-ACME-001',
      time: '1 day ago'
    }
  ];

  useEffect(() => {
    fetchDashboardSummary();
  }, []);

  const fetchDashboardSummary = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/sow/dashboard/summary');
      const data = await response.json();
      setSummary(data.summary);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch dashboard summary:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!summary) {
    return (
      <Alert severity="error">Failed to load dashboard data</Alert>
    );
  }

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
                <Typography variant="h6">Active SOWs</Typography>
              </Box>
              <Typography variant="h3">{summary.active_sows}</Typography>
              <Typography variant="body2" color="text.secondary">
                {summary.total_obligations} total obligations
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
              <Typography variant="h3">{summary.overall_compliance_rate}%</Typography>
              <LinearProgress
                variant="determinate"
                value={summary.overall_compliance_rate}
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
                <Typography variant="h6">Penalty Exposure</Typography>
              </Box>
              <Typography variant="h3">${(summary.total_penalty_exposure / 1000).toFixed(0)}K</Typography>
              <Typography variant="body2" color="text.secondary">
                ${(summary.immediate_risk / 1000).toFixed(0)}K immediate risk
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
              <Typography variant="h3">{summary.critical_alerts}</Typography>
              <Typography variant="body2" color="text.secondary">
                {summary.at_risk_obligations} at risk
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Financial Summary */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Financial Protection
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Penalties Avoided YTD</Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main">
                    ${(summary.penalties_avoided_ytd / 1000).toFixed(0)}K
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Scope Creep Detected</Typography>
                  <Typography variant="body2" fontWeight="bold" color="warning.main">
                    {summary.scope_creep_detected} items
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Potential Recovery</Typography>
                  <Typography variant="body2" fontWeight="bold" color="primary.main">
                    ${(summary.potential_revenue_recovery / 1000).toFixed(0)}K
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                SLA Status
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Compliant</Typography>
                  <Chip label={summary.sla_status.compliant} color="success" size="small" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">At Risk</Typography>
                  <Chip label={summary.sla_status.at_risk} color="warning" size="small" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Breached</Typography>
                  <Chip label={summary.sla_status.breached} color="error" size="small" />
                </Box>
              </Box>
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
