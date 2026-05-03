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
  key_stakeholders: string[];
}

interface GitHubLabel {
  name: string;
  color: string;
  description: string;
}

interface SlackChannel {
  name: string;
  description: string;
  is_private: boolean;
}

interface TeamMember {
  name: string;
  email: string;
  role: string;
  notify_on: string[];
}

interface ConfigurationResponse {
  sow_id: string;
  suggested_config: {
    github?: {
      repository_owner: string;
      repository_name: string;
      labels: GitHubLabel[];
      milestone_name: string;
    };
    slack?: {
      workspace_id: string;
      channels: SlackChannel[];
      alert_channel: string;
    };
    outlook?: {
      team_members: TeamMember[];
      calendar_name: string;
    };
  };
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
    key_stakeholders: [],
  });
  const [configuration, setConfiguration] = useState<ConfigurationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [applyResults, setApplyResults] = useState<any>(null);
  const [newStakeholder, setNewStakeholder] = useState('');
  const [existingConfig, setExistingConfig] = useState<ConfigurationResponse | null>(null);
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
          // Populate form with existing data
          if (data.github) {
            setTeamInfo(prev => ({
              ...prev,
              github_repo: `${data.github.repository_owner}/${data.github.repository_name}`
            }));
          }
          if (data.slack) {
            setTeamInfo(prev => ({
              ...prev,
              slack_workspace: data.slack.workspace_id
            }));
          }
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
      setActiveStep(2);
    } catch (error) {
      console.error('Failed to apply configuration:', error);
    } finally {
      setApplying(false);
    }
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

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          <AutoAwesome sx={{ mr: 1, verticalAlign: 'middle' }} />
          AI-Powered Integration Configuration
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Let AI configure GitHub, Slack, and Outlook integrations for your SOW
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

      {/* Step 1: Team Information */}
      {activeStep === 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Tell us about your team
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Provide team information and AI will suggest optimal integration configuration
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="SOW ID"
                value={sowId}
                onChange={(e) => setSowId(e.target.value)}
                helperText="Statement of Work identifier"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Project Manager"
                value={teamInfo.project_manager}
                onChange={(e) => setTeamInfo({ ...teamInfo, project_manager: e.target.value })}
                helperText="Format: Name <email@example.com>"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Tech Lead"
                value={teamInfo.tech_lead}
                onChange={(e) => setTeamInfo({ ...teamInfo, tech_lead: e.target.value })}
                helperText="Format: Name <email@example.com>"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Team Size"
                value={teamInfo.team_size}
                onChange={(e) => setTeamInfo({ ...teamInfo, team_size: parseInt(e.target.value) })}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="GitHub Repository"
                value={teamInfo.github_repo}
                onChange={(e) => setTeamInfo({ ...teamInfo, github_repo: e.target.value })}
                helperText="Format: owner/repository"
                InputProps={{
                  startAdornment: <GitHub sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Slack Workspace"
                value={teamInfo.slack_workspace}
                onChange={(e) => setTeamInfo({ ...teamInfo, slack_workspace: e.target.value })}
                InputProps={{
                  startAdornment: <Chat sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Key Stakeholders
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="email@example.com"
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
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      Milestone: {configuration.suggested_config.github.milestone_name}
                    </Typography>
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
                    <Typography variant="subtitle2" color="text.secondary">
                      Workspace: {configuration.suggested_config.slack.workspace_id}
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Channels
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
