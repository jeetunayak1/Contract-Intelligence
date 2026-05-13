import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Button,
    Alert,
    Grid,
    Chip,
    LinearProgress,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Divider,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    TextField,
    Switch,
    FormControlLabel,
} from '@mui/material';
import {
    AdminPanelSettings as AdminIcon,
    GitHub as GitHubIcon,
    PlayArrow as PlayIcon,
    CheckCircle as CheckCircleIcon,
    Warning as WarningIcon,
    Delete as DeleteIcon,
    Refresh as RefreshIcon,
} from '@mui/icons-material';

interface SOW {
    _id: string;
    sow_number: string;
    client_name: string;
    project_name: string;
}

const AdminDemoData: React.FC = () => {
    const [sows, setSows] = useState<SOW[]>([]);
    const [selectedSow, setSelectedSow] = useState('');
    const [generating, setGenerating] = useState(false);
    const [progress, setProgress] = useState(0);
    const [logs, setLogs] = useState<string[]>([]);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState('');

    // Configuration options
    const [numCriticalIssues, setNumCriticalIssues] = useState(3);
    const [numHighIssues, setNumHighIssues] = useState(5);
    const [numMediumIssues, setNumMediumIssues] = useState(7);
    const [includeOverdue, setIncludeOverdue] = useState(true);
    const [includeComments, setIncludeComments] = useState(true);
    const [includeCommits, setIncludeCommits] = useState(false);

    useEffect(() => {
        fetchSOWs();
    }, []);

    const fetchSOWs = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v1/sow/list');
            const data = await response.json();
            setSows(data.sows || []);
        } catch (error) {
            console.error('Error fetching SOWs:', error);
        }
    };

    const addLog = (message: string) => {
        setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
    };

    const generateDemoData = async () => {
        if (!selectedSow) {
            setError('Please select an SOW first');
            return;
        }

        setGenerating(true);
        setProgress(0);
        setLogs([]);
        setError('');
        setResult(null);

        try {
            addLog('🚀 Starting demo data generation...');
            setProgress(10);

            // Call backend API to generate demo data
            const response = await fetch('http://localhost:8000/api/v1/admin/generate-demo-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sow_id: selectedSow,
                    num_critical_issues: numCriticalIssues,
                    num_high_issues: numHighIssues,
                    num_medium_issues: numMediumIssues,
                    include_overdue: includeOverdue,
                    include_comments: includeComments,
                    include_commits: includeCommits,
                }),
            });

            setProgress(30);
            addLog('📡 Connecting to GitHub API...');

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to generate demo data');
            }

            const data = await response.json();
            setProgress(60);
            addLog(`✅ Created ${data.issues_created} issues in GitHub`);

            if (data.comments_created) {
                addLog(`💬 Added ${data.comments_created} comments`);
            }

            if (data.commits_created) {
                addLog(`📝 Created ${data.commits_created} commits`);
            }

            setProgress(80);
            addLog('🏷️ Applied labels and milestones');

            setProgress(100);
            addLog('✨ Demo data generation complete!');

            setResult(data);
        } catch (err: any) {
            setError(err.message || 'Failed to generate demo data');
            addLog(`❌ Error: ${err.message}`);
        } finally {
            setGenerating(false);
        }
    };

    const clearDemoData = async () => {
        if (!selectedSow) {
            setError('Please select an SOW first');
            return;
        }

        if (!window.confirm('Are you sure you want to delete all demo issues? This cannot be undone!')) {
            return;
        }

        setGenerating(true);
        setLogs([]);
        setError('');

        try {
            addLog('🗑️ Clearing demo data from GitHub...');

            const response = await fetch('http://localhost:8000/api/v1/admin/clear-demo-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sow_id: selectedSow }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to clear demo data');
            }

            const data = await response.json();
            addLog(`✅ Deleted ${data.issues_deleted} issues`);
            addLog('✨ Demo data cleared successfully!');
        } catch (err: any) {
            setError(err.message || 'Failed to clear demo data');
            addLog(`❌ Error: ${err.message}`);
        } finally {
            setGenerating(false);
        }
    };

    const populateSLAData = async () => {
        setGenerating(true);
        setLogs([]);
        setError('');
        setResult(null);

        try {
            addLog('🔧 Populating SLA data for all SOWs...');

            const response = await fetch('http://localhost:8000/api/v1/admin/populate-sla-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to populate SLA data');
            }

            const data = await response.json();
            addLog(`✅ Updated ${data.sows_updated} SOWs with SLA data`);
            addLog(`💰 Total penalty exposure: $${data.total_penalty_exposure.toLocaleString()}`);
            addLog('✨ SLA data population complete!');

            setResult({
                ...data,
                message: `Successfully populated SLA data for ${data.sows_updated} SOWs`
            });
        } catch (err: any) {
            setError(err.message || 'Failed to populate SLA data');
            addLog(`❌ Error: ${err.message}`);
        } finally {
            setGenerating(false);
        }
    };

    return (
        <Box sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" gap={2} mb={3}>
                <AdminIcon sx={{ fontSize: 40, color: '#ff9800' }} />
                <Box>
                    <Typography variant="h4">Admin - Demo Data Generator</Typography>
                    <Typography variant="body2" color="text.secondary">
                        Generate realistic GitHub issues for hackathon demos
                    </Typography>
                </Box>
            </Box>

            <Alert severity="warning" sx={{ mb: 3 }}>
                <strong>⚠️ Admin Only:</strong> This page creates real issues in your GitHub repository. Use only for demos and testing.
            </Alert>

            {/* SLA Data Population Card */}
            <Card sx={{ mb: 3, bgcolor: '#e3f2fd' }}>
                <CardContent>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Box>
                            <Typography variant="h6" gutterBottom>
                                🎯 Step 1: Populate SLA Data
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Add deadlines and penalty amounts to all SOW obligations. This enables Live Monitoring to calculate real-time risk metrics.
                            </Typography>
                        </Box>
                        <Button
                            variant="contained"
                            color="info"
                            startIcon={<RefreshIcon />}
                            onClick={populateSLAData}
                            disabled={generating}
                            sx={{ minWidth: 200 }}
                        >
                            Populate SLA Data
                        </Button>
                    </Box>
                </CardContent>
            </Card>

            <Grid container spacing={3}>
                {/* Configuration Panel */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Configuration
                            </Typography>
                            <Divider sx={{ my: 2 }} />

                            <FormControl fullWidth sx={{ mb: 2 }}>
                                <InputLabel>Select SOW</InputLabel>
                                <Select
                                    value={selectedSow}
                                    onChange={(e) => setSelectedSow(e.target.value)}
                                    label="Select SOW"
                                >
                                    {sows.map((sow) => (
                                        <MenuItem key={sow._id} value={sow._id}>
                                            {sow.project_name || sow.sow_number || sow._id}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>

                            <TextField
                                fullWidth
                                type="number"
                                label="Critical Issues"
                                value={numCriticalIssues}
                                onChange={(e) => setNumCriticalIssues(parseInt(e.target.value))}
                                sx={{ mb: 2 }}
                                helperText="High penalty, urgent deadlines"
                            />

                            <TextField
                                fullWidth
                                type="number"
                                label="High Priority Issues"
                                value={numHighIssues}
                                onChange={(e) => setNumHighIssues(parseInt(e.target.value))}
                                sx={{ mb: 2 }}
                                helperText="Important deliverables"
                            />

                            <TextField
                                fullWidth
                                type="number"
                                label="Medium Priority Issues"
                                value={numMediumIssues}
                                onChange={(e) => setNumMediumIssues(parseInt(e.target.value))}
                                sx={{ mb: 2 }}
                                helperText="Standard tasks"
                            />

                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={includeOverdue}
                                        onChange={(e) => setIncludeOverdue(e.target.checked)}
                                    />
                                }
                                label="Include Overdue Issues (for risk demo)"
                                sx={{ mb: 1 }}
                            />

                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={includeComments}
                                        onChange={(e) => setIncludeComments(e.target.checked)}
                                    />
                                }
                                label="Add Comments to Issues"
                                sx={{ mb: 1 }}
                            />

                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={includeCommits}
                                        onChange={(e) => setIncludeCommits(e.target.checked)}
                                        disabled
                                    />
                                }
                                label="Create Commits (Coming Soon)"
                                sx={{ mb: 2 }}
                            />

                            <Box display="flex" gap={2}>
                                <Button
                                    variant="contained"
                                    color="primary"
                                    startIcon={<PlayIcon />}
                                    onClick={generateDemoData}
                                    disabled={generating || !selectedSow}
                                    fullWidth
                                >
                                    Generate Demo Data
                                </Button>
                                <Button
                                    variant="outlined"
                                    color="error"
                                    startIcon={<DeleteIcon />}
                                    onClick={clearDemoData}
                                    disabled={generating || !selectedSow}
                                    fullWidth
                                >
                                    Clear Data
                                </Button>
                            </Box>
                        </CardContent>
                    </Card>

                    {result && (
                        <Card sx={{ mt: 2 }}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Generation Summary
                                </Typography>
                                <Divider sx={{ my: 2 }} />
                                <Grid container spacing={2}>
                                    <Grid item xs={6}>
                                        <Box textAlign="center">
                                            <Typography variant="h3" color="primary">
                                                {result.issues_created}
                                            </Typography>
                                            <Typography variant="body2" color="text.secondary">
                                                Issues Created
                                            </Typography>
                                        </Box>
                                    </Grid>
                                    <Grid item xs={6}>
                                        <Box textAlign="center">
                                            <Typography variant="h3" color="secondary">
                                                {result.comments_created || 0}
                                            </Typography>
                                            <Typography variant="body2" color="text.secondary">
                                                Comments Added
                                            </Typography>
                                        </Box>
                                    </Grid>
                                </Grid>
                                {result.repository_url && (
                                    <Box mt={2}>
                                        <Button
                                            variant="outlined"
                                            startIcon={<GitHubIcon />}
                                            href={result.repository_url}
                                            target="_blank"
                                            fullWidth
                                        >
                                            View in GitHub
                                        </Button>
                                    </Box>
                                )}
                            </CardContent>
                        </Card>
                    )}
                </Grid>

                {/* Activity Log */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Activity Log
                            </Typography>
                            <Divider sx={{ my: 2 }} />

                            {generating && (
                                <Box sx={{ mb: 2 }}>
                                    <LinearProgress variant="determinate" value={progress} />
                                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                                        {progress}% Complete
                                    </Typography>
                                </Box>
                            )}

                            {error && (
                                <Alert severity="error" sx={{ mb: 2 }}>
                                    {error}
                                </Alert>
                            )}

                            <Box
                                sx={{
                                    maxHeight: 400,
                                    overflow: 'auto',
                                    bgcolor: '#0a0a0c',
                                    p: 2,
                                    borderRadius: 1,
                                    fontFamily: 'monospace',
                                    fontSize: '0.875rem',
                                }}
                            >
                                {logs.length === 0 ? (
                                    <Typography variant="body2" color="text.secondary">
                                        No activity yet. Click "Generate Demo Data" to start.
                                    </Typography>
                                ) : (
                                    logs.map((log, index) => (
                                        <Typography
                                            key={index}
                                            variant="body2"
                                            sx={{ color: '#00e676', mb: 0.5 }}
                                        >
                                            {log}
                                        </Typography>
                                    ))
                                )}
                            </Box>
                        </CardContent>
                    </Card>

                    <Card sx={{ mt: 2 }}>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                What Gets Created
                            </Typography>
                            <Divider sx={{ my: 2 }} />
                            <List dense>
                                <ListItem>
                                    <ListItemIcon>
                                        <CheckCircleIcon color="success" fontSize="small" />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary="GitHub Issues"
                                        secondary="With SOW-specific labels and milestones"
                                    />
                                </ListItem>
                                <ListItem>
                                    <ListItemIcon>
                                        <CheckCircleIcon color="success" fontSize="small" />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary="Due Dates"
                                        secondary="Mix of past, present, and future deadlines"
                                    />
                                </ListItem>
                                <ListItem>
                                    <ListItemIcon>
                                        <CheckCircleIcon color="success" fontSize="small" />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary="Assignees"
                                        secondary="Based on configured team members"
                                    />
                                </ListItem>
                                <ListItem>
                                    <ListItemIcon>
                                        <CheckCircleIcon color="success" fontSize="small" />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary="Comments"
                                        secondary="Realistic progress updates and discussions"
                                    />
                                </ListItem>
                                <ListItem>
                                    <ListItemIcon>
                                        <WarningIcon color="warning" fontSize="small" />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary="Overdue Items"
                                        secondary="For demonstrating risk detection"
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

export default AdminDemoData;

// Made with Bob
