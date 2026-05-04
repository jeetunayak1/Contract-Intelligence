import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Stepper,
  Step,
  StepLabel,
  Button,
  TextField,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore,
  GitHub,
  Chat,
  Email,
  CheckCircle,
  Error as ErrorIcon,
  Info,
  Add,
  Delete,
  AutoAwesome,
} from '@mui/icons-material';

interface TeamInfo {
  project_manager: string;
  tech_lead: string;
  team_size: number;
  github_repo: string;
  slack_workspace: string;
  slack_alert_channel: string;
  outlook_calendar_name: string;
  key_stakeholders: string[];
}

interface GitHubLabel {
  name: string;
  color: string;
  description: string;
}

interface GitHubIssueTemplate {
  title_prefix: string;
  body_intro: string;
  default_labels: string[];
  assignees: string[];
}

interface GitHubGeneratedIssue {
  obligation_id: string;
  title: string;
  body: string;
  labels: string[];
  assignees: string[];
  issue_number?: number;
  issue_url?: string;
  issue_type: string;
  created: boolean;
}

interface GitHubAutomationSettings {
  create_labels: boolean;
  create_milestone: boolean;
  create_issue_templates: boolean;
  auto_create_obligation_issues: boolean;
  auto_create_review_issue: boolean;
}

interface SlackChannel {
  name: string;
  description: string;
  is_private: boolean;
  members?: string[];
}

interface TeamMember {
  name: string;
  email: string;
  role: string;
  notify_on: string[];
}

interface IntegrationConfigData {
  sow_id: string;
  team_info?: Partial<TeamInfo>;
  github?: {
    sow_id?: string;
    repository_owner: string;
    repository_name: string;
    labels: GitHubLabel[];
    milestone_name: string;
    project_board_name?: string;
    issue_template?: GitHubIssueTemplate;
    automation?: GitHubAutomationSettings;
    generated_issues?: GitHubGeneratedIssue[];
    configured?: boolean;
  };
  slack?: {
    sow_id?: string;
    workspace_id: string;
    channels: SlackChannel[];
    alert_channel: string;
    configured?: boolean;
  };
  outlook?: {
    sow_id?: string;
    team_members: TeamMember[];
    calendar_name: string;
    configured?: boolean;
  };
}

interface ConfigurationResponse {
  sow_id: string;
  suggested_config: IntegrationConfigData;
  explanation: string;
  next_steps: string[];
}

const IntegrationConfig: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [sowId, setSowId] = useState('');
  const [teamInfo, setTeamInfo] = useState<TeamInfo>({
    project_manager: '',
    tech_lead: '',
    team_size: 5,
    github_repo: '',
    slack_workspace: '',
    slack_alert_channel: '',
    outlook_calendar_name: '',
    key_stakeholders: [],
  });
  const [configuration, setConfiguration] = useState<ConfigurationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [applyResults, setApplyResults] = useState<any>(null);
  const [newStakeholder, setNewStakeholder] = useState('');
  const [existingConfig, setExistingConfig] = useState<IntegrationConfigData | null>(null);
  const [loadingExisting, setLoadingExisting] = useState(false);

  const steps = ['Team Information', 'AI Configuration', 'Review & Apply'];

  // Load existing configuration if SOW ID changes
  useEffect(() => {
    const loadExistingConfig = async () => {
      if (!sowId.trim()) return;
      
      setLoadingExisting(true);
      try {
        const response = await fetch(`http://localhost:8000/api/v1/integrations/${sowId}`);
        if (response.ok) {
          const data = await response.json();
          setExistingConfig(data);
          setTeamInfo(prev => ({
            ...prev,
            ...data.team_info,
            github_repo: data.github
              ? `${data.github.repository_owner}/${data.github.repository_name}`
              : prev.github_repo,
            slack_workspace: data.slack?.workspace_id ?? prev.slack_workspace,
            slack_alert_channel: data.slack?.alert_channel ?? prev.slack_alert_channel,
            outlook_calendar_name: data.outlook?.calendar_name ?? prev.outlook_calendar_name,
          }));
        }
      } catch (error) {
        console.error('Failed to load existing configuration:', error);
      } finally {
        setLoadingExisting(false);
      }
    };

    loadExistingConfig();
  }, [sowId]);

  const handleGenerateConfig = async () => {
    if (!sowId.trim()) {
      alert('Please enter an SOW ID');
      return;
    }
    if (!teamInfo.project_manager.trim() || !teamInfo.tech_lead.trim()) {
      alert('Please enter Project Manager and Tech Lead information');
      return;
    }
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/integrations/configure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sow_id: sowId, team_info: teamInfo }),
      });
      const data = await response.json();
      setConfiguration(data);
      setActiveStep(1);
    } catch (error) {
      console.error('Failed to generate configuration:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyConfiguration = async () => {
    if (!configuration) return;
    
    setApplying(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/integrations/apply/${sowId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(configuration.suggested_config),
      });
      const data = await response.json();
      setApplyResults(data);
      setExistingConfig(configuration.suggested_config);
      setActiveStep(2);
    } catch (error) {
      console.error('Failed to apply configuration:', error);
    } finally {
      setApplying(false);
    }
  };

  const updateTeamInfo = (field: keyof TeamInfo, value: string | number) => {
    setTeamInfo((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const addStakeholder = () => {
    if (newStakeholder && !teamInfo.key_stakeholders.includes(newStakeholder)) {
      setTeamInfo({
        ...teamInfo,
        key_stakeholders: [...teamInfo.key_stakeholders, newStakeholder],
      });
      setNewStakeholder('');
    }
  };

  const removeStakeholder = (email: string) => {
    setTeamInfo({
      ...teamInfo,
      key_stakeholders: teamInfo.key_stakeholders.filter(s => s !== email),
    });
  };

  const generatedIssues = configuration?.suggested_config.github?.generated_issues ?? [];
  const existingGeneratedIssues = existingConfig?.github?.generated_issues ?? [];
  const existingGitHubSow = existingConfig?.github?.sow_id ?? existingConfig?.sow_id;
  const existingSlackSow = existingConfig?.slack?.sow_id ?? existingConfig?.sow_id;
  const existingOutlookSow = existingConfig?.outlook?.sow_id ?? existingConfig?.sow_id;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          <AutoAwesome sx={{ mr: 1, verticalAlign: 'middle' }} />
          AI-Powered Integration Configuration
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure GitHub, Slack, and Outlook per SOW so each engagement gets its own labels, issues, channels, and stakeholders
        </Typography>
      </Box>

      {/* Stepper */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {existingConfig && (
        <Paper sx={{ p: 3, mb: 3, border: '1px solid', borderColor: 'divider' }}>
          <Typography variant="h6" gutterBottom>
            Existing Saved Per-SOW Configuration
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Each integration below is stored independently against SOW <strong>{sowId}</strong> and will not affect other SOWs.
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2">GitHub SOW Binding</Typography>
              <Typography variant="body2" color="text.secondary">
                {existingGitHubSow || 'Not saved'}
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2">Slack SOW Binding</Typography>
              <Typography variant="body2" color="text.secondary">
                {existingSlackSow || 'Not saved'}
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2">Outlook SOW Binding</Typography>
              <Typography variant="body2" color="text.secondary">
                {existingOutlookSow || 'Not saved'}
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2">Saved Slack Alert Channel</Typography>
              <Typography variant="body2" color="text.secondary">
                {existingConfig.slack?.alert_channel || 'Not saved'}
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2">Saved Outlook Calendar</Typography>
              <Typography variant="body2" color="text.secondary">
                {existingConfig.outlook?.calendar_name || 'Not saved'}
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2">Saved Generated GitHub Issues</Typography>
              <Typography variant="body2" color="text.secondary">
                {existingGeneratedIssues.length} issue definitions saved for this SOW
              </Typography>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Step 1: Team Information */}
      {activeStep === 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Tell us about your team
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Provide SOW-specific team information and the system will generate dedicated GitHub, Slack, and Outlook configuration for this engagement
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="SOW ID"
                value={sowId}
                onChange={(e) => setSowId(e.target.value.toUpperCase())}
                helperText="Statement of Work identifier"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Project Manager"
                value={teamInfo.project_manager}
                onChange={(e) => updateTeamInfo('project_manager', e.target.value)}
                helperText="Format: Name <email@example.com>"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Tech Lead"
                value={teamInfo.tech_lead}
                onChange={(e) => updateTeamInfo('tech_lead', e.target.value)}
                helperText="Format: Name <email@example.com>"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Team Size"
                value={teamInfo.team_size}
                onChange={(e) => updateTeamInfo('team_size', parseInt(e.target.value || '0', 10))}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="GitHub Repository"
                value={teamInfo.github_repo}
                onChange={(e) => updateTeamInfo('github_repo', e.target.value)}
                helperText="Format: owner/repository"
                InputProps={{
                  startAdornment: <GitHub sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Slack Workspace"
                value={teamInfo.slack_workspace}
                onChange={(e) => updateTeamInfo('slack_workspace', e.target.value)}
                helperText="Workspace for this SOW only"
                InputProps={{
                  startAdornment: <Chat sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Slack Alert Channel"
                value={teamInfo.slack_alert_channel}
                onChange={(e) => updateTeamInfo('slack_alert_channel', e.target.value)}
                helperText="Dedicated alert channel for this SOW, e.g. sow-acme-alerts"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Outlook Calendar Name"
                value={teamInfo.outlook_calendar_name}
                onChange={(e) => updateTeamInfo('outlook_calendar_name', e.target.value)}
                helperText="Dedicated calendar for this SOW, e.g. ACME Migration Delivery Calendar"
              />
            </Grid>

            <Grid item xs={12}>
              <Alert severity="info">
                This form defines a separate GitHub repository mapping, Slack workspace/channel, Outlook calendar, and stakeholder list for the current SOW only.
              </Alert>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Key Stakeholders
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="stakeholder@example.com"
                  value={newStakeholder}
                  onChange={(e) => setNewStakeholder(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addStakeholder()}
                />
                <Button variant="outlined" onClick={addStakeholder} startIcon={<Add />}>
                  Add
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {teamInfo.key_stakeholders.map((email) => (
                  <Chip
                    key={email}
                    label={email}
                    onDelete={() => removeStakeholder(email)}
                    icon={<Email />}
                  />
                ))}
              </Box>
            </Grid>
          </Grid>

          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleGenerateConfig}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <AutoAwesome />}
            >
              {loading ? 'Generating Configuration...' : 'Generate AI Configuration'}
            </Button>
          </Box>
        </Paper>
      )}

      {/* Step 2: AI Configuration */}
      {activeStep === 1 && configuration && (
        <Box>
          {/* AI Explanation */}
          <Alert severity="info" icon={<AutoAwesome />} sx={{ mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              AI Configuration Analysis
            </Typography>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
              {configuration.explanation}
            </Typography>
          </Alert>

          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={4}>
              <Alert severity="info">
                GitHub is scoped to <strong>{configuration.suggested_config.github?.sow_id || configuration.sow_id}</strong>
              </Alert>
            </Grid>
            <Grid item xs={12} md={4}>
              <Alert severity="info">
                Slack is scoped to <strong>{configuration.suggested_config.slack?.sow_id || configuration.sow_id}</strong>
              </Alert>
            </Grid>
            <Grid item xs={12} md={4}>
              <Alert severity="info">
                Outlook is scoped to <strong>{configuration.suggested_config.outlook?.sow_id || configuration.sow_id}</strong>
              </Alert>
            </Grid>
          </Grid>

          {/* GitHub Configuration */}
          {configuration.suggested_config.github && (
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <GitHub sx={{ mr: 2 }} />
                <Typography variant="h6">GitHub Configuration</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Alert severity="success">
                      This GitHub setup belongs only to SOW <strong>{configuration.suggested_config.github.sow_id || configuration.sow_id}</strong>.
                      Labels, milestone, board, and generated issues are independent from other SOWs.
                    </Alert>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Repository: {configuration.suggested_config.github.repository_owner}/
                      {configuration.suggested_config.github.repository_name}
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Custom Labels ({configuration.suggested_config.github.labels.length})
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {configuration.suggested_config.github.labels.map((label) => (
                        <Tooltip key={label.name} title={label.description}>
                          <Chip
                            label={label.name}
                            size="small"
                            sx={{
                              bgcolor: `#${label.color}`,
                              color: '#fff',
                            }}
                          />
                        </Tooltip>
                      ))}
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary">
                      Milestone: {configuration.suggested_config.github.milestone_name}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary">
                      Project Board: {configuration.suggested_config.github.project_board_name || 'Not configured'}
                    </Typography>
                  </Grid>
                  {configuration.suggested_config.github.issue_template && (
                    <Grid item xs={12}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="subtitle2" gutterBottom>
                            Issue Template
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Prefix: {configuration.suggested_config.github.issue_template.title_prefix}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Default assignees: {configuration.suggested_config.github.issue_template.assignees.join(', ') || 'None'}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Default labels: {configuration.suggested_config.github.issue_template.default_labels.join(', ') || 'None'}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  )}
                  {configuration.suggested_config.github.automation && (
                    <Grid item xs={12}>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {Object.entries(configuration.suggested_config.github.automation).map(([key, enabled]) => (
                          <Chip
                            key={key}
                            label={key.replace(/_/g, ' ')}
                            color={enabled ? 'success' : 'default'}
                            variant={enabled ? 'filled' : 'outlined'}
                          />
                        ))}
                      </Box>
                    </Grid>
                  )}
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Generated SOW Issues ({generatedIssues.length})
                    </Typography>
                    <List dense>
                      {generatedIssues.map((issue) => (
                        <ListItem key={issue.obligation_id} alignItems="flex-start">
                          <ListItemIcon>
                            <Info color="primary" />
                          </ListItemIcon>
                          <ListItemText
                            primary={issue.title}
                            secondary={
                              <>
                                <Typography variant="body2" color="text.secondary">
                                  Type: {issue.issue_type} • Obligation: {issue.obligation_id}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  Labels: {issue.labels.join(', ') || 'None'}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  Assignees: {issue.assignees.join(', ') || 'None'}
                                </Typography>
                              </>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Slack Configuration */}
          {configuration.suggested_config.slack && (
            <Accordion defaultExpanded sx={{ mt: 2 }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Chat sx={{ mr: 2 }} />
                <Typography variant="h6">Slack Configuration</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Alert severity="success">
                      Slack notifications and channels are isolated for SOW <strong>{configuration.suggested_config.slack.sow_id || configuration.sow_id}</strong>.
                    </Alert>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Workspace: {configuration.suggested_config.slack.workspace_id}
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Dedicated Channels
                    </Typography>
                    <List dense>
                      {configuration.suggested_config.slack.channels.map((channel) => (
                        <ListItem key={channel.name}>
                          <ListItemIcon>
                            <Chat color="primary" />
                          </ListItemIcon>
                          <ListItemText
                            primary={`#${channel.name}`}
                            secondary={channel.description}
                          />
                          {channel.name === configuration.suggested_config.slack?.alert_channel && (
                            <Chip label="Alert Channel" size="small" color="primary" />
                          )}
                        </ListItem>
                      ))}
                    </List>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Outlook Configuration */}
          {configuration.suggested_config.outlook && (
            <Accordion defaultExpanded sx={{ mt: 2 }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Email sx={{ mr: 2 }} />
                <Typography variant="h6">Outlook Configuration</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Alert severity="success">
                      Outlook schedules and stakeholders are isolated for SOW <strong>{configuration.suggested_config.outlook.sow_id || configuration.sow_id}</strong>.
                    </Alert>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Calendar: {configuration.suggested_config.outlook.calendar_name}
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Team Members ({configuration.suggested_config.outlook.team_members.length})
                    </Typography>
                    <List dense>
                      {configuration.suggested_config.outlook.team_members.map((member) => (
                        <ListItem key={member.email}>
                          <ListItemIcon>
                            <Email color="primary" />
                          </ListItemIcon>
                          <ListItemText
                            primary={`${member.name} (${member.role})`}
                            secondary={member.email}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Next Steps */}
          {existingConfig && (
            <Paper sx={{ p: 3, mt: 3, mb: 3, border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="h6" gutterBottom>
                Existing Saved Per-SOW Configuration
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2">GitHub SOW Binding</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {existingGitHubSow || 'Not saved'}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2">Slack SOW Binding</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {existingSlackSow || 'Not saved'}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2">Outlook SOW Binding</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {existingOutlookSow || 'Not saved'}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2">Saved Slack Alert Channel</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {existingConfig.slack?.alert_channel || 'Not saved'}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2">Saved Outlook Calendar</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {existingConfig.outlook?.calendar_name || 'Not saved'}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2">Saved Generated GitHub Issues</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {existingGeneratedIssues.length} issue definitions saved for this SOW
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          )}

          <Paper sx={{ p: 3, mt: 3, bgcolor: 'background.default' }}>
            <Typography variant="subtitle2" gutterBottom>
              Next Steps
            </Typography>
            <List dense>
              {configuration.next_steps.map((step, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <Info color="primary" />
                  </ListItemIcon>
                  <ListItemText primary={step} />
                </ListItem>
              ))}
            </List>
          </Paper>

          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
            <Button onClick={() => setActiveStep(0)}>Back</Button>
            <Button
              variant="contained"
              size="large"
              onClick={handleApplyConfiguration}
              disabled={applying}
              startIcon={applying ? <CircularProgress size={20} /> : <CheckCircle />}
            >
              {applying ? 'Applying Configuration...' : 'Apply Configuration'}
            </Button>
          </Box>
        </Box>
      )}

      {/* Step 3: Results */}
      {activeStep === 2 && applyResults && (
        <Box>
          <Alert
            severity={applyResults.overall_success ? 'success' : 'warning'}
            sx={{ mb: 3 }}
          >
            <Typography variant="subtitle2">
              {applyResults.overall_success
                ? 'Configuration applied successfully!'
                : 'Configuration partially applied'}
            </Typography>
          </Alert>

          <Grid container spacing={2}>
            {/* GitHub Results */}
            {applyResults.results.github && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <GitHub sx={{ mr: 2 }} />
                      <Typography variant="h6">GitHub</Typography>
                      {applyResults.results.github.success ? (
                        <CheckCircle color="success" sx={{ ml: 'auto' }} />
                      ) : (
                        <ErrorIcon color="error" sx={{ ml: 'auto' }} />
                      )}
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {applyResults.results.github.message}
                    </Typography>
                    {applyResults.results.github.created_labels && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="caption" display="block" gutterBottom>
                          Created Labels:
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {applyResults.results.github.created_labels.map((label: string) => (
                            <Chip key={label} label={label} size="small" />
                          ))}
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Slack Results */}
            {applyResults.results.slack && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Chat sx={{ mr: 2 }} />
                      <Typography variant="h6">Slack</Typography>
                      {applyResults.results.slack.success ? (
                        <CheckCircle color="success" sx={{ ml: 'auto' }} />
                      ) : (
                        <ErrorIcon color="error" sx={{ ml: 'auto' }} />
                      )}
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {applyResults.results.slack.message}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Outlook Results */}
            {applyResults.results.outlook && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Email sx={{ mr: 2 }} />
                      <Typography variant="h6">Outlook</Typography>
                      {applyResults.results.outlook.success ? (
                        <CheckCircle color="success" sx={{ ml: 'auto' }} />
                      ) : (
                        <ErrorIcon color="error" sx={{ ml: 'auto' }} />
                      )}
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {applyResults.results.outlook.message}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>

          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
            <Button
              variant="contained"
              size="large"
              onClick={() => window.location.href = '/'}
            >
              Go to Dashboard
            </Button>
          </Box>
        </Box>
      )}
    </Container>
  );
};

export default IntegrationConfig;

// Made with Bob
