import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  Alert,
  Divider,
  Card,
  CardContent,
  IconButton,
  InputAdornment,
} from '@mui/material';
import {
  Save,
  Visibility,
  VisibilityOff,
  GitHub,
  Chat,
  Email,
  CheckCircle,
} from '@mui/icons-material';

interface APISettings {
  github_token: string;
  github_owner: string;
  github_repo: string;
  slack_bot_token: string;
  slack_workspace_id: string;
  microsoft_client_id: string;
  microsoft_client_secret: string;
  microsoft_tenant_id: string;
}

const Settings: React.FC = () => {
  const [settings, setSettings] = useState<APISettings>({
    github_token: '',
    github_owner: '',
    github_repo: '',
    slack_bot_token: '',
    slack_workspace_id: '',
    microsoft_client_id: '',
    microsoft_client_secret: '',
    microsoft_tenant_id: '',
  });
  
  const [showTokens, setShowTokens] = useState({
    github: false,
    slack: false,
    microsoft_secret: false,
  });
  
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('api_settings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
    }
  }, []);

  const handleSave = () => {
    try {
      // Save to localStorage
      localStorage.setItem('api_settings', JSON.stringify(settings));
      setSaved(true);
      setError('');
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      setError('Failed to save settings');
    }
  };

  const handleChange = (field: keyof APISettings) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setSettings({ ...settings, [field]: event.target.value });
  };

  const toggleShowToken = (field: keyof typeof showTokens) => {
    setShowTokens({ ...showTokens, [field]: !showTokens[field] });
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          API Configuration Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure your API keys and credentials for GitHub, Slack, and Outlook integrations
        </Typography>
      </Box>

      {saved && (
        <Alert severity="success" sx={{ mb: 3 }} icon={<CheckCircle />}>
          Settings saved successfully!
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* GitHub Settings */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <GitHub sx={{ mr: 2, fontSize: 32 }} />
            <Typography variant="h6">GitHub Configuration</Typography>
          </Box>
          
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Personal Access Token"
                type={showTokens.github ? 'text' : 'password'}
                value={settings.github_token}
                onChange={handleChange('github_token')}
                placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                helperText="Create at: Settings → Developer settings → Personal access tokens"
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => toggleShowToken('github')} edge="end">
                        {showTokens.github ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Repository Owner"
                value={settings.github_owner}
                onChange={handleChange('github_owner')}
                placeholder="your-username or organization"
                helperText="GitHub username or organization name"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Repository Name"
                value={settings.github_repo}
                onChange={handleChange('github_repo')}
                placeholder="repository-name"
                helperText="Default repository for SOW tracking"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Slack Settings */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Chat sx={{ mr: 2, fontSize: 32 }} />
            <Typography variant="h6">Slack Configuration</Typography>
          </Box>
          
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Bot Token"
                type={showTokens.slack ? 'text' : 'password'}
                value={settings.slack_bot_token}
                onChange={handleChange('slack_bot_token')}
                placeholder="xoxb-xxxxxxxxxxxx-xxxxxxxxxxxx"
                helperText="Create at: api.slack.com → Your Apps → OAuth & Permissions"
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => toggleShowToken('slack')} edge="end">
                        {showTokens.slack ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Workspace ID"
                value={settings.slack_workspace_id}
                onChange={handleChange('slack_workspace_id')}
                placeholder="T1234567890"
                helperText="Find in Slack workspace settings"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Microsoft/Outlook Settings */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Email sx={{ mr: 2, fontSize: 32 }} />
            <Typography variant="h6">Microsoft Graph API (Outlook)</Typography>
          </Box>
          
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Client ID"
                value={settings.microsoft_client_id}
                onChange={handleChange('microsoft_client_id')}
                placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                helperText="Azure AD App Registration → Application (client) ID"
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Client Secret"
                type={showTokens.microsoft_secret ? 'text' : 'password'}
                value={settings.microsoft_client_secret}
                onChange={handleChange('microsoft_client_secret')}
                placeholder="Client secret value"
                helperText="Azure AD App Registration → Certificates & secrets"
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => toggleShowToken('microsoft_secret')} edge="end">
                        {showTokens.microsoft_secret ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Tenant ID"
                value={settings.microsoft_tenant_id}
                onChange={handleChange('microsoft_tenant_id')}
                placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                helperText="Azure AD → Directory (tenant) ID"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Setup Instructions */}
      <Paper sx={{ p: 3, mb: 3, bgcolor: 'background.default' }}>
        <Typography variant="h6" gutterBottom>
          Setup Instructions
        </Typography>
        <Divider sx={{ my: 2 }} />
        
        <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
          GitHub Personal Access Token:
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          1. Go to GitHub Settings → Developer settings → Personal access tokens<br />
          2. Generate new token (classic)<br />
          3. Select scopes: repo, admin:org, write:discussion<br />
          4. Copy and paste the token above
        </Typography>

        <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
          Slack Bot Token:
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          1. Go to api.slack.com → Your Apps<br />
          2. Create new app or select existing<br />
          3. OAuth & Permissions → Bot Token Scopes<br />
          4. Add: channels:manage, channels:write, chat:write<br />
          5. Install app to workspace and copy Bot User OAuth Token
        </Typography>

        <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
          Microsoft Graph API:
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          1. Go to Azure Portal → Azure Active Directory<br />
          2. App registrations → New registration<br />
          3. API permissions → Add: Calendars.ReadWrite, User.Read.All<br />
          4. Certificates & secrets → New client secret<br />
          5. Copy Application ID, Tenant ID, and Client Secret
        </Typography>
      </Paper>

      {/* Save Button */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<Save />}
          onClick={handleSave}
        >
          Save Settings
        </Button>
      </Box>
    </Container>
  );
};

export default Settings;

// Made with Bob
