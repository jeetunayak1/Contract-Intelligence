import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  Grid,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  InputAdornment,
  Link,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  GitHub as GitHubIcon,
  Save as SaveIcon,
  Visibility,
  VisibilityOff,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  OpenInNew as OpenInNewIcon,
  Send as SendIcon,
} from '@mui/icons-material';

const Settings: React.FC = () => {
  const [githubToken, setGithubToken] = useState('');
  const [slackWebhook, setSlackWebhook] = useState('');
  const [showToken, setShowToken] = useState(false);
  const [showWebhook, setShowWebhook] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState('');
  const [tokenStatus, setTokenStatus] = useState<'valid' | 'invalid' | 'unknown'>('unknown');
  const [webhookStatus, setWebhookStatus] = useState<'valid' | 'invalid' | 'unknown'>('unknown');
  const [testingSlack, setTestingSlack] = useState(false);
  const [slackTestResult, setSlackTestResult] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/settings/get');
      if (response.ok) {
        const data = await response.json();
        if (data.github_token) {
          setGithubToken('••••••••••••••••');
          setTokenStatus('valid');
        }
        if (data.slack_webhook_url) {
          setSlackWebhook('••••••••••••••••');
          setWebhookStatus('valid');
        }
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveSuccess(false);
    setSaveError('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/settings/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          github_token: githubToken,
          slack_webhook_url: slackWebhook,
        }),
      });

      if (response.ok) {
        setSaveSuccess(true);
        setTokenStatus('valid');
        if (slackWebhook && slackWebhook !== '••••••••••••••••') {
          setWebhookStatus('valid');
        }
        setTimeout(() => setSaveSuccess(false), 3000);
      } else {
        const error = await response.json();
        setSaveError(error.detail || 'Failed to save settings');
      }
    } catch (error) {
      setSaveError('Network error: Could not save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleTestSlack = async () => {
    setTestingSlack(true);
    setSlackTestResult('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/settings/test-slack', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      const data = await response.json();

      if (data.success) {
        setSlackTestResult('✅ Test notification sent successfully! Check your Slack channel.');
      } else {
        setSlackTestResult(`❌ ${data.message}`);
      }
    } catch (error) {
      setSlackTestResult('❌ Network error: Could not test Slack connection');
    } finally {
      setTestingSlack(false);
      setTimeout(() => setSlackTestResult(''), 5000);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <SettingsIcon sx={{ fontSize: 40, color: '#4caf50' }} />
        <Box>
          <Typography variant="h4">Settings</Typography>
          <Typography variant="body2" color="text.secondary">
            Configure API tokens and integration credentials
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* GitHub Configuration */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <GitHubIcon color="primary" />
                <Typography variant="h6">GitHub Integration</Typography>
              </Box>

              {saveSuccess && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  Settings saved successfully!
                </Alert>
              )}

              {saveError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {saveError}
                </Alert>
              )}

              <TextField
                fullWidth
                label="GitHub Personal Access Token"
                type={showToken ? 'text' : 'password'}
                value={githubToken}
                onChange={(e) => setGithubToken(e.target.value)}
                placeholder="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                sx={{ mb: 2 }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowToken(!showToken)}
                        edge="end"
                      >
                        {showToken ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              <Box display="flex" alignItems="center" gap={1} mb={2}>
                {tokenStatus === 'valid' && (
                  <Alert severity="success" icon={<CheckCircleIcon />} sx={{ flex: 1 }}>
                    Token configured
                  </Alert>
                )}
                {tokenStatus === 'unknown' && (
                  <Alert severity="warning" icon={<WarningIcon />} sx={{ flex: 1 }}>
                    No token configured
                  </Alert>
                )}
              </Box>

              <Button
                variant="contained"
                color="primary"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={saving || !githubToken}
                fullWidth
              >
                {saving ? 'Saving...' : 'Save Settings'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Instructions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                How to Get GitHub Token
              </Typography>
              <Divider sx={{ my: 2 }} />
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <Typography variant="body2" color="primary">1</Typography>
                  </ListItemIcon>
                  <ListItemText
                    primary="Go to GitHub Settings"
                    secondary={
                      <Link
                        href="https://github.com/settings/tokens"
                        target="_blank"
                        rel="noopener noreferrer"
                        sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                      >
                        Open GitHub Tokens <OpenInNewIcon fontSize="small" />
                      </Link>
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Typography variant="body2" color="primary">2</Typography>
                  </ListItemIcon>
                  <ListItemText
                    primary="Generate new token (classic)"
                    secondary="Click 'Generate new token (classic)'"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Typography variant="body2" color="primary">3</Typography>
                  </ListItemIcon>
                  <ListItemText
                    primary="Select scopes"
                    secondary="Check: repo, write:org, admin:repo_hook"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Typography variant="body2" color="primary">4</Typography>
                  </ListItemIcon>
                  <ListItemText
                    primary="Copy token"
                    secondary="Copy and paste it above"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>

          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Required Permissions
              </Typography>
              <Divider sx={{ my: 2 }} />
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary="repo"
                    secondary="Full control of repositories"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary="write:org"
                    secondary="Read and write org membership"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary="admin:repo_hook"
                    secondary="Full control of repository hooks"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Slack Configuration */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <SendIcon color="secondary" />
                <Typography variant="h6">Slack Integration</Typography>
              </Box>

              <TextField
                fullWidth
                label="Slack Webhook URL"
                type={showWebhook ? 'text' : 'password'}
                value={slackWebhook}
                onChange={(e) => setSlackWebhook(e.target.value)}
                placeholder="https://hooks.slack.com/services/..."
                sx={{ mb: 2 }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowWebhook(!showWebhook)}
                        edge="end"
                      >
                        {showWebhook ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              <Box display="flex" alignItems="center" gap={1} mb={2}>
                {webhookStatus === 'valid' && (
                  <Alert severity="success" icon={<CheckCircleIcon />} sx={{ flex: 1 }}>
                    Webhook configured
                  </Alert>
                )}
                {webhookStatus === 'unknown' && (
                  <Alert severity="warning" icon={<WarningIcon />} sx={{ flex: 1 }}>
                    No webhook configured
                  </Alert>
                )}
              </Box>

              {slackTestResult && (
                <Alert severity={slackTestResult.includes('✅') ? 'success' : 'error'} sx={{ mb: 2 }}>
                  {slackTestResult}
                </Alert>
              )}

              <Box display="flex" gap={2}>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<SaveIcon />}
                  onClick={handleSave}
                  disabled={saving}
                  sx={{ flex: 1 }}
                >
                  {saving ? 'Saving...' : 'Save Settings'}
                </Button>
                <Button
                  variant="outlined"
                  color="secondary"
                  startIcon={<SendIcon />}
                  onClick={handleTestSlack}
                  disabled={testingSlack || webhookStatus === 'unknown'}
                  sx={{ flex: 1 }}
                >
                  {testingSlack ? 'Testing...' : 'Test Slack'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Slack Instructions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                How to Get Slack Webhook
              </Typography>
              <Divider sx={{ my: 2 }} />
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <Typography variant="body2" color="secondary">1</Typography>
                  </ListItemIcon>
                  <ListItemText
                    primary="Go to Slack API"
                    secondary={
                      <Link
                        href="https://api.slack.com/messaging/webhooks"
                        target="_blank"
                        rel="noopener noreferrer"
                        sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                      >
                        Open Slack Webhooks <OpenInNewIcon fontSize="small" />
                      </Link>
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Typography variant="body2" color="secondary">2</Typography>
                  </ListItemIcon>
                  <ListItemText
                    primary="Create Incoming Webhook"
                    secondary="Click 'Create your Slack app'"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Typography variant="body2" color="secondary">3</Typography>
                  </ListItemIcon>
                  <ListItemText
                    primary="Select channel"
                    secondary="Choose where notifications will be sent"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Typography variant="body2" color="secondary">4</Typography>
                  </ListItemIcon>
                  <ListItemText
                    primary="Copy webhook URL"
                    secondary="Copy and paste it above"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>

          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Notification Types
              </Typography>
              <Divider sx={{ my: 2 }} />
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="error" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary="SLA Breach Alerts"
                    secondary="Critical SLA violations"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="warning" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Penalty Warnings"
                    secondary="High penalty exposure"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="info" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Daily Summaries"
                    secondary="SOW monitoring reports"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Settings;

// Made with Bob
