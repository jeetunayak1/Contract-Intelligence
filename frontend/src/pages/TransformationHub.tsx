import React, { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Divider,
  Grid,
  List,
  ListItem,
  ListItemText,
  Paper,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
  Avatar,
  LinearProgress,
} from '@mui/material';
import {
  Warning,
  SmartToy,
  AutoFixHigh,
  Security,
  TrendingUp,
  ReceiptLong,
  TrackChanges,
  History,
  CloudUpload,
  Psychology,
  DoneAll,
  GitHub,
  Download,
  CalendarMonth,
  AttachMoney,
  Gavel,
  TipsAndUpdates,
} from '@mui/icons-material';
import { toast } from 'react-toastify';

interface SOWListItem {
  _id: string;
  sow_number: string;
  client_name: string;
  project_name: string;
  status: string;
  review_status?: string;
  analysis_status?: string;
  active_agent?: string;
  updated_at?: string;
  risk_assessment?: {
    risk_score?: number;
    risk_level?: string;
    total_penalty_exposure?: number;
  };
  alerts?: ReviewAlert[];
  action_items?: ActionItem[];
}

interface ReviewAlert {
  _id?: string;
  id?: string;
  title: string;
  message: string;
  severity?: string;
  recommended_actions?: string[];
  penalty_amount?: number;
  days_until_penalty?: number;
  hours_until_penalty?: number;
}

interface ActionItemNumericRisk {
  penalty_amount?: number;
  penalty_amount_display?: string;
  days_remaining?: number | null;
  hours_remaining?: number | null;
  days_until_penalty?: number | null;
  hours_until_penalty?: number | null;
  potential_revenue?: number;
  potential_revenue_display?: string;
  risk_score?: number;
  total_penalty_exposure?: number;
  total_penalty_exposure_display?: string;
}

interface ActionItem {
    id: string;
    title: string;
    description: string;
    priority?: string;
    approval_state?: string;
    execution_state?: string;
    recommended_owner?: string;
    recommended_actions?: string[];
    action_type?: string;
    execution_targets?: string[];
    workflow_stage?: 'pre_acceptance' | 'post_approval' | string;
    cta_label?: string;
    sla_reference?: string;
    numeric_risk?: ActionItemNumericRisk;
    github_issue?: {
      issue_url?: string;
      title?: string;
      repository?: string;
      workflow_stage?: string;
      sla_reference?: string;
    };
    calendar_event?: {
      title?: string;
      provider?: string;
      start_time?: string;
      calendar_name?: string;
      workflow_stage?: string;
      sla_reference?: string;
    };
}

interface TimelineEvent {
  id: string;
  event_type: string;
  title: string;
  timestamp: string;
  decision?: string;
  notes?: string;
}

interface SOWDetail extends SOWListItem {
  description?: string;
  obligations?: Array<{
    id: string;
    description: string;
    deadline?: string;
    risk_level?: string;
    status?: string;
  }>;
  vague_clauses?: Array<{
    id: string;
    clause_text: string;
    risk_description?: string;
    severity?: string;
    recommendation?: string;
  }>;
  scope_creep_items?: Array<{
    id?: string;
    title?: string;
    description?: string;
    status?: string;
    financial_impact?: number;
  }>;
  agent_summary?: {
    ingestion_findings?: Record<string, number>;
    risk_findings?: Record<string, string | number>;
    executive_recommendations?: Record<string, number>;
  };
  transformation_plan?: {
    revenue_leakage_score?: number;
    proposed_outcome_milestones?: Array<{
      milestone_name?: string;
      value?: number;
    }>;
    compensation_rewrite?: {
      diff_format?: string;
      new_text?: string;
    };
    risk_profile?: string[];
  };
  approval_history?: Array<{
    decided_at: string;
    decision: string;
    notes?: string;
    approved_alert_ids?: string[];
    approved_action_ids?: string[];
  }>;
  integration_execution?: {
    pre_acceptance?: {
      github?: {
        executed?: boolean;
        issues_created?: Array<{
          title?: string;
          issue_url?: string;
          created?: boolean;
          repository?: string;
          sla_reference?: string;
        }>;
        executed_at?: string;
        message?: string;
      };
      calendar?: {
        executed?: boolean;
        meetings_created?: Array<{
          title?: string;
          provider?: string;
          start_time?: string;
          scheduled?: boolean;
          calendar_name?: string;
          sla_reference?: string;
        }>;
        executed_at?: string;
      };
    };
    post_approval?: {
      github?: {
        executed?: boolean;
        issues_created?: Array<{
          title?: string;
          issue_url?: string;
          created?: boolean;
          repository?: string;
          sla_reference?: string;
        }>;
        executed_at?: string;
      };
      calendar?: {
        executed?: boolean;
        meetings_created?: Array<{
          title?: string;
          provider?: string;
          start_time?: string;
          scheduled?: boolean;
          calendar_name?: string;
          sla_reference?: string;
        }>;
        executed_at?: string;
      };
      teams?: {
        executed?: boolean;
        channels_created?: Array<{
          channel_name?: string;
          created?: boolean;
        }>;
        executed_at?: string;
      };
    };
  };
  timeline_events?: TimelineEvent[];
}

interface DashboardSummaryResponse {
  summary: {
    active_sows: number;
    total_obligations: number;
    at_risk_obligations: number;
    critical_alerts: number;
    total_penalty_exposure: number;
    immediate_risk: number;
  };
}

const API_BASE = 'http://localhost:8000/api/v1/sow';

const TransformationHub: React.FC = () => {
  const [tab, setTab] = useState(0);
  const [sows, setSows] = useState<SOWListItem[]>([]);
  const [selectedSowId, setSelectedSowId] = useState<string>('');
  const [selectedSow, setSelectedSow] = useState<SOWDetail | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [dashboardSummary, setDashboardSummary] = useState<DashboardSummaryResponse['summary'] | null>(null);

  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [approving, setApproving] = useState(false);
  const [executing, setExecuting] = useState(false);

  const [uploadForm, setUploadForm] = useState({
    sowNumber: '',
    clientName: '',
    projectName: '',
    file: null as File | null,
  });
  const [approvalNotes, setApprovalNotes] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStep, setUploadStep] = useState('');

  const selectedSowAlerts = selectedSow?.alerts ?? [];
  const selectedActionItems = selectedSow?.action_items ?? [];
  const selectedApprovedActionIds = useMemo(
    () => selectedActionItems.filter((item) => item.approval_state === 'approved').map((item) => item.id),
    [selectedActionItems]
  );

  useEffect(() => {
    void loadSows();
    void loadDashboardSummary();
  }, []);

  useEffect(() => {
    if (selectedSowId) {
      void loadSowDetail(selectedSowId);
      void loadTimeline(selectedSowId);
    }
  }, [selectedSowId]);

  const loadSows = async () => {
    setLoadingList(true);
    try {
      const response = await fetch(`${API_BASE}/list`);
      if (!response.ok) {
        throw new Error('Failed to load SOW list');
      }
      const data = await response.json();
      const items: SOWListItem[] = data.sows ?? [];
      setSows(items);
      if (!selectedSowId && items.length > 0) {
        setSelectedSowId(items[0]._id);
      }
    } catch (error) {
      console.error(error);
      toast.error('Failed to load saved SOWs');
    } finally {
      setLoadingList(false);
    }
  };

  const loadDashboardSummary = async () => {
    try {
      const response = await fetch(`${API_BASE}/dashboard/summary`);
      if (!response.ok) {
        throw new Error('Failed to load dashboard summary');
      }
      const data: DashboardSummaryResponse = await response.json();
      setDashboardSummary(data.summary);
    } catch (error) {
      console.error(error);
    }
  };

  const loadSowDetail = async (sowId: string) => {
    setLoadingDetail(true);
    try {
      const response = await fetch(`${API_BASE}/${sowId}`);
      if (!response.ok) {
        throw new Error('Failed to load SOW detail');
      }
      const data = await response.json();
      setSelectedSow(data.sow ?? null);
    } catch (error) {
      console.error(error);
      toast.error('Failed to load SOW review package');
    } finally {
      setLoadingDetail(false);
    }
  };

  const loadTimeline = async (sowId: string) => {
    try {
      const response = await fetch(`${API_BASE}/${sowId}/timeline`);
      if (!response.ok) {
        throw new Error('Failed to load timeline');
      }
      const data = await response.json();
      setTimeline(data.timeline ?? []);
    } catch (error) {
      console.error(error);
      setTimeline([]);
    }
  };

  const handleUploadChange = (field: 'sowNumber' | 'clientName' | 'projectName', value: string) => {
    setUploadForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setUploadForm((prev) => ({ ...prev, file }));
  };

  const handleUpload = async (directFile?: File, directProject?: string) => {
    const file = directFile || uploadForm.file;
    const project = directProject || uploadForm.projectName;
    const client = directFile ? 'Auto-Detected' : uploadForm.clientName;
    const sowNum = directFile ? 'Pending' : uploadForm.sowNumber;

    if (!file || !sowNum || !client || !project) {
      toast.error('Provide SOW number, client, project, and a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('sow_number', sowNum);
    formData.append('client_name', client);
    formData.append('project_name', project);

    setUploading(true);
    setUploadProgress(10);
    setUploadStep('Agent Recon: Parsing document structure...');
    
    try {
      // Simulate steps for better UX since it's a single request
      const simulateSteps = async () => {
        await new Promise(r => setTimeout(r, 1500));
        setUploadProgress(30);
        setUploadStep('Agent Mitigator: Scanning for SLA penalties & liability gaps...');
        await new Promise(r => setTimeout(r, 2000));
        setUploadProgress(60);
        setUploadStep('Agent Strategist: Identifying revenue leakage & outcome opportunities...');
        await new Promise(r => setTimeout(r, 1500));
        setUploadProgress(85);
        setUploadStep('Agent Drafter: Generating optimized contract transformation...');
      };

      const uploadPromise = fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });

      void simulateSteps();
      
      const response = await uploadPromise;

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || 'Upload failed');
      }

      const data = await response.json();
      const newSowId = data.sow?._id as string | undefined;

      toast.success('SOW uploaded and analyzed successfully');
      setUploadForm({
        sowNumber: '',
        clientName: '',
        projectName: '',
        file: null,
      });

      await loadSows();
      await loadDashboardSummary();

      if (newSowId) {
        setSelectedSowId(newSowId);
        setTab(1);
      }
    } catch (error) {
      console.error(error);
      toast.error(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setUploading(false);
      setUploadProgress(0);
      setUploadStep('');
    }
  };

  const handleReviewDecision = async (decision: 'approved' | 'rejected' | 'clear') => {
    if (!selectedSowId) {
      return;
    }

    const approvedAlertIds = decision === 'approved'
      ? selectedSowAlerts
          .map((alert) => alert._id || alert.id)
          .filter((value): value is string => Boolean(value))
      : [];

    const approvedActionIds = decision === 'approved'
      ? selectedActionItems.map((item) => item.id)
      : [];

    setApproving(true);
    try {
      const response = await fetch(`${API_BASE}/${selectedSowId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision,
          notes: approvalNotes,
          approved_alert_ids: approvedAlertIds,
          approved_action_ids: approvedActionIds,
        }),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || 'Review decision failed');
      }

      if (decision === 'approved') {
        toast.success('SOW approved and ready for execution');
      } else if (decision === 'rejected') {
        toast.success('SOW rejected');
      } else {
        toast.success('SOW review cleared');
      }

      await loadSowDetail(selectedSowId);
      await loadTimeline(selectedSowId);
      await loadDashboardSummary();
      await loadSows();
    } catch (error) {
      console.error(error);
      toast.error(error instanceof Error ? error.message : 'Review decision failed');
    } finally {
      setApproving(false);
    }
  };

  const handleExecuteActions = async (actionItemIds?: string[], workflowStage?: string) => {
    if (!selectedSowId) {
      return;
    }

    setExecuting(true);
    try {
      const response = await fetch(`${API_BASE}/${selectedSowId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action_item_ids: actionItemIds && actionItemIds.length > 0 ? actionItemIds : selectedApprovedActionIds,
          workflow_stage: workflowStage,
        }),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || 'Action execution failed');
      }

      const data = await response.json();
      const githubCount = Array.isArray(data.issues_created) ? data.issues_created.length : 0;
      const meetingCount = Array.isArray(data.meetings_created) ? data.meetings_created.length : 0;
      const teamsCount = Array.isArray(data.teams_channels_created) ? data.teams_channels_created.length : 0;
      toast.success(`Executed ${githubCount} GitHub items, ${meetingCount} meetings, and ${teamsCount} Teams channels`);
      await loadSowDetail(selectedSowId);
      await loadTimeline(selectedSowId);
      await loadDashboardSummary();
      await loadSows();
    } catch (error) {
      console.error(error);
      toast.error(error instanceof Error ? error.message : 'Action execution failed');
    } finally {
      setExecuting(false);
    }
  };

  const renderRiskChip = (level?: string) => {
    const l = (level || 'medium').toLowerCase();
    return (
      <Chip
        size="small"
        label={l.toUpperCase()}
        sx={{
          fontWeight: 900,
          fontSize: '0.65rem',
          height: 20,
          borderRadius: 1,
          bgcolor: 
            l === 'critical' ? 'rgba(255, 23, 68, 0.15)' : 
            l === 'high' ? 'rgba(255, 152, 0, 0.15)' : 
            'rgba(0, 230, 118, 0.15)',
          color: 
            l === 'critical' ? '#ff1744' : 
            l === 'high' ? '#ff9800' : 
            '#00e676',
          border: `1px solid ${
            l === 'critical' ? 'rgba(255, 23, 68, 0.3)' : 
            l === 'high' ? 'rgba(255, 152, 0, 0.3)' : 
            'rgba(0, 230, 118, 0.3)'
          }`,
        }}
      />
    );
  };

  const getFinancialImpact = (item: ActionItem) => {
    if (item.numeric_risk?.total_penalty_exposure) return { label: 'Penalty Risk', value: item.numeric_risk.total_penalty_exposure_display, color: 'secondary.main' };
    if (item.numeric_risk?.penalty_amount) return { label: 'Penalty Risk', value: item.numeric_risk.penalty_amount_display, color: 'secondary.main' };
    if (item.numeric_risk?.potential_revenue) return { label: 'Revenue Leakage', value: item.numeric_risk.potential_revenue_display, color: 'primary.main' };
    return null;
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4, position: 'relative' }}>
      {/* Agentic Processing Overlay */}
      {uploading && (
        <Box 
          sx={{ 
            position: 'fixed', 
            top: 0, left: 0, right: 0, bottom: 0, 
            bgcolor: 'rgba(10, 10, 12, 0.9)', 
            zIndex: 9999, 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center',
            backdropFilter: 'blur(10px)'
          }}
        >
          <Box sx={{ width: '400px', textAlign: 'center' }}>
            <Box className="agent-pulse" sx={{ width: 80, height: 80, bgcolor: 'primary.main', mx: 'auto', mb: 4, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Psychology sx={{ fontSize: 40, color: '#000' }} />
            </Box>
            <Typography variant="h4" sx={{ fontWeight: 800, mb: 1 }}>Agentic <span className="gradient-text">Transformation</span></Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>The AI swarm is operationalizing your SOW...</Typography>
            
            <Box sx={{ mb: 4 }}>
              <LinearProgress variant="determinate" value={uploadProgress} sx={{ height: 10, borderRadius: 5, bgcolor: 'rgba(255,255,255,0.05)' }} />
              <Typography variant="caption" sx={{ mt: 2, display: 'block', fontWeight: 700, color: 'primary.main', textTransform: 'uppercase', letterSpacing: 1 }}>
                {uploadStep}
              </Typography>
            </Box>

            <Stack spacing={2} sx={{ textAlign: 'left', opacity: 0.6 }}>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                <DoneAll sx={{ color: uploadProgress > 20 ? 'primary.main' : 'text.disabled' }} />
                <Typography variant="body2">Ingestion & Metadata Extraction</Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                <DoneAll sx={{ color: uploadProgress > 50 ? 'primary.main' : 'text.disabled' }} />
                <Typography variant="body2">SLA & Liability Risk Mapping</Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                <DoneAll sx={{ color: uploadProgress > 80 ? 'primary.main' : 'text.disabled' }} />
                <Typography variant="body2">Revenue Leakage & Outcome Simulation</Typography>
              </Box>
            </Stack>
          </Box>
        </Box>
      )}

      {/* Header Section */}
      <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h3" sx={{ fontWeight: 800, mb: 1 }}>
            Transformation <span className="gradient-text">Hub</span>
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Operationalizing the journey from T&M to high-performance Outcome-Based delivery.
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" startIcon={<History />} sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700 }}>
            Audit Trail
          </Button>
          <Button variant="contained" startIcon={<Download />} sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700 }}>
            Export Strategy
          </Button>
        </Box>
      </Box>

      {/* Workflow Progress (Stepper-like) */}
      <Paper className="glass-card" sx={{ p: 4, mb: 6 }}>
        <Grid container spacing={2}>
          {[
            { label: 'Recon', icon: <Psychology />, desc: 'Model Classification', active: true },
            { label: 'Strategist', icon: <TrendingUp />, desc: 'Revenue Optimization', active: true },
            { label: 'Mitigator', icon: <Security />, desc: 'Risk Protection', active: true },
            { label: 'Drafter', icon: <AutoFixHigh />, desc: 'Contract Rewrite', active: true },
            { label: 'Monitor', icon: <TrackChanges />, desc: 'SLA Operationalization', active: false },
          ].map((step, i) => (
            <Grid item xs={2.4} key={i}>
              <Box sx={{ textAlign: 'center', opacity: step.active ? 1 : 0.3 }}>
                <Avatar sx={{ mx: 'auto', bgcolor: step.active ? 'primary.main' : 'rgba(255,255,255,0.1)', mb: 1, width: 48, height: 48 }}>
                  {step.icon}
                </Avatar>
                <Typography variant="subtitle2" sx={{ fontWeight: 800 }}>{step.label}</Typography>
                <Typography variant="caption" color="text.secondary">{step.desc}</Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Paper>

      <Grid container spacing={4}>
        {/* Left: SOW List & Selector */}
        <Grid item xs={12} md={4}>
          <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6" sx={{ fontWeight: 800 }}>Active Transformations</Typography>
            <Button 
              variant="contained" 
              size="small" 
              startIcon={<CloudUpload />} 
              onClick={() => {
                const input = document.createElement('input');
                input.type = 'file';
                input.onchange = (e: any) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    handleUpload(file, file.name.split('.')[0]);
                  }
                };
                input.click();
              }}
              sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700 }}
            >
              Upload
            </Button>
          </Box>
          <Stack spacing={2}>
            {sows.map((sow) => (
              <Box 
                key={sow._id} 
                onClick={() => setSelectedSowId(sow._id)}
                sx={{ 
                  p: 3, 
                  borderRadius: 4, 
                  cursor: 'pointer',
                  bgcolor: selectedSowId === sow._id ? 'rgba(0, 230, 118, 0.05)' : 'rgba(255,255,255,0.02)', 
                  border: selectedSowId === sow._id ? '1px solid #00e676' : '1px solid rgba(255,255,255,0.05)',
                  transition: 'all 0.2s',
                  '&:hover': { bgcolor: 'rgba(255,255,255,0.05)' }
                }}
              >
                <Typography variant="subtitle1" sx={{ fontWeight: 800 }}>{sow.project_name}</Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>{sow.client_name}</Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Chip size="small" label={sow.risk_assessment?.risk_level || 'low'} color={sow.risk_assessment?.risk_level === 'critical' ? 'error' : 'success'} sx={{ fontWeight: 900, textTransform: 'uppercase', fontSize: '0.6rem', height: 18 }} />
                  <Chip size="small" label={sow.active_agent || 'Recon'} sx={{ fontWeight: 900, fontSize: '0.6rem', height: 18 }} />
                </Box>
              </Box>
            ))}
          </Stack>
        </Grid>

        {/* Right: Detail & Agent Action Center */}
        <Grid item xs={12} md={8}>
          {!selectedSow ? (
            <Paper className="glass-card" sx={{ p: 10, textAlign: 'center' }}>
              <Psychology sx={{ fontSize: 60, opacity: 0.1, mb: 2 }} />
              <Typography color="text.secondary">Select an SOW to begin agentic transformation.</Typography>
            </Paper>
          ) : (
            <Stack spacing={4}>
              {/* Agentic Insights Tabs */}
              <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
                <Tabs value={tab} onChange={(_, v) => setTab(v)} textColor="primary" indicatorColor="primary">
                  <Tab label="Agentic Insights" sx={{ fontWeight: 800, textTransform: 'none' }} />
                  <Tab label={`Action Center (${selectedActionItems.length})`} sx={{ fontWeight: 800, textTransform: 'none' }} />
                </Tabs>
              </Box>

              {tab === 0 && (
                <Stack spacing={4}>
                  {/* Agent: Recon Findings */}
                  <Card className="glass-card">
                    <CardContent sx={{ p: 4 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2 }}>
                        <Avatar sx={{ bgcolor: 'primary.main' }}><Psychology /></Avatar>
                        <Box>
                          <Typography variant="h6" sx={{ fontWeight: 800 }}>Agent: Recon Findings</Typography>
                          <Typography variant="caption" color="text.secondary">Baseline Model Identification</Typography>
                        </Box>
                      </Box>
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                          <Paper sx={{ p: 3, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 3 }}>
                            <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 800 }}>Contract Type</Typography>
                            <Typography variant="h5" sx={{ fontWeight: 800, color: 'primary.main' }}>Time & Materials (T&M)</Typography>
                          </Paper>
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <Paper sx={{ p: 3, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 3 }}>
                            <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 800 }}>Baseline Risk Level</Typography>
                            <Typography variant="h5" sx={{ fontWeight: 800, color: 'warning.main' }}>{selectedSow.risk_assessment?.risk_level?.toUpperCase() || 'MEDIUM'}</Typography>
                          </Paper>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>

                  {/* Agent: Strategist (Revenue Optimization) */}
                  <Card className="glass-card revenue-uplift">
                    <CardContent sx={{ p: 4 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2 }}>
                        <Avatar sx={{ bgcolor: 'primary.main' }}><TrendingUp /></Avatar>
                        <Box>
                          <Typography variant="h6" sx={{ fontWeight: 800 }}>Agent: Strategist</Typography>
                          <Typography variant="caption" color="text.secondary">Revenue Leakage Optimization</Typography>
                        </Box>
                      </Box>
                      
                      {selectedSow.transformation_plan ? (
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={4}>
                            <Typography variant="h2" sx={{ fontWeight: 900, color: 'primary.main' }}>{selectedSow.transformation_plan.revenue_leakage_score}<span style={{ fontSize: '1rem', opacity: 0.5 }}>/100</span></Typography>
                            <Typography variant="subtitle2" sx={{ fontWeight: 800 }}>Leakage Score</Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                              {selectedSow.transformation_plan.risk_profile?.join(' ')}
                            </Typography>
                          </Grid>
                          <Grid item xs={12} md={8}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 800, mb: 2 }}>Proposed Outcome Milestones</Typography>
                            <Stack spacing={1}>
                              {selectedSow.transformation_plan.proposed_outcome_milestones?.map((m, i) => (
                                <Box key={i} sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2, display: 'flex', justifyContent: 'space-between' }}>
                                  <Typography variant="body2" sx={{ fontWeight: 600 }}>{m.milestone_name}</Typography>
                                  <Typography variant="body2" color="primary.main" sx={{ fontWeight: 800 }}>${m.value?.toLocaleString()}</Typography>
                                </Box>
                              ))}
                            </Stack>
                          </Grid>
                        </Grid>
                      ) : (
                        <Alert severity="info" sx={{ bgcolor: 'transparent', border: '1px solid rgba(0,230,118,0.2)' }}>Strategist Agent is analyzing revenue ceilings...</Alert>
                      )}
                    </CardContent>
                  </Card>

                  {/* Agent: Mitigator (Risk Shield) */}
                  <Card className="glass-card risk-shield">
                    <CardContent sx={{ p: 4 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2 }}>
                        <Avatar sx={{ bgcolor: 'secondary.main' }}><Security /></Avatar>
                        <Box>
                          <Typography variant="h6" sx={{ fontWeight: 800 }}>Agent: Mitigator</Typography>
                          <Typography variant="caption" color="text.secondary">Liability Shield & Penalty Analysis</Typography>
                        </Box>
                      </Box>
                      <Stack spacing={2}>
                        {selectedSowAlerts?.map((alert, i) => (
                          <Box key={i} sx={{ p: 2, bgcolor: 'rgba(244, 143, 177, 0.05)', border: '1px solid rgba(244, 143, 177, 0.1)', borderRadius: 2 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 800, color: 'secondary.main' }}>{alert.title}</Typography>
                            <Typography variant="body2" color="text.secondary">{alert.message}</Typography>
                          </Box>
                        ))}
                      </Stack>
                    </CardContent>
                  </Card>

                  {/* Agent: Drafter (Auto-Rewrite) */}
                  <Card className="glass-card">
                    <CardContent sx={{ p: 4 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2, justifyContent: 'space-between' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Avatar sx={{ bgcolor: 'info.main' }}><AutoFixHigh /></Avatar>
                          <Box>
                            <Typography variant="h6" sx={{ fontWeight: 800 }}>Agent: Drafter</Typography>
                            <Typography variant="caption" color="text.secondary">Ready-to-Sign Contract Rewrite</Typography>
                          </Box>
                        </Box>
                        <Button 
                          variant="contained" 
                          color="primary" 
                          startIcon={<DoneAll />} 
                          onClick={() => handleReviewDecision('approved')}
                          disabled={selectedSow.review_status === 'approved'}
                          sx={{ borderRadius: 2, fontWeight: 700 }}
                        >
                          {selectedSow.review_status === 'approved' ? 'Strategy Approved' : 'Approve Full Strategy'}
                        </Button>
                      </Box>
                      <Paper sx={{ p: 3, bgcolor: '#000', borderRadius: 4, maxHeight: 400, overflowY: 'auto' }}>
                        <pre style={{ margin: 0, whiteSpace: 'pre-wrap', color: '#00e676', fontFamily: 'monospace', fontSize: '0.85rem' }}>
                          {selectedSow.transformation_plan?.compensation_rewrite?.diff_format || selectedSow.transformation_plan?.compensation_rewrite?.new_text || 'Drafter Agent is generating the side-by-side diff...'}
                        </pre>
                      </Paper>
                    </CardContent>
                  </Card>
                </Stack>
              )}

              {tab === 1 && (
                <Stack spacing={3}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h5" sx={{ fontWeight: 800 }}>Agentic <span className="gradient-text">Transformation Backlog</span></Typography>
                    <Typography variant="body2" color="text.secondary">{selectedActionItems.length} precision items identified</Typography>
                  </Box>

                  {selectedActionItems.map((item) => {
                    const impact = getFinancialImpact(item);
                    return (
                      <Card key={item.id} className="glass-card" sx={{ borderLeft: `4px solid ${item.priority === 'critical' ? '#ff1744' : item.priority === 'high' ? '#ff9800' : '#00e676'}` }}>
                        <CardContent sx={{ p: 3 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2, alignItems: 'flex-start' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                              {item.action_type === 'create_github_issue' ? <GitHub sx={{ opacity: 0.5 }} /> : <CalendarMonth sx={{ opacity: 0.5 }} />}
                              <Box>
                                <Typography variant="subtitle1" sx={{ fontWeight: 800 }}>{item.title}</Typography>
                                <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                  <Gavel sx={{ fontSize: '0.8rem' }} /> SLA Ref: {item.sla_reference || 'N/A'}
                                </Typography>
                              </Box>
                            </Box>
                            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                              {renderRiskChip(item.priority)}
                              <Chip size="small" label={item.approval_state?.toUpperCase()} sx={{ fontSize: '0.6rem', fontWeight: 900 }} variant="outlined" />
                            </Box>
                          </Box>

                          <Grid container spacing={3}>
                            <Grid item xs={12} md={8}>
                              <Box sx={{ mb: 2 }}>
                                <Typography variant="caption" sx={{ fontWeight: 800, color: 'text.secondary', textTransform: 'uppercase', letterSpacing: 1, display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                                  <TipsAndUpdates sx={{ fontSize: '0.9rem' }} /> Why this change?
                                </Typography>
                                <Typography variant="body2" color="text.primary" sx={{ lineHeight: 1.6 }}>{item.description}</Typography>
                              </Box>
                              
                              <Box sx={{ mb: 2 }}>
                                <Typography variant="caption" sx={{ fontWeight: 800, color: 'text.secondary', textTransform: 'uppercase', letterSpacing: 1, display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                                  Recommended Fix
                                </Typography>
                                <Stack spacing={0.5}>
                                  {item.recommended_actions?.map((action, i) => (
                                    <Box key={i} sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}>
                                      <DoneAll sx={{ fontSize: '0.9rem', color: 'primary.main', mt: 0.3 }} />
                                      <Typography variant="body2" color="text.secondary">{action}</Typography>
                                    </Box>
                                  ))}
                                </Stack>
                              </Box>
                            </Grid>

                            <Grid item xs={12} md={4}>
                              <Box sx={{ bgcolor: 'rgba(255,255,255,0.02)', p: 2, borderRadius: 3, border: '1px solid rgba(255,255,255,0.05)', mb: 2 }}>
                                <Typography variant="caption" sx={{ fontWeight: 800, color: 'text.secondary', textTransform: 'uppercase', letterSpacing: 1, mb: 1, display: 'block' }}>
                                  Financial Impact
                                </Typography>
                                {impact ? (
                                  <Box>
                                    <Typography variant="h5" sx={{ fontWeight: 900, color: impact.color }}>{impact.value}</Typography>
                                    <Typography variant="caption" color="text.secondary">{impact.label}</Typography>
                                  </Box>
                                ) : (
                                  <Typography variant="body2" color="text.secondary">No immediate financial risk detected.</Typography>
                                )}
                              </Box>

                              <Stack spacing={1}>
                                <Button 
                                  variant="contained" 
                                  fullWidth 
                                  size="small" 
                                  startIcon={<DoneAll />} 
                                  onClick={() => handleExecuteActions([item.id])}
                                  disabled={executing}
                                  sx={{ borderRadius: 2, fontWeight: 700, textTransform: 'none' }}
                                >
                                  Approve Transform
                                </Button>
                                <Button 
                                  variant="outlined" 
                                  fullWidth 
                                  size="small" 
                                  startIcon={<CalendarMonth />} 
                                  onClick={() => toast.info('Scheduling alignment meeting...')}
                                  sx={{ borderRadius: 2, fontWeight: 700, textTransform: 'none' }}
                                >
                                  Schedule Meeting
                                </Button>
                              </Stack>
                            </Grid>
                          </Grid>
                        </CardContent>
                      </Card>
                    );
                  })}
                </Stack>
              )}
            </Stack>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};
export default TransformationHub;

// Made with Bob
