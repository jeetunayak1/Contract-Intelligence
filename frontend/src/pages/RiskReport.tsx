import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Alert,
  AlertTitle,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Button,
  Divider,
  Paper
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  TrendingDown as TrendingDownIcon,
  AttachMoney as MoneyIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';

interface RiskReportProps {
  sowId: string;
}

interface CriticalAlert {
  id: string;
  title: string;
  message: string;
  severity: string;
  penalty_amount: number;
  days_until_penalty: number;
  hours_until_penalty: number;
  obligation: {
    id: string;
    description: string;
    deadline: string;
    current_progress: number;
    blockers: string[];
  };
  recommended_actions: string[];
}

interface RiskReportData {
  sow_id: string;
  sow_number: string;
  client_name: string;
  project_name: string;
  overall_risk_score: number;
  overall_risk_level: string;
  critical_alerts: CriticalAlert[];
  high_risk_obligations: any[];
  scope_creep_detected: any[];
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
    fetchRiskReport();
  }, [sowId]);

  const fetchRiskReport = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/sow/${sowId}/risk-report`);
      const data = await response.json();
      setRiskReport(data.risk_report);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch risk report:', error);
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      default: return 'success';
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'critical': return '#d32f2f';
      case 'high': return '#f57c00';
      case 'medium': return '#fbc02d';
      default: return '#388e3c';
    }
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2, textAlign: 'center' }}>
          Loading Risk Report...
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
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 'bold' }}>
          🚨 Risk Report
        </Typography>
        <Typography variant="h5" color="text.secondary">
          {riskReport.project_name} - {riskReport.client_name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          SOW: {riskReport.sow_number}
        </Typography>
      </Box>

      {/* Overall Risk Score */}
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

      {/* Critical Alerts - THE WOW MOMENT */}
      {riskReport.critical_alerts.map((alert) => (
        <Card 
          key={alert.id} 
          sx={{ 
            mb: 3, 
            border: '3px solid #d32f2f',
            animation: 'pulse 2s infinite'
          }}
        >
          <CardContent>
            <Alert severity="error" sx={{ mb: 2 }}>
              <AlertTitle sx={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                {alert.title}
              </AlertTitle>
              <Typography variant="h5" sx={{ mt: 2, mb: 2 }}>
                {alert.message}
              </Typography>
            </Alert>

            {/* Countdown Timer */}
            <Paper sx={{ p: 3, mb: 2, bgcolor: '#ffebee' }}>
              <Grid container spacing={3} alignItems="center">
                <Grid item>
                  <ScheduleIcon sx={{ fontSize: 50, color: '#d32f2f' }} />
                </Grid>
                <Grid item xs>
                  <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#d32f2f' }}>
                    {alert.hours_until_penalty} Hours
                  </Typography>
                  <Typography variant="h6" color="text.secondary">
                    Until ${alert.penalty_amount.toLocaleString()}/day penalty
                  </Typography>
                </Grid>
              </Grid>
            </Paper>

            {/* Current Status */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                📊 Current Status
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography>Progress</Typography>
                  <Typography fontWeight="bold">
                    {alert.obligation.current_progress}%
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={alert.obligation.current_progress}
                  sx={{ height: 10, borderRadius: 5 }}
                  color={alert.obligation.current_progress > 80 ? 'success' : 'error'}
                />
              </Box>
            </Box>

            {/* Blockers */}
            {alert.obligation.blockers.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom color="error">
                  🔴 Blockers ({alert.obligation.blockers.length})
                </Typography>
                <List>
                  {alert.obligation.blockers.map((blocker, index) => (
                    <ListItem key={index} sx={{ bgcolor: '#ffebee', mb: 1, borderRadius: 1 }}>
                      <ListItemText primary={blocker} />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {/* Recommended Actions */}
            <Box>
              <Typography variant="h6" gutterBottom>
                💡 Recommended Actions
              </Typography>
              <List>
                {alert.recommended_actions.map((action, index) => (
                  <ListItem key={index}>
                    <Button
                      variant="contained"
                      color="primary"
                      fullWidth
                      sx={{ justifyContent: 'flex-start', textAlign: 'left' }}
                    >
                      {action}
                    </Button>
                  </ListItem>
                ))}
              </List>
            </Box>
          </CardContent>
        </Card>
      ))}

      {/* Financial Summary */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
            💰 Financial Summary
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, bgcolor: '#ffebee' }}>
                <Typography variant="body2" color="text.secondary">
                  Total Penalty Exposure
                </Typography>
                <Typography variant="h4" color="error">
                  ${riskReport.financial_summary.total_penalty_exposure.toLocaleString()}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, bgcolor: '#fff3e0' }}>
                <Typography variant="body2" color="text.secondary">
                  Immediate Risk
                </Typography>
                <Typography variant="h4" color="warning.main">
                  ${riskReport.financial_summary.immediate_risk.toLocaleString()}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, bgcolor: '#e8f5e9' }}>
                <Typography variant="body2" color="text.secondary">
                  Penalties Avoided YTD
                </Typography>
                <Typography variant="h4" color="success.main">
                  ${riskReport.financial_summary.penalties_avoided_ytd.toLocaleString()}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, bgcolor: '#e3f2fd' }}>
                <Typography variant="body2" color="text.secondary">
                  Potential Recovery (Scope Creep)
                </Typography>
                <Typography variant="h4" color="primary">
                  ${riskReport.financial_summary.potential_recovery.toLocaleString()}
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* SLA Status */}
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
            📈 SLA Compliance Status
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

      {/* Pulse Animation */}
      <style>
        {`
          @keyframes pulse {
            0%, 100% {
              box-shadow: 0 0 0 0 rgba(211, 47, 47, 0.7);
            }
            50% {
              box-shadow: 0 0 0 10px rgba(211, 47, 47, 0);
            }
          }
        `}
      </style>
    </Box>
  );
};

export default RiskReport;

// Made with Bob
