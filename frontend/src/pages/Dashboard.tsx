import React, { useEffect, useMemo, useState } from 'react';
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
  List,
  ListItem,
  ListItemText,
  Stack,
} from '@mui/material';
import {
  Warning,
  CheckCircle,
  Error as ErrorIcon,
  Description,
  AttachMoney,
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

interface DashboardSow {
  _id: string;
  sow_number: string;
  client_name: string;
  project_name: string;
  review_status?: string;
  analysis_status?: string;
  total_penalty_exposure?: number;
  alerts_count?: number;
  high_risk_count?: number;
  updated_at?: string;
}

interface DashboardListResponse {
  sows?: DashboardSow[];
}

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [sows, setSows] = useState<DashboardSow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [summaryResponse, listResponse] = await Promise.all([
        fetch('http://localhost:8000/api/v1/sow/dashboard/summary'),
        fetch('http://localhost:8000/api/v1/sow/list'),
      ]);

      if (!summaryResponse.ok) {
        throw new globalThis.Error('Failed to fetch dashboard summary');
      }

      const summaryData = await summaryResponse.json();
      setSummary(summaryData.summary);

      if (listResponse.ok) {
        const listData: DashboardListResponse = await listResponse.json();
        setSows(listData.sows ?? []);
      } else {
        setSows([]);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setSummary(null);
      setSows([]);
    } finally {
      setLoading(false);
    }
  };

  const recentSows = useMemo(
    () =>
      [...sows]
        .sort((a, b) => (b.updated_at || '').localeCompare(a.updated_at || ''))
        .slice(0, 5),
    [sows]
  );

  const riskBuckets = useMemo(() => {
    const critical = sows.filter((sow) => (sow.high_risk_count ?? 0) >= 3).length;
    const high = sows.filter((sow) => (sow.high_risk_count ?? 0) > 0 && (sow.high_risk_count ?? 0) < 3).length;
    const medium = sows.filter((sow) => (sow.alerts_count ?? 0) > 0 && (sow.high_risk_count ?? 0) === 0).length;
    const low = Math.max(sows.length - critical - high - medium, 0);

    return { critical, high, medium, low };
  }, [sows]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!summary) {
    return <Alert severity="error">Failed to load dashboard data</Alert>;
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          SOW Risk Intelligence Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Live portfolio view of obligations, financial exposure, risk concentration, and recovery opportunity.
        </Typography>
      </Box>

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
                <AttachMoney color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Penalty Exposure</Typography>
              </Box>
              <Typography variant="h4">${summary.total_penalty_exposure.toLocaleString()}</Typography>
              <Typography variant="body2" color="text.secondary">
                ${summary.immediate_risk.toLocaleString()} immediate risk
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <ErrorIcon color="error" sx={{ mr: 1 }} />
                <Typography variant="h6">Critical Alerts</Typography>
              </Box>
              <Typography variant="h3">{summary.critical_alerts}</Typography>
              <Typography variant="body2" color="text.secondary">
                {summary.at_risk_obligations} obligations at risk
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Financial Protection
              </Typography>
              <Stack spacing={1.5} sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Penalties Avoided YTD</Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main">
                    ${summary.penalties_avoided_ytd.toLocaleString()}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Scope Creep Detected</Typography>
                  <Typography variant="body2" fontWeight="bold" color="warning.main">
                    {summary.scope_creep_detected} items
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Potential Recovery</Typography>
                  <Typography variant="body2" fontWeight="bold" color="primary.main">
                    ${summary.potential_revenue_recovery.toLocaleString()}
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                SLA Status
              </Typography>
              <Stack spacing={1.5} sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Compliant</Typography>
                  <Chip label={summary.sla_status.compliant} color="success" size="small" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">At Risk</Typography>
                  <Chip label={summary.sla_status.at_risk} color="warning" size="small" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Breached</Typography>
                  <Chip label={summary.sla_status.breached} color="error" size="small" />
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Recently Updated SOWs
            </Typography>
            {recentSows.length === 0 ? (
              <Alert severity="info">No SOWs available yet.</Alert>
            ) : (
              <List>
                {recentSows.map((sow) => (
                  <ListItem key={sow._id} divider>
                    <ListItemText
                      primary={sow.project_name}
                      secondary={`${sow.client_name} · ${sow.sow_number} · ${sow.high_risk_count ?? 0} high-risk obligations · ${sow.alerts_count ?? 0} alerts`}
                    />
                    <Chip
                      size="small"
                      label={sow.review_status || 'pending'}
                      color={sow.review_status === 'approved' ? 'success' : 'default'}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Portfolio Risk Mix
            </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'error.light', borderRadius: 1 }}>
                  <Typography variant="h4" color="error.dark">
                    {riskBuckets.critical}
                  </Typography>
                  <Typography variant="body2" color="error.dark">
                    Critical
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'warning.light', borderRadius: 1 }}>
                  <Typography variant="h4" color="warning.dark">
                    {riskBuckets.high}
                  </Typography>
                  <Typography variant="body2" color="warning.dark">
                    High
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
                  <Typography variant="h4" color="info.dark">
                    {riskBuckets.medium}
                  </Typography>
                  <Typography variant="body2" color="info.dark">
                    Medium
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
                  <Typography variant="h4" color="success.dark">
                    {riskBuckets.low}
                  </Typography>
                  <Typography variant="body2" color="success.dark">
                    Low
                  </Typography>
                </Box>
              </Grid>
            </Grid>

            <Alert severity="warning" icon={<Warning />} sx={{ mt: 3 }}>
              <Typography variant="subtitle2">Immediate portfolio focus</Typography>
              <Typography variant="body2">
                {summary.critical_alerts} critical alerts and ${summary.immediate_risk.toLocaleString()} in immediate exposure require human review.
              </Typography>
            </Alert>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;

// Made with Bob
