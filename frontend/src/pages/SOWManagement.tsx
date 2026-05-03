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
} from '@mui/material';
import {
  CloudUpload,
  Description,
  DoneAll,
  GitHub,
  Notifications,
  Timeline,
  Warning,
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

const SOWManagement: React.FC = () => {
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

  const handleUpload = async () => {
    if (!uploadForm.file || !uploadForm.sowNumber || !uploadForm.clientName || !uploadForm.projectName) {
      toast.error('Provide SOW number, client, project, and a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', uploadForm.file);
    formData.append('sow_number', uploadForm.sowNumber);
    formData.append('client_name', uploadForm.clientName);
    formData.append('project_name', uploadForm.projectName);

    setUploading(true);
    try {
      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });

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

  const renderRiskChip = (level?: string) => (
    <Chip
      size="small"
      label={(level || 'unknown').toUpperCase()}
      color={
        level === 'critical'
          ? 'error'
          : level === 'high'
            ? 'warning'
            : level === 'medium'
              ? 'info'
              : 'success'
      }
    />
  );

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          SOW Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload new SOWs, review agentic findings, surface numeric risk, approve action plans, and execute approved work into GitHub or calendar workflows.
        </Typography>
      </Box>

      {dashboardSummary && (
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="overline">Active SOWs</Typography>
                <Typography variant="h4">{dashboardSummary.active_sows}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="overline">At-Risk Obligations</Typography>
                <Typography variant="h4">{dashboardSummary.at_risk_obligations}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="overline">Critical Alerts</Typography>
                <Typography variant="h4">{dashboardSummary.critical_alerts}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="overline">Penalty Exposure</Typography>
                <Typography variant="h4">${dashboardSummary.total_penalty_exposure.toLocaleString()}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tab} onChange={(_, value) => setTab(value)}>
          <Tab label="Upload New SOW" icon={<CloudUpload />} iconPosition="start" />
          <Tab label="Review Saved SOWs" icon={<Description />} iconPosition="start" />
        </Tabs>
      </Paper>

      {tab === 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Upload and Analyze
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="SOW Number"
                value={uploadForm.sowNumber}
                onChange={(event) => handleUploadChange('sowNumber', event.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Client Name"
                value={uploadForm.clientName}
                onChange={(event) => handleUploadChange('clientName', event.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Project Name"
                value={uploadForm.projectName}
                onChange={(event) => handleUploadChange('projectName', event.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={8}>
              <Button variant="outlined" component="label" fullWidth sx={{ py: 1.8 }}>
                {uploadForm.file ? `Selected: ${uploadForm.file.name}` : 'Choose SOW file'}
                <input hidden type="file" accept=".pdf,.doc,.docx,.txt" onChange={handleFileChange} />
              </Button>
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                fullWidth
                variant="contained"
                onClick={handleUpload}
                disabled={uploading}
                sx={{ height: '100%' }}
                startIcon={uploading ? <CircularProgress size={18} color="inherit" /> : <CloudUpload />}
              >
                {uploading ? 'Analyzing...' : 'Upload & Analyze'}
              </Button>
            </Grid>
          </Grid>

          <Alert severity="info" sx={{ mt: 3 }}>
            The upload flow parses the SOW, generates SLA and revenue-risk findings, creates human-review action items, and persists the review package for later approval and execution.
          </Alert>
        </Paper>
      )}

      {tab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, minHeight: 600 }}>
              <Typography variant="h6" gutterBottom>
                Saved SOWs
              </Typography>
              {loadingList ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                  <CircularProgress />
                </Box>
              ) : sows.length === 0 ? (
                <Alert severity="info">No SOWs saved yet.</Alert>
              ) : (
                <Stack spacing={2}>
                  {sows.map((sow) => (
                    <Card
                      key={sow._id}
                      variant={selectedSowId === sow._id ? 'elevation' : 'outlined'}
                      sx={{
                        cursor: 'pointer',
                        borderColor: selectedSowId === sow._id ? 'primary.main' : undefined,
                      }}
                      onClick={() => setSelectedSowId(sow._id)}
                    >
                      <CardContent>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {sow.project_name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {sow.client_name} · {sow.sow_number}
                        </Typography>
                        <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                          {renderRiskChip(sow.risk_assessment?.risk_level)}
                          <Chip size="small" label={sow.review_status || 'pending'} />
                        </Box>
                      </CardContent>
                    </Card>
                  ))}
                </Stack>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, minHeight: 600 }}>
              {!selectedSowId ? (
                <Alert severity="info">Select a saved SOW to review.</Alert>
              ) : loadingDetail ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                  <CircularProgress />
                </Box>
              ) : !selectedSow ? (
                <Alert severity="error">Failed to load selected SOW.</Alert>
              ) : (
                <Stack spacing={3}>
                  <Box>
                    <Typography variant="h5">{selectedSow.project_name}</Typography>
                    <Typography variant="body1" color="text.secondary">
                      {selectedSow.client_name} · {selectedSow.sow_number}
                    </Typography>
                    <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {renderRiskChip(selectedSow.risk_assessment?.risk_level)}
                      <Chip label={selectedSow.analysis_status || 'analysis_unknown'} />
                      <Chip label={selectedSow.review_status || 'review_unknown'} />
                    </Box>
                  </Box>

                  <Grid container spacing={2}>
                    <Grid item xs={12} md={3}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="overline">Risk Score</Typography>
                          <Typography variant="h4">{selectedSow.risk_assessment?.risk_score ?? 0}</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="overline">Penalty Exposure</Typography>
                          <Typography variant="h5">
                            ${Number(selectedSow.risk_assessment?.total_penalty_exposure ?? 0).toLocaleString()}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="overline">Alerts</Typography>
                          <Typography variant="h4">{selectedSowAlerts.length}</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="overline">Action Items</Typography>
                          <Typography variant="h4">{selectedActionItems.length}</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>

                  <Divider />

                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Agent Summary
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={4}>
                        <Paper variant="outlined" sx={{ p: 2 }}>
                          <Typography variant="subtitle2">Ingestion Findings</Typography>
                          <Typography variant="body2">
                            Obligations: {selectedSow.agent_summary?.ingestion_findings?.obligations_count ?? 0}
                          </Typography>
                          <Typography variant="body2">
                            SLA Terms: {selectedSow.agent_summary?.ingestion_findings?.sla_terms_count ?? 0}
                          </Typography>
                          <Typography variant="body2">
                            Vague Clauses: {selectedSow.agent_summary?.ingestion_findings?.vague_clauses_count ?? 0}
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Paper variant="outlined" sx={{ p: 2 }}>
                          <Typography variant="subtitle2">Risk Findings</Typography>
                          <Typography variant="body2">
                            Level: {String(selectedSow.agent_summary?.risk_findings?.risk_level ?? 'unknown')}
                          </Typography>
                          <Typography variant="body2">
                            Penalty Exposure: ${Number(selectedSow.agent_summary?.risk_findings?.total_penalty_exposure ?? 0).toLocaleString()}
                          </Typography>
                          <Typography variant="body2">
                            High Risk Obligations: {selectedSow.agent_summary?.risk_findings?.high_risk_obligations ?? 0}
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Paper variant="outlined" sx={{ p: 2 }}>
                          <Typography variant="subtitle2">Executive Recommendations</Typography>
                          <Typography variant="body2">
                            Alerts Generated: {selectedSow.agent_summary?.executive_recommendations?.alerts_generated ?? 0}
                          </Typography>
                          <Typography variant="body2">
                            Action Items: {selectedSow.agent_summary?.executive_recommendations?.action_items_generated ?? 0}
                          </Typography>
                          <Typography variant="body2">
                            Scope Creep: {selectedSow.agent_summary?.executive_recommendations?.scope_creep_items_detected ?? 0}
                          </Typography>
                        </Paper>
                      </Grid>
                    </Grid>
                  </Box>

                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Alerts
                    </Typography>
                    <Stack spacing={2}>
                      {selectedSowAlerts.length === 0 ? (
                        <Alert severity="success">No alerts generated for this SOW.</Alert>
                      ) : (
                        selectedSowAlerts.map((alert, index) => (
                          <Alert
                            key={alert._id || alert.id || `${alert.title}-${index}`}
                            severity={
                              alert.severity === 'critical'
                                ? 'error'
                                : alert.severity === 'high'
                                  ? 'warning'
                                  : 'info'
                            }
                            icon={<Notifications />}
                          >
                            <Typography variant="subtitle2">{alert.title}</Typography>
                            <Typography variant="body2">{alert.message}</Typography>
                            {(alert.penalty_amount || alert.hours_until_penalty || alert.days_until_penalty) && (
                              <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                {typeof alert.penalty_amount === 'number' && (
                                  <Chip size="small" color="error" label={`Exposure $${alert.penalty_amount.toLocaleString()}`} />
                                )}
                                {typeof alert.hours_until_penalty === 'number' && (
                                  <Chip size="small" color="warning" label={`${alert.hours_until_penalty} hrs left`} />
                                )}
                                {typeof alert.days_until_penalty === 'number' && typeof alert.hours_until_penalty !== 'number' && (
                                  <Chip size="small" color="warning" label={`${alert.days_until_penalty} days left`} />
                                )}
                              </Box>
                            )}
                            {alert.recommended_actions && alert.recommended_actions.length > 0 && (
                              <Box sx={{ mt: 1 }}>
                                <Typography variant="caption">Recommended Actions:</Typography>
                                <List dense>
                                  {alert.recommended_actions.map((action, actionIndex) => (
                                    <ListItem key={`${alert.title}-${actionIndex}`} sx={{ py: 0 }}>
                                      <ListItemText primary={action} />
                                    </ListItem>
                                  ))}
                                </List>
                              </Box>
                            )}
                          </Alert>
                        ))
                      )}
                    </Stack>
                  </Box>

                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Action Items
                    </Typography>
                    <Stack spacing={2}>
                      {selectedActionItems.length === 0 ? (
                        <Alert severity="info">No action items were generated.</Alert>
                      ) : (
                        selectedActionItems.map((item) => (
                          <Card key={item.id} variant="outlined">
                            <CardContent>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2, flexWrap: 'wrap' }}>
                                <Box sx={{ flex: 1, minWidth: 280 }}>
                                  <Typography variant="subtitle1">{item.title}</Typography>
                                  <Typography variant="body2" color="text.secondary">
                                    {item.description}
                                  </Typography>
                                </Box>
                                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'flex-start' }}>
                                  {renderRiskChip(item.priority)}
                                  <Chip size="small" label={item.approval_state || 'pending'} />
                                  <Chip size="small" label={item.execution_state || 'not_started'} />
                                </Box>
                              </Box>

                              <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                                Recommended owner: {item.recommended_owner || 'unassigned'}
                              </Typography>

                              {(item.execution_targets?.length || item.action_type || item.workflow_stage || item.sla_reference) && (
                                <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                  {item.workflow_stage && (
                                    <Chip
                                      size="small"
                                      color={item.workflow_stage === 'pre_acceptance' ? 'secondary' : 'primary'}
                                      label={item.workflow_stage === 'pre_acceptance' ? 'PRE-ACCEPTANCE' : 'POST-APPROVAL'}
                                    />
                                  )}
                                  {item.action_type && (
                                    <Chip size="small" variant="outlined" label={item.action_type.replaceAll('_', ' ')} />
                                  )}
                                  {item.execution_targets?.map((target) => (
                                    <Chip key={`${item.id}-${target}`} size="small" label={target.toUpperCase()} />
                                  ))}
                                  {item.sla_reference && (
                                    <Chip size="small" color="warning" variant="outlined" label={`SLA: ${item.sla_reference}`} />
                                  )}
                                </Box>
                              )}

                              {item.numeric_risk && (
                                <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                  {item.numeric_risk.penalty_amount_display && (
                                    <Chip color="error" size="small" label={`Penalty ${item.numeric_risk.penalty_amount_display}`} />
                                  )}
                                  {typeof item.numeric_risk.days_remaining === 'number' && (
                                    <Chip color="warning" size="small" label={`${item.numeric_risk.days_remaining} days remaining`} />
                                  )}
                                  {typeof item.numeric_risk.hours_until_penalty === 'number' && (
                                    <Chip color="warning" size="small" label={`${item.numeric_risk.hours_until_penalty} hrs until penalty`} />
                                  )}
                                  {item.numeric_risk.potential_revenue_display && (
                                    <Chip color="primary" size="small" label={`Revenue at stake ${item.numeric_risk.potential_revenue_display}`} />
                                  )}
                                  {item.numeric_risk.total_penalty_exposure_display && (
                                    <Chip color="error" size="small" label={`Portfolio exposure ${item.numeric_risk.total_penalty_exposure_display}`} />
                                  )}
                                  {typeof item.numeric_risk.risk_score === 'number' && (
                                    <Chip color="info" size="small" label={`Risk score ${item.numeric_risk.risk_score}`} />
                                  )}
                                </Box>
                              )}

                              {item.recommended_actions && item.recommended_actions.length > 0 && (
                                <List dense sx={{ mt: 1 }}>
                                  {item.recommended_actions.map((action, actionIndex) => (
                                    <ListItem key={`${item.id}-${actionIndex}`} sx={{ py: 0 }}>
                                      <ListItemText primary={action} />
                                    </ListItem>
                                  ))}
                                </List>
                              )}

                              <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                {item.execution_targets?.includes('github') && (
                                  <Button
                                    size="small"
                                    variant="contained"
                                    startIcon={<GitHub />}
                                    disabled={executing || item.approval_state !== 'approved' || !item.execution_targets?.includes('github')}
                                    onClick={() => void handleExecuteActions([item.id], item.workflow_stage)}
                                  >
                                    {item.cta_label || 'Create GitHub item'}
                                  </Button>
                                )}
                                {item.execution_targets?.includes('calendar') && (
                                  <Button
                                    size="small"
                                    variant="outlined"
                                    startIcon={<Timeline />}
                                    disabled={executing || item.approval_state !== 'approved' || !item.execution_targets?.includes('calendar')}
                                    onClick={() => void handleExecuteActions([item.id], item.workflow_stage)}
                                  >
                                    {item.execution_targets?.includes('github') ? 'Schedule meeting' : (item.cta_label || 'Schedule meeting')}
                                  </Button>
                                )}
                              </Box>

                              {(item.github_issue?.issue_url || item.calendar_event?.title) && (
                                <Box sx={{ mt: 2 }}>
                                  {item.github_issue?.issue_url && (
                                    <Typography variant="body2" color="primary">
                                      GitHub issue created:
                                      {' '}
                                      <a
                                        href={item.github_issue.issue_url}
                                        target="_blank"
                                        rel="noreferrer"
                                        style={{ color: 'inherit', textDecoration: 'underline' }}
                                      >
                                        {item.github_issue.issue_url}
                                      </a>
                                      {item.github_issue.repository ? ` · Repo ${item.github_issue.repository}` : ''}
                                      {item.github_issue.sla_reference ? ` · SLA ${item.github_issue.sla_reference}` : ''}
                                    </Typography>
                                  )}
                                  {item.calendar_event?.title && (
                                    <Typography variant="body2" color="text.secondary">
                                      Calendar: {item.calendar_event.title}
                                      {item.calendar_event.provider ? ` (${item.calendar_event.provider})` : ''}
                                      {item.calendar_event.calendar_name ? ` · ${item.calendar_event.calendar_name}` : ''}
                                      {item.calendar_event.sla_reference ? ` · SLA ${item.calendar_event.sla_reference}` : ''}
                                    </Typography>
                                  )}
                                </Box>
                              )}
                            </CardContent>
                          </Card>
                        ))
                      )}
                    </Stack>
                  </Box>

                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Timeline
                    </Typography>
                    <List>
                      {timeline.length === 0 ? (
                        <ListItem>
                          <ListItemText primary="No timeline events recorded." />
                        </ListItem>
                      ) : (
                        timeline.map((event) => (
                          <ListItem key={event.id} divider>
                            <ListItemText
                              primary={event.title}
                              secondary={`${event.event_type} · ${new Date(event.timestamp).toLocaleString()}`}
                            />
                          </ListItem>
                        ))
                      )}
                    </List>
                  </Box>

                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Review Decision & Actions
                    </Typography>
                    <TextField
                      fullWidth
                      multiline
                      minRows={3}
                      label="Review Notes"
                      value={approvalNotes}
                      onChange={(event) => setApprovalNotes(event.target.value)}
                    />
                    <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                      <Button
                        variant="contained"
                        color="success"
                        startIcon={<DoneAll />}
                        onClick={() => void handleReviewDecision('approved')}
                        disabled={approving || selectedActionItems.length === 0}
                      >
                        {approving ? 'Saving...' : 'Accept SOW'}
                      </Button>
                      <Button
                        variant="outlined"
                        color="error"
                        onClick={() => void handleReviewDecision('rejected')}
                        disabled={approving || !selectedSowId}
                      >
                        Reject SOW
                      </Button>
                      <Button
                        variant="outlined"
                        color="inherit"
                        onClick={() => void handleReviewDecision('clear')}
                        disabled={approving || !selectedSowId}
                      >
                        Clear Review
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<GitHub />}
                        onClick={() => void handleExecuteActions()}
                        disabled={executing || selectedSow?.review_status !== 'approved'}
                      >
                        {executing ? 'Executing...' : 'Take Actions / Execute Approved Actions'}
                      </Button>
                    </Box>
                  </Box>
                </Stack>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};
export default SOWManagement;

// Made with Bob
