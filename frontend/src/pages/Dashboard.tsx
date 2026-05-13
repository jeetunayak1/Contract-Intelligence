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
  Stack,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Avatar,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Warning,
  CheckCircle,
  Error as ErrorIcon,
  Description,
  SmartToy,
  Event,
  EditNote,
  CloudUpload,
  TrendingUp,
  Shield,
  Psychology,
  AutoGraph,
  InfoOutlined,
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
  active_agent?: string;
  updated_at?: string;
}

interface DashboardListResponse {
  sows?: DashboardSow[];
}

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [sows, setSows] = useState<DashboardSow[]>([]);
  const [loading, setLoading] = useState(true);

  // Upload state
  const [uploadOpen, setUploadOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [sowNumber, setSowNumber] = useState('');
  const [clientName, setClientName] = useState('');
  const [projectName, setProjectName] = useState('');

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

  const handleUploadSubmit = async () => {
    if (!file || !sowNumber || !clientName || !projectName) {
      alert('Please fill all fields and select a file.');
      return;
    }
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('sow_number', sowNumber);
    formData.append('client_name', clientName);
    formData.append('project_name', projectName);

    try {
      const response = await fetch('http://localhost:8000/api/v1/sow/upload', {
        method: 'POST',
        body: formData,
      });
      if (response.ok) {
        alert('SOW Uploaded Successfully!');
        setUploadOpen(false);
        setFile(null);
        setSowNumber('');
        setClientName('');
        setProjectName('');
        fetchDashboardData();
      } else {
        const error = await response.json();
        alert(`Failed to upload: ${error.detail}`);
      }
    } catch (err) {
      alert('Failed to upload SOW.');
    } finally {
      setUploading(false);
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
      {/* Top Section: Title & Agent Status */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 5 }}>
        <Box>
          <Typography variant="h3" sx={{ fontWeight: 800, mb: 0.5 }}>
            Executive <span className="gradient-text">Command Center</span>
          </Typography>
          <Typography variant="body1" color="text.secondary">
            De-risking the SOW portfolio and optimizing outcome-based revenue conversion.
          </Typography>
        </Box>
        <Paper className="glass-card" sx={{ p: 1.5, display: 'flex', alignItems: 'center', gap: 2, px: 3 }}>
          <Box sx={{ position: 'relative' }}>
            <Avatar sx={{ bgcolor: 'rgba(0, 230, 118, 0.1)', color: '#00e676', border: '1px solid rgba(0, 230, 118, 0.3)' }}>
              <Psychology />
            </Avatar>
            <Box className="agent-pulse" sx={{ position: 'absolute', bottom: 0, right: 0, width: 12, height: 12, bgcolor: '#00e676', border: '2px solid #151518' }} />
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 800, textTransform: 'uppercase', letterSpacing: 1 }}>
              Agent Status: Active
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {recentSows.length > 0 && recentSows[0].active_agent 
                ? `${recentSows[0].active_agent} is optimizing revenue...` 
                : 'Strategist Agent scanning for leakage...'}
            </Typography>
          </Box>
        </Paper>
      </Box>

      {/* Main KPI Row */}
      <Grid container spacing={3} sx={{ mb: 5 }}>
        <Grid item xs={12} md={4}>
          <Card className="glass-card revenue-uplift" sx={{ position: 'relative', overflow: 'hidden' }}>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="subtitle2" sx={{ color: 'primary.main', fontWeight: 700, textTransform: 'uppercase' }}>
                  Revenue Uplift Potential
                </Typography>
                <TrendingUp color="primary" />
              </Box>
              <Typography variant="h2" sx={{ fontWeight: 800, mb: 1 }}>
                ${summary.potential_revenue_recovery.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Projected annual margin lift through outcome-based conversion.
              </Typography>
              <Box sx={{ mt: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
                <AutoGraph sx={{ fontSize: 16, color: 'primary.main' }} />
                <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 700 }}>
                  +24.5% vs Last Quarter
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card className="glass-card risk-shield">
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="subtitle2" sx={{ color: 'secondary.main', fontWeight: 700, textTransform: 'uppercase' }}>
                  Risk Shield Protection
                </Typography>
                <Shield color="secondary" />
              </Box>
              <Typography variant="h2" sx={{ fontWeight: 800, mb: 1 }}>
                ${summary.total_penalty_exposure.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Potential penalty exposure neutralized across {summary.active_sows} active SOWs.
              </Typography>
              <Box sx={{ mt: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Warning sx={{ fontSize: 16, color: 'secondary.main' }} />
                <Typography variant="caption" sx={{ color: 'secondary.main', fontWeight: 700 }}>
                  {summary.critical_alerts} High-Risk Items Flagged
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card className="glass-card" sx={{ p: 1 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 3, color: 'text.secondary', textTransform: 'uppercase' }}>
                Portfolio Health Index
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', height: 120 }}>
                <CircularProgress 
                  variant="determinate" 
                  value={summary.overall_compliance_rate} 
                  size={120} 
                  thickness={5} 
                  sx={{ color: 'primary.main' }} 
                />
                <Box sx={{ position: 'absolute', textAlign: 'center' }}>
                  <Typography variant="h4" sx={{ fontWeight: 800 }}>{summary.overall_compliance_rate}%</Typography>
                  <Typography variant="caption">Compliant</Typography>
                </Box>
              </Box>
              <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-around' }}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>{summary.sla_status.compliant}</Typography>
                  <Typography variant="caption" color="text.secondary">Safe</Typography>
                </Box>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: 'warning.main' }}>{summary.sla_status.at_risk}</Typography>
                  <Typography variant="caption" color="text.secondary">At Risk</Typography>
                </Box>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: 'error.main' }}>{summary.sla_status.breached}</Typography>
                  <Typography variant="caption" color="text.secondary">Breached</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={4} sx={{ mb: 5 }}>
        {/* Risk Heatmap (Visual Placeholder) */}
        <Grid item xs={12} md={8}>
          <Card className="glass-card">
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 800 }}>Portfolio <span className="gradient-text">Risk Heatmap</span></Typography>
                  <Typography variant="body2" color="text.secondary">Concentration of financial exposure across client segments.</Typography>
                </Box>
                <Tooltip title="Heatmap shows risk concentration vs revenue value">
                  <IconButton size="small"><InfoOutlined /></IconButton>
                </Tooltip>
              </Box>
              
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 2, height: 300 }}>
                {[...Array(12)].map((_, i) => (
                  <Box 
                    key={i} 
                    sx={{ 
                      borderRadius: 2, 
                      bgcolor: i % 5 === 0 ? 'rgba(244, 143, 177, 0.3)' : i % 3 === 0 ? 'rgba(255, 152, 0, 0.2)' : 'rgba(0, 230, 118, 0.1)',
                      border: '1px solid rgba(255,255,255,0.05)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 0.2s',
                      '&:hover': { transform: 'scale(1.05)', border: '1px solid rgba(255,255,255,0.2)' }
                    }}
                  >
                    <Typography variant="caption" sx={{ fontWeight: 800, opacity: 0.7 }}>
                      {['Finance', 'Healthcare', 'Retail', 'Tech', 'Energy', 'Gov', 'Media', 'Education'][i % 8]}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card className="glass-card" sx={{ height: '100%' }}>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6" sx={{ fontWeight: 800 }}>Transformation <span className="gradient-text">Queue</span></Typography>
                <Button 
                  size="small" 
                  variant="outlined" 
                  startIcon={<CloudUpload />} 
                  onClick={() => setUploadOpen(true)}
                  sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700 }}
                >
                  Upload SOW
                </Button>
              </Box>
              
              <Stack spacing={2}>
                {recentSows.map((sow) => (
                  <Box 
                    key={sow._id} 
                    sx={{ 
                      p: 2, 
                      borderRadius: 3, 
                      bgcolor: 'rgba(255,255,255,0.02)', 
                      border: '1px solid rgba(255,255,255,0.05)',
                      '&:hover': { bgcolor: 'rgba(255,255,255,0.05)' }
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 800 }}>{sow.project_name}</Typography>
                      <Chip 
                        size="small" 
                        label={sow.review_status || 'analyzing'} 
                        sx={{ fontSize: '0.65rem', fontWeight: 900, textTransform: 'uppercase', bgcolor: sow.review_status === 'approved' ? 'primary.dark' : 'rgba(255,255,255,0.1)' }} 
                      />
                    </Box>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                      {sow.client_name} · ${sow.total_penalty_exposure?.toLocaleString() || 0} at risk
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Chip label="Strategist Active" size="small" sx={{ fontSize: '0.6rem', height: 18, bgcolor: 'rgba(0, 230, 118, 0.1)', color: 'primary.main', border: '1px solid rgba(0, 230, 118, 0.3)' }} />
                    </Box>
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Resolution & Simulation Row */}
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Card className="glass-card">
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h6" sx={{ fontWeight: 800, mb: 3 }}>
                Profitability <span className="gradient-text">Simulator</span>
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'flex-end', height: 200, mb: 4, gap: 4 }}>
                <Box sx={{ flex: 1, textAlign: 'center' }}>
                  <Typography variant="caption" color="error.main" sx={{ fontWeight: 800 }}>${(summary.active_sows * 15000).toLocaleString()}</Typography>
                  <Box sx={{ height: 120, bgcolor: 'error.main', opacity: 0.6, borderRadius: 2, mt: 1, position: 'relative' }}>
                     <Box sx={{ position: 'absolute', top: -25, left: 0, right: 0 }}><Typography variant="caption" sx={{ fontWeight: 700 }}>AS-IS (T&M)</Typography></Box>
                  </Box>
                </Box>
                <Box sx={{ flex: 1, textAlign: 'center' }}>
                  <Typography variant="caption" color="primary.main" sx={{ fontWeight: 800 }}>${(summary.active_sows * 15000 + summary.potential_revenue_recovery).toLocaleString()}</Typography>
                  <Box sx={{ height: 180, bgcolor: 'primary.main', opacity: 0.8, borderRadius: 2, mt: 1, position: 'relative' }}>
                     <Box sx={{ position: 'absolute', top: -25, left: 0, right: 0 }}><Typography variant="caption" sx={{ fontWeight: 700 }}>TARGET (OUTCOME)</Typography></Box>
                  </Box>
                </Box>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Conversion to Outcome-Based models eliminates headcount billing caps and rewards high-efficiency delivery teams.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card className="glass-card">
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h6" sx={{ fontWeight: 800, mb: 3 }}>
                Agent: <span className="gradient-text">Strategist Insights</span>
              </Typography>
              <Stack spacing={2}>
                {recentSows.filter(s => (s.high_risk_count ?? 0) > 0).slice(0, 2).map(sow => (
                  <Box key={sow._id} sx={{ p: 2, border: '1px solid rgba(244, 143, 177, 0.2)', borderRadius: 2, bgcolor: 'rgba(244, 143, 177, 0.05)' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 800 }}>{sow.project_name}</Typography>
                      <Chip label="High Leakage" size="small" color="error" sx={{ height: 18, fontSize: '0.6rem', fontWeight: 900 }} />
                    </Box>
                    <Typography variant="body2" sx={{ mb: 2, fontSize: '0.85rem' }}>Suggesting conversion to milestone-based billing to recapture ${sow.total_penalty_exposure?.toLocaleString()} in exposure.</Typography>
                    <Stack direction="row" spacing={1}>
                      <Button size="small" variant="contained" sx={{ textTransform: 'none', borderRadius: 2, fontWeight: 700 }}>Resolve via Rewrite</Button>
                      <Button size="small" variant="outlined" sx={{ textTransform: 'none', borderRadius: 2, fontWeight: 700 }}>Schedule Align</Button>
                    </Stack>
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Upload Dialog */}
      <Dialog open={uploadOpen} onClose={() => !uploading && setUploadOpen(false)} maxWidth="sm" fullWidth PaperProps={{ className: 'glass-card' }}>
        <DialogTitle sx={{ fontWeight: 800 }}>Upload <span className="gradient-text">Statement of Work</span></DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField label="SOW Number" fullWidth required value={sowNumber} onChange={(e) => setSowNumber(e.target.value)} />
            <TextField label="Client Name" fullWidth required value={clientName} onChange={(e) => setClientName(e.target.value)} />
            <TextField label="Project Name" fullWidth required value={projectName} onChange={(e) => setProjectName(e.target.value)} />
            <Box sx={{ p: 3, border: '2px dashed rgba(255,255,255,0.1)', borderRadius: 3, textAlign: 'center' }}>
              <CloudUpload sx={{ fontSize: 40, color: 'primary.main', mb: 1, opacity: 0.5 }} />
              <Typography variant="body2" gutterBottom sx={{ fontWeight: 600 }}>Drag & drop document or click to browse</Typography>
              <Typography variant="caption" color="text.secondary">PDF, DOCX, or TXT supported</Typography>
              <input type="file" accept=".pdf,.docx,.txt" onChange={(e) => setFile(e.target.files?.[0] || null)} style={{ marginTop: 16 }} />
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setUploadOpen(false)} disabled={uploading} sx={{ fontWeight: 700 }}>Cancel</Button>
          <Button variant="contained" onClick={handleUploadSubmit} disabled={uploading} sx={{ fontWeight: 700, borderRadius: 2, px: 4 }}>
            {uploading ? <CircularProgress size={24} color="inherit" /> : 'Begin Transformation'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Dashboard;

// Made with Bob
