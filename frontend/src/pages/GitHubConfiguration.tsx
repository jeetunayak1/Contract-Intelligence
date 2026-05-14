import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    TextField,
    Button,
    Grid,
    Chip,
    Alert,
    Stepper,
    Step,
    StepLabel,
    FormControlLabel,
    Switch,
    IconButton,
    Divider,
    List,
    ListItem,
    ListItemText,
    ListItemSecondaryAction,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    CircularProgress,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
} from '@mui/material';
import {
    GitHub as GitHubIcon,
    Add as AddIcon,
    Delete as DeleteIcon,
    Save as SaveIcon,
    CheckCircle as CheckCircleIcon,
    Warning as WarningIcon,
    ExpandMore as ExpandMoreIcon,
    Settings as SettingsIcon,
    Label as LabelIcon,
    Assignment as AssignmentIcon,
} from '@mui/icons-material';

interface SOW {
    _id: string;
    sow_number: string;
    client_name: string;
    project_name: string;
    status: string;
}

interface GitHubLabel {
    name: string;
    color: string;
    description: string;
}

interface GitHubConfig {
    sow_id: string;
    repository_owner: string;
    repository_name: string;
    labels: GitHubLabel[];
    milestone_name: string;
    project_board_name: string;
    issue_template: {
        title_prefix: string;
        body_intro: string;
        default_labels: string[];
        assignees: string[];
    };
    automation: {
        create_labels: boolean;
        create_milestone: boolean;
        create_issue_templates: boolean;
        auto_create_obligation_issues: boolean;
        auto_create_review_issue: boolean;
    };
    pre_acceptance_repo: {
        repository_owner: string;
        repository_name: string;
        purpose: string;
        stage: string;
    } | null;
    delivery_repo: {
        repository_owner: string;
        repository_name: string;
        purpose: string;
        stage: string;
    } | null;
    configured: boolean;
    configured_at?: string;
}

const GitHubConfiguration: React.FC = () => {
    const [sows, setSows] = useState<SOW[]>([]);
    const [selectedSow, setSelectedSow] = useState<string>('');
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [activeStep, setActiveStep] = useState(0);
    const [config, setConfig] = useState<GitHubConfig | null>(null);
    const [teamInfo, setTeamInfo] = useState({
        project_manager: '',
        tech_lead: '',
        team_size: 5,
        github_repo: '',
        pre_acceptance_github_repo: '',
        delivery_github_repo: '',
        slack_workspace: '',
        key_stakeholders: [] as string[],
    });
    const [newStakeholder, setNewStakeholder] = useState('');
    const [applyResult, setApplyResult] = useState<any>(null);
    const [showApplyDialog, setShowApplyDialog] = useState(false);

    const steps = ['Select SOW', 'Team Information', 'GitHub Repositories', 'Review & Apply'];

    useEffect(() => {
        fetchSOWs();
    }, []);

    useEffect(() => {
        if (selectedSow) {
            fetchExistingConfig();
        }
    }, [selectedSow]);

    const fetchSOWs = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v1/sow/list');
            const data = await response.json();
            console.log('Fetched SOWs:', data.sows);
            setSows(data.sows || []);
        } catch (error) {
            console.error('Error fetching SOWs:', error);
        }
    };

    const fetchExistingConfig = async () => {
        console.log('Fetching config for SOW:', selectedSow);
        try {
            const response = await fetch(`http://localhost:8000/api/v1/integrations/${selectedSow}`);
            if (response.ok) {
                const data = await response.json();
                console.log('Found existing configuration:', data);
                setConfig(data.github);
                if (data.team_info) {
                    setTeamInfo({
                        ...teamInfo,
                        ...data.team_info,
                        key_stakeholders: data.team_info.key_stakeholders || [],
                    });
                }
            } else if (response.status === 404) {
                console.log('No existing configuration for this SOW - will create new one');
                // Reset config and team info for new configuration
                setConfig(null);
                setTeamInfo({
                    project_manager: '',
                    tech_lead: '',
                    team_size: 5,
                    github_repo: '',
                    pre_acceptance_github_repo: '',
                    delivery_github_repo: '',
                    slack_workspace: '',
                    key_stakeholders: [],
                });
            }
        } catch (error) {
            console.log('Error fetching configuration:', error);
        }
    };

    const generateConfiguration = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/v1/integrations/configure', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sow_id: selectedSow,
                    team_info: teamInfo,
                }),
            });
            const data = await response.json();
            setConfig(data.suggested_config.github);
            setActiveStep(3);
        } catch (error) {
            console.error('Error generating configuration:', error);
        } finally {
            setLoading(false);
        }
    };

    const applyConfiguration = async () => {
        if (!config) return;

        setSaving(true);
        try {
            const fullConfig = {
                sow_id: selectedSow,
                team_info: teamInfo,
                github: config,
                slack: null,
                outlook: null,
            };

            const response = await fetch(`http://localhost:8000/api/v1/integrations/apply/${selectedSow}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(fullConfig),
            });
            const result = await response.json();
            setApplyResult(result);
            setShowApplyDialog(true);
        } catch (error) {
            console.error('Error applying configuration:', error);
        } finally {
            setSaving(false);
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

    const handleNext = () => {
        if (activeStep === 2) {
            generateConfiguration();
        } else {
            setActiveStep((prev) => prev + 1);
        }
    };

    const handleBack = () => {
        setActiveStep((prev) => prev - 1);
    };

    const renderStepContent = () => {
        switch (activeStep) {
            case 0:
                return (
                    <Box>
                        <Typography variant="h6" gutterBottom>
                            Select SOW for GitHub Configuration
                        </Typography>
                        {selectedSow && (
                            <Alert severity="info" sx={{ mb: 2 }}>
                                Selected SOW: <strong>{selectedSow}</strong>
                            </Alert>
                        )}
                        <Grid container spacing={2}>
                            {sows.map((sow) => (
                                <Grid item xs={12} md={6} key={sow._id}>
                                    <Card
                                        sx={{
                                            cursor: 'pointer',
                                            border: (selectedSow && selectedSow === sow._id) ? '2px solid #4caf50' : '1px solid #ddd',
                                            '&:hover': { boxShadow: 3 },
                                        }}
                                        onClick={() => {
                                            console.log('Clicked SOW ID:', sow._id, 'SOW Number:', sow.sow_number, 'Current selected:', selectedSow);
                                            if (sow._id) {
                                                setSelectedSow(sow._id);
                                            } else {
                                                console.error('SOW ID is missing:', sow);
                                            }
                                        }}
                                    >
                                        <CardContent>
                                            <Box display="flex" alignItems="center" gap={1}>
                                                <GitHubIcon color={(selectedSow && selectedSow === sow._id) ? 'success' : 'action'} />
                                                <Box flex={1}>
                                                    <Typography variant="h6">{sow.sow_number || sow._id}</Typography>
                                                    <Typography variant="body2" color="text.secondary">
                                                        {sow.client_name} - {sow.project_name}
                                                    </Typography>
                                                    <Typography variant="caption" color="text.secondary">
                                                        Status: {sow.status}
                                                    </Typography>
                                                </Box>
                                                {(selectedSow && selectedSow === sow._id) && (
                                                    <CheckCircleIcon color="success" />
                                                )}
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    </Box>
                );

            case 1:
                return (
                    <Box>
                        <Typography variant="h6" gutterBottom>
                            Team Information for {selectedSow}
                        </Typography>
                        <Grid container spacing={3}>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    fullWidth
                                    label="Project Manager"
                                    placeholder="John Smith <john.smith@example.com>"
                                    value={teamInfo.project_manager}
                                    onChange={(e) => setTeamInfo({ ...teamInfo, project_manager: e.target.value })}
                                    helperText="Format: Name <email@example.com>"
                                />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    fullWidth
                                    label="Tech Lead"
                                    placeholder="Jane Doe <jane.doe@example.com>"
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
                                    label="Slack Workspace"
                                    value={teamInfo.slack_workspace}
                                    onChange={(e) => setTeamInfo({ ...teamInfo, slack_workspace: e.target.value })}
                                    placeholder="acme-corp"
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <Typography variant="subtitle2" gutterBottom>
                                    Key Stakeholders
                                </Typography>
                                <Box display="flex" gap={1} mb={2}>
                                    <TextField
                                        fullWidth
                                        size="small"
                                        placeholder="stakeholder@example.com"
                                        value={newStakeholder}
                                        onChange={(e) => setNewStakeholder(e.target.value)}
                                        onKeyPress={(e) => e.key === 'Enter' && addStakeholder()}
                                    />
                                    <Button
                                        variant="contained"
                                        startIcon={<AddIcon />}
                                        onClick={addStakeholder}
                                    >
                                        Add
                                    </Button>
                                </Box>
                                <Box display="flex" flexWrap="wrap" gap={1}>
                                    {teamInfo.key_stakeholders.map((email) => (
                                        <Chip
                                            key={email}
                                            label={email}
                                            onDelete={() => removeStakeholder(email)}
                                            color="primary"
                                            variant="outlined"
                                        />
                                    ))}
                                </Box>
                            </Grid>
                        </Grid>
                    </Box>
                );

            case 2:
                return (
                    <Box>
                        <Typography variant="h6" gutterBottom>
                            GitHub Repository Configuration
                        </Typography>
                        <Alert severity="info" sx={{ mb: 3 }}>
                            Configure separate repositories for pre-acceptance (review/negotiation) and post-approval (delivery) workflows
                        </Alert>
                        <Grid container spacing={3}>
                            <Grid item xs={12}>
                                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                                    Default Repository
                                </Typography>
                                <TextField
                                    fullWidth
                                    label="GitHub Repository"
                                    placeholder="owner/repository-name"
                                    value={teamInfo.github_repo}
                                    onChange={(e) => setTeamInfo({ ...teamInfo, github_repo: e.target.value })}
                                    helperText="Format: owner/repository-name (e.g., acme-corp/platform-migration)"
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <Divider sx={{ my: 2 }} />
                                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                                    Pre-Acceptance Repository (Optional)
                                </Typography>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                    Used for SOW review, SLA negotiation, and acceptance criteria before approval
                                </Typography>
                                <TextField
                                    fullWidth
                                    label="Pre-Acceptance Repository"
                                    placeholder="owner/sow-reviews"
                                    value={teamInfo.pre_acceptance_github_repo}
                                    onChange={(e) => setTeamInfo({ ...teamInfo, pre_acceptance_github_repo: e.target.value })}
                                    helperText="Leave empty to use default repository"
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <Divider sx={{ my: 2 }} />
                                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                                    Delivery Repository (Optional)
                                </Typography>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                    Used for approved delivery execution, implementation tracking, and SLA-bound work
                                </Typography>
                                <TextField
                                    fullWidth
                                    label="Delivery Repository"
                                    placeholder="owner/delivery-tracking"
                                    value={teamInfo.delivery_github_repo}
                                    onChange={(e) => setTeamInfo({ ...teamInfo, delivery_github_repo: e.target.value })}
                                    helperText="Leave empty to use default repository"
                                />
                            </Grid>
                        </Grid>
                    </Box>
                );

            case 3:
                return (
                    <Box>
                        <Typography variant="h6" gutterBottom>
                            Review Configuration for {selectedSow}
                        </Typography>
                        {loading ? (
                            <Box display="flex" justifyContent="center" p={4}>
                                <CircularProgress />
                            </Box>
                        ) : config ? (
                            <Box>
                                <Accordion defaultExpanded>
                                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                        <Box display="flex" alignItems="center" gap={1}>
                                            <SettingsIcon color="primary" />
                                            <Typography variant="subtitle1">Repository Configuration</Typography>
                                        </Box>
                                    </AccordionSummary>
                                    <AccordionDetails>
                                        <Grid container spacing={2}>
                                            <Grid item xs={12}>
                                                <Typography variant="body2" color="text.secondary">
                                                    <strong>Default Repository:</strong> {config.repository_owner}/{config.repository_name}
                                                </Typography>
                                            </Grid>
                                            {config.pre_acceptance_repo && (
                                                <Grid item xs={12}>
                                                    <Typography variant="body2" color="text.secondary">
                                                        <strong>Pre-Acceptance:</strong> {config.pre_acceptance_repo.repository_owner}/{config.pre_acceptance_repo.repository_name}
                                                    </Typography>
                                                    <Typography variant="caption" color="text.secondary">
                                                        {config.pre_acceptance_repo.purpose}
                                                    </Typography>
                                                </Grid>
                                            )}
                                            {config.delivery_repo && (
                                                <Grid item xs={12}>
                                                    <Typography variant="body2" color="text.secondary">
                                                        <strong>Delivery:</strong> {config.delivery_repo.repository_owner}/{config.delivery_repo.repository_name}
                                                    </Typography>
                                                    <Typography variant="caption" color="text.secondary">
                                                        {config.delivery_repo.purpose}
                                                    </Typography>
                                                </Grid>
                                            )}
                                            <Grid item xs={12}>
                                                <Typography variant="body2" color="text.secondary">
                                                    <strong>Milestone:</strong> {config.milestone_name}
                                                </Typography>
                                            </Grid>
                                        </Grid>
                                    </AccordionDetails>
                                </Accordion>

                                <Accordion>
                                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                        <Box display="flex" alignItems="center" gap={1}>
                                            <LabelIcon color="primary" />
                                            <Typography variant="subtitle1">Labels ({config.labels.length})</Typography>
                                        </Box>
                                    </AccordionSummary>
                                    <AccordionDetails>
                                        <TableContainer component={Paper} variant="outlined">
                                            <Table size="small">
                                                <TableHead>
                                                    <TableRow>
                                                        <TableCell>Label Name</TableCell>
                                                        <TableCell>Color</TableCell>
                                                        <TableCell>Description</TableCell>
                                                    </TableRow>
                                                </TableHead>
                                                <TableBody>
                                                    {config.labels.map((label) => (
                                                        <TableRow key={label.name}>
                                                            <TableCell>
                                                                <Chip
                                                                    label={label.name}
                                                                    size="small"
                                                                    sx={{ bgcolor: `#${label.color}`, color: '#fff' }}
                                                                />
                                                            </TableCell>
                                                            <TableCell>#{label.color}</TableCell>
                                                            <TableCell>{label.description}</TableCell>
                                                        </TableRow>
                                                    ))}
                                                </TableBody>
                                            </Table>
                                        </TableContainer>
                                    </AccordionDetails>
                                </Accordion>

                                <Accordion>
                                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                        <Box display="flex" alignItems="center" gap={1}>
                                            <AssignmentIcon color="primary" />
                                            <Typography variant="subtitle1">Automation Settings</Typography>
                                        </Box>
                                    </AccordionSummary>
                                    <AccordionDetails>
                                        <List>
                                            <ListItem>
                                                <ListItemText primary="Create Labels" />
                                                <ListItemSecondaryAction>
                                                    <Chip
                                                        label={config.automation.create_labels ? 'Enabled' : 'Disabled'}
                                                        color={config.automation.create_labels ? 'success' : 'default'}
                                                        size="small"
                                                    />
                                                </ListItemSecondaryAction>
                                            </ListItem>
                                            <ListItem>
                                                <ListItemText primary="Create Milestone" />
                                                <ListItemSecondaryAction>
                                                    <Chip
                                                        label={config.automation.create_milestone ? 'Enabled' : 'Disabled'}
                                                        color={config.automation.create_milestone ? 'success' : 'default'}
                                                        size="small"
                                                    />
                                                </ListItemSecondaryAction>
                                            </ListItem>
                                            <ListItem>
                                                <ListItemText primary="Auto-create Obligation Issues" />
                                                <ListItemSecondaryAction>
                                                    <Chip
                                                        label={config.automation.auto_create_obligation_issues ? 'Enabled' : 'Disabled'}
                                                        color={config.automation.auto_create_obligation_issues ? 'success' : 'default'}
                                                        size="small"
                                                    />
                                                </ListItemSecondaryAction>
                                            </ListItem>
                                            <ListItem>
                                                <ListItemText primary="Auto-create Review Issue" />
                                                <ListItemSecondaryAction>
                                                    <Chip
                                                        label={config.automation.auto_create_review_issue ? 'Enabled' : 'Disabled'}
                                                        color={config.automation.auto_create_review_issue ? 'success' : 'default'}
                                                        size="small"
                                                    />
                                                </ListItemSecondaryAction>
                                            </ListItem>
                                        </List>
                                    </AccordionDetails>
                                </Accordion>

                                <Box mt={3}>
                                    <Alert severity="warning">
                                        <Typography variant="body2">
                                            <strong>Important:</strong> Applying this configuration will create labels, milestones, and issues in your GitHub repository.
                                            Make sure you have the necessary permissions and have configured your GitHub token in Settings.
                                        </Typography>
                                    </Alert>
                                </Box>
                            </Box>
                        ) : (
                            <Alert severity="info">
                                Click "Generate Configuration" to create the GitHub setup for this SOW.
                            </Alert>
                        )}
                    </Box>
                );

            default:
                return null;
        }
    };

    return (
        <Box sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" gap={2} mb={3}>
                <GitHubIcon sx={{ fontSize: 40, color: '#4caf50' }} />
                <Box>
                    <Typography variant="h4">GitHub Configuration</Typography>
                    <Typography variant="body2" color="text.secondary">
                        Configure GitHub repositories, labels, and automation for each SOW
                    </Typography>
                </Box>
            </Box>

            <Card>
                <CardContent>
                    <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
                        {steps.map((label) => (
                            <Step key={label}>
                                <StepLabel>{label}</StepLabel>
                            </Step>
                        ))}
                    </Stepper>

                    {renderStepContent()}

                    <Box display="flex" justifyContent="space-between" mt={4}>
                        <Button
                            disabled={activeStep === 0}
                            onClick={handleBack}
                        >
                            Back
                        </Button>
                        <Box display="flex" gap={2}>
                            {activeStep === 3 && config && (
                                <Button
                                    variant="contained"
                                    color="success"
                                    startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
                                    onClick={applyConfiguration}
                                    disabled={saving}
                                >
                                    {saving ? 'Applying...' : 'Apply Configuration'}
                                </Button>
                            )}
                            {activeStep < 3 && (
                                <Button
                                    variant="contained"
                                    onClick={handleNext}
                                    disabled={!selectedSow || (activeStep === 2 && loading)}
                                >
                                    {activeStep === 2 ? (loading ? 'Generating...' : 'Generate Configuration') : 'Next'}
                                </Button>
                            )}
                        </Box>
                    </Box>
                </CardContent>
            </Card>

            <Dialog open={showApplyDialog} onClose={() => setShowApplyDialog(false)} maxWidth="md" fullWidth>
                <DialogTitle>
                    <Box display="flex" alignItems="center" gap={1}>
                        {applyResult?.overall_success ? (
                            <CheckCircleIcon color="success" />
                        ) : (
                            <WarningIcon color="warning" />
                        )}
                        <Typography variant="h6">
                            Configuration {applyResult?.overall_success ? 'Applied Successfully' : 'Partially Applied'}
                        </Typography>
                    </Box>
                </DialogTitle>
                <DialogContent>
                    {applyResult && (
                        <Box>
                            <Typography variant="subtitle2" gutterBottom>
                                GitHub Results:
                            </Typography>
                            <Alert severity={applyResult.results.github.success ? 'success' : 'error'} sx={{ mb: 2 }}>
                                {applyResult.results.github.message}
                            </Alert>
                            {applyResult.results.github.created_labels && (
                                <Box mb={2}>
                                    <Typography variant="body2" gutterBottom>
                                        <strong>Created Labels:</strong>
                                    </Typography>
                                    <Box display="flex" flexWrap="wrap" gap={1}>
                                        {applyResult.results.github.created_labels.map((label: string) => (
                                            <Chip key={label} label={label} size="small" color="success" />
                                        ))}
                                    </Box>
                                </Box>
                            )}
                            {applyResult.results.github.created_issues && (
                                <Box mb={2}>
                                    <Typography variant="body2" gutterBottom>
                                        <strong>Created Issues:</strong>
                                    </Typography>
                                    <List dense>
                                        {applyResult.results.github.created_issues.map((issue: any) => (
                                            <ListItem key={issue.issue_number}>
                                                <ListItemText
                                                    primary={issue.title}
                                                    secondary={
                                                        <a href={issue.issue_url} target="_blank" rel="noopener noreferrer">
                                                            #{issue.issue_number}
                                                        </a>
                                                    }
                                                />
                                            </ListItem>
                                        ))}
                                    </List>
                                </Box>
                            )}
                        </Box>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setShowApplyDialog(false)}>Close</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default GitHubConfiguration;

// Made with Bob
