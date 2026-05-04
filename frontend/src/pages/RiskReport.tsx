import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Alert,
  AlertTitle,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Paper,
  Chip,
  Stack,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  TrendingDown as TrendingDownIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';

interface RiskReportProps {
  sowId: string;
}

interface CriticalAlert {
  _id?: string;
  id?: string;
  title: string;
  message: string;
  severity: string;
  penalty_amount?: number;
  days_until_penalty?: number;
  hours_until_penalty?: number;
  recommended_actions: string[];
}

interface HighRiskObligation {
  id: string;
  description: string;
  deadline?: string;
  risk_level?: string;
  penalty_amount?: number;
  penalty_amount_display?: string;
  days_remaining?: number | null;
  hours_remaining?: number | null;
  progress_percentage?: number;
}

interface ScopeCreepItem {
  id?: string;
  title?: string;
  description?: string;
  potential_revenue?: number;
  cost?: number;
}

interface RiskReportData {
  sow_id: string;
  sow_number: string;
  client_name: string;
  project_name: string;
  overall_risk_score: number;
  overall_risk_level: string;
  critical_alerts: CriticalAlert[];
  high_risk_obligations: HighRiskObligation[];
  scope_creep_detected: ScopeCreepItem[];
  financial_summary: {
    total_penalty_exposure: number;
    immediate_risk: number;
    penalties_avoided_ytd: number;
    scope_creep_value: number;
    potential_recovery: number;
  };
  sla_status: {
    compliant: number;
    at_risk: number;
    breached: number;
    compliance_rate: number;
  };
}

const RiskReport: React.FC<RiskReportProps> = ({ sowId }) => {
  const [riskReport, setRiskReport] = useState<RiskReportData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void fetchRiskReport();
  }, [sowId]);

  const fetchRiskReport = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/sow/${sowId}/risk-report`);
      if (!response.ok) {
        throw new globalThis.Error('Failed to fetch risk report');
      }

      const data = await response.json();
      setRiskReport(data.risk_report ?? null);
    } catch (error) {
      console.error('Failed to fetch risk report:', error);
      setRiskReport(null);
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'critical':
        return '#d32f2f';
      case 'high':
        return '#f57c00';
      case 'medium':
        return '#fbc02d';
      default:
        return '#388e3c';
    }
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2, textAlign: 'center' }}>
          Loading risk report...
        </Typography>
      </Box>
    );
  }

  if (!riskReport) {
    return (
      <Alert severity="error">
        <AlertTitle>Error</AlertTitle>
        Failed to load risk report
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 'bold' }}>
          Risk Report
        </Typography>
        <Typography variant="h5" color="text.secondary">
          {riskReport.project_name} - {riskReport.client_name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          SOW: {riskReport.sow_number}
        </Typography>
      </Box>

      <Card sx={{ mb: 3, bgcolor: getRiskLevelColor(riskReport.overall_risk_level), color: 'white' }}>
        <CardContent>
          <Grid container alignItems="center" spacing={2}>
            <Grid item>
              <ErrorIcon sx={{ fontSize: 60 }} />
            </Grid>
            <Grid item xs>
              <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                Overall Risk Score: {riskReport.overall_risk_score}/100
              </Typography>
              <Typography variant="h6">
                Risk Level: {riskReport.overall_risk_level.toUpperCase()}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, bgcolor: '#ffebee' }}>
            <Typography variant="body2" color="text.secondary">
              Total Penalty Exposure
            </Typography>
            <Typography variant="h4" color="error.main">
              ${riskReport.financial_summary.total_penalty_exposure.toLocaleString()}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, bgcolor: '#fff3e0' }}>
            <Typography variant="body2" color="text.secondary">
              Immediate Risk
            </Typography>
            <Typography variant="h4" color="warning.main">
              ${riskReport.financial_summary.immediate_risk.toLocaleString()}
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
          Critical Alerts
        </Typography>
        {riskReport.critical_alerts.length === 0 ? (
          <Alert severity="success">No critical alerts for this SOW.</Alert>
        ) : (
          <Stack spacing={2}>
            {riskReport.critical_alerts.map((alert) => (
              <Card
                key={alert._id || alert.id || alert.title}
                sx={{ border: '2px solid #d32f2f' }}
              >
                <CardContent>
                  <Alert severity="error" sx={{ mb: 2 }}>
                    <AlertTitle>{alert.title}</AlertTitle>
                    {alert.message}
                  </Alert>

                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                    {typeof alert.penalty_amount === 'number' && (
                      <Chip color="error" label={`Penalty $${alert.penalty_amount.toLocaleString()}`} />
                    )}
                    {typeof alert.hours_until_penalty === 'number' && (
                      <Chip icon={<ScheduleIcon />} color="warning" label={`${alert.hours_until_penalty} hours left`} />
                    )}
                    {typeof alert.days_until_penalty === 'number' && typeof alert.hours_until_penalty !== 'number' && (
                      <Chip icon={<ScheduleIcon />} color="warning" label={`${alert.days_until_penalty} days left`} />
                    )}
                  </Box>

                  {alert.recommended_actions?.length > 0 && (
                    <List dense>
                      {alert.recommended_actions.map((action, index) => (
                        <ListItem key={`${alert.title}-${index}`} sx={{ px: 0 }}>
                          <ListItemText primary={action} />
                        </ListItem>
                      ))}
                    </List>
                  )}
                </CardContent>
              </Card>
            ))}
          </Stack>
        )}
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={7}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
                High-Risk Obligations
              </Typography>
              {riskReport.high_risk_obligations.length === 0 ? (
                <Alert severity="info">No high-risk obligations found.</Alert>
              ) : (
                <Stack spacing={2}>
                  {riskReport.high_risk_obligations.map((obligation) => (
                    <Paper key={obligation.id} variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {obligation.description}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Deadline: {obligation.deadline || 'Not provided'}
                      </Typography>
                      <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {obligation.risk_level && (
                          <Chip
                            size="small"
                            color={obligation.risk_level === 'critical' ? 'error' : 'warning'}
                            label={obligation.risk_level.toUpperCase()}
                          />
                        )}
                        {obligation.penalty_amount_display && (
                          <Chip size="small" color="error" label={`Penalty ${obligation.penalty_amount_display}`} />
                        )}
                        {typeof obligation.days_remaining === 'number' && (
                          <Chip size="small" color="warning" label={`${obligation.days_remaining} days remaining`} />
                        )}
                        {typeof obligation.hours_remaining === 'number' && obligation.hours_remaining < 72 && (
                          <Chip size="small" color="error" label={`${obligation.hours_remaining} hours remaining`} />
                        )}
                      </Box>
                    </Paper>
                  ))}
                </Stack>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={5}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
                Revenue Recovery
              </Typography>
              <Stack spacing={2}>
                <Paper sx={{ p: 2, bgcolor: '#e8f5e9' }}>
                  <Typography variant="body2" color="text.secondary">
                    Penalties Avoided YTD
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    ${riskReport.financial_summary.penalties_avoided_ytd.toLocaleString()}
                  </Typography>
                </Paper>
                <Paper sx={{ p: 2, bgcolor: '#e3f2fd' }}>
                  <Typography variant="body2" color="text.secondary">
                    Scope Creep Recovery Opportunity
                  </Typography>
                  <Typography variant="h4" color="primary.main">
                    ${riskReport.financial_summary.potential_recovery.toLocaleString()}
                  </Typography>
                </Paper>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
            SLA Compliance Status
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={3}>
              <Box sx={{ textAlign: 'center' }}>
                <CheckIcon sx={{ fontSize: 40, color: 'success.main' }} />
                <Typography variant="h4">{riskReport.sla_status.compliant}</Typography>
                <Typography variant="body2">Compliant</Typography>
              </Box>
            </Grid>
            <Grid item xs={3}>
              <Box sx={{ textAlign: 'center' }}>
                <WarningIcon sx={{ fontSize: 40, color: 'warning.main' }} />
                <Typography variant="h4">{riskReport.sla_status.at_risk}</Typography>
                <Typography variant="body2">At Risk</Typography>
              </Box>
            </Grid>
            <Grid item xs={3}>
              <Box sx={{ textAlign: 'center' }}>
                <ErrorIcon sx={{ fontSize: 40, color: 'error.main' }} />
                <Typography variant="h4">{riskReport.sla_status.breached}</Typography>
                <Typography variant="body2">Breached</Typography>
              </Box>
            </Grid>
            <Grid item xs={3}>
              <Box sx={{ textAlign: 'center' }}>
                <TrendingDownIcon sx={{ fontSize: 40, color: 'primary.main' }} />
                <Typography variant="h4">{riskReport.sla_status.compliance_rate}%</Typography>
                <Typography variant="body2">Compliance Rate</Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {riskReport.scope_creep_detected.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
              Scope Creep Findings
            </Typography>
            <Stack spacing={2}>
              {riskReport.scope_creep_detected.map((item, index) => (
                <Alert key={item.id || `${index}`} severity="warning">
                  <Typography variant="subtitle2">{item.title || 'Potential Scope Creep Detected'}</Typography>
                  <Typography variant="body2">{item.description || 'Additional investigation recommended.'}</Typography>
                  {(item.potential_revenue || item.cost) && (
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Estimated commercial value: ${(item.potential_revenue || item.cost || 0).toLocaleString()}
                    </Typography>
                  )}
                </Alert>
              ))}
            </Stack>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default RiskReport;
