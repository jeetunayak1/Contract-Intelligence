import React, { useEffect, useState } from 'react';
import {
    Box,
    Card,
    CardContent,
    Container,
    Grid,
    Typography,
    CircularProgress,
    LinearProgress,
    Chip,
    Paper,
    Stack,
    Avatar,
    Button,
    Alert,
    Divider,
} from '@mui/material';
import {
    TrendingUp,
    Warning,
    CheckCircle,
    Error as ErrorIcon,
    AttachMoney,
    Schedule,
    Assessment,
    Psychology,
    Security,
    Gavel,
    TipsAndUpdates,
} from '@mui/icons-material';
import { toast } from 'react-toastify';

const API_BASE = 'http://localhost:8000/api/v1';

interface DashboardData {
    sow_id: string;
    sow_info: {
        sow_number: string;
        client_name: string;
        project_name: string;
    };
    agents: {
        contract: any;
        compliance: any;
        risk: any;
        forecast: any;
    };
    metrics: {
        sla_health: any;
        penalty_exposure: any;
        scope_burn: any;
        breach_risk: any;
        margin_forecast: any;
    };
    recommendations: any[];
    change_order: any;
    generated_at: string;
}

const LiveMonitoring: React.FC = () => {
    const [loading, setLoading] = useState(true);
    const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
    const [selectedSowId, setSelectedSowId] = useState<string>('');
    const [sows, setSows] = useState<any[]>([]);

    useEffect(() => {
        loadSows();
    }, []);

    useEffect(() => {
        if (selectedSowId) {
            loadDashboard(selectedSowId);
        }
    }, [selectedSowId]);

    const loadSows = async () => {
        try {
            const response = await fetch(`${API_BASE}/sow/list`);
            const data = await response.json();
            const sowList = data.sows || [];
            setSows(sowList);
            if (sowList.length > 0 && !selectedSowId) {
                setSelectedSowId(sowList[0]._id);
            }
        } catch (error) {
            console.error('Failed to load SOWs:', error);
            toast.error('Failed to load SOWs');
        }
    };

    const loadDashboard = async (sowId: string) => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/monitoring/live-dashboard/${sowId}`);
            if (!response.ok) throw new Error('Failed to load dashboard');
            const data = await response.json();
            setDashboardData(data);
        } catch (error) {
            console.error('Failed to load dashboard:', error);
            toast.error('Failed to load monitoring dashboard');
        } finally {
            setLoading(false);
        }
    };

    const getHealthColor = (score: number) => {
        if (score >= 90) return '#00e676';
        if (score >= 70) return '#ff9800';
        return '#ff1744';
    };

    const getRiskColor = (probability: number) => {
        if (probability >= 0.7) return '#ff1744';
        if (probability >= 0.4) return '#ff9800';
        return '#00e676';
    };

    if (loading && !dashboardData) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
                <CircularProgress />
            </Container>
        );
    }

    if (!dashboardData) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4 }}>
                <Alert severity="info">Select an SOW to view live monitoring dashboard</Alert>
            </Container>
        );
    }

    const { metrics, agents, recommendations, change_order, sow_info } = dashboardData;

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h3" sx={{ fontWeight: 800, mb: 1 }}>
                    Live <span className="gradient-text">Monitoring</span>
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    Real-time multi-agent analysis for {sow_info.project_name}
                </Typography>
            </Box>

            {/* SOW Selector */}
            <Paper className="glass-card" sx={{ p: 3, mb: 4 }}>
                <Typography variant="h6" sx={{ fontWeight: 800, mb: 2 }}>Select SOW</Typography>
                <Stack direction="row" spacing={2} flexWrap="wrap">
                    {sows.map((sow) => (
                        <Chip
                            key={sow._id}
                            label={`${sow.project_name} (${sow.client_name})`}
                            onClick={() => setSelectedSowId(sow._id)}
                            color={selectedSowId === sow._id ? 'primary' : 'default'}
                            sx={{ fontWeight: selectedSowId === sow._id ? 800 : 400 }}
                        />
                    ))}
                </Stack>
            </Paper>

            {/* Agent Status Bar */}
            <Paper className="glass-card" sx={{ p: 3, mb: 4 }}>
                <Typography variant="h6" sx={{ fontWeight: 800, mb: 3 }}>Agent Status</Typography>
                <Grid container spacing={2}>
                    {Object.values(agents).map((agent: any, idx) => (
                        <Grid item xs={12} md={3} key={idx}>
                            <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'rgba(0, 230, 118, 0.05)', borderRadius: 3 }}>
                                <Avatar sx={{ mx: 'auto', mb: 1, bgcolor: 'primary.main', width: 48, height: 48 }}>
                                    <Psychology />
                                </Avatar>
                                <Typography variant="subtitle2" sx={{ fontWeight: 800 }}>{agent.name}</Typography>
                                <Typography variant="caption" color="text.secondary">{agent.description}</Typography>
                                <Chip label={agent.status} size="small" color="success" sx={{ mt: 1, fontWeight: 700 }} />
                            </Box>
                        </Grid>
                    ))}
                </Grid>
            </Paper>

            {/* Main Metrics Grid */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                {/* SLA Health */}
                <Grid item xs={12} md={3}>
                    <Card className="glass-card" sx={{ height: '100%' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                                    <CheckCircle />
                                </Avatar>
                                <Box>
                                    <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 800 }}>
                                        SLA Health
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">Live meters</Typography>
                                </Box>
                            </Box>
                            <Typography variant="h2" sx={{ fontWeight: 900, color: getHealthColor(metrics.sla_health.overall_score), mb: 2 }}>
                                {metrics.sla_health.overall_score}%
                            </Typography>
                            <LinearProgress
                                variant="determinate"
                                value={metrics.sla_health.overall_score}
                                sx={{
                                    height: 10,
                                    borderRadius: 5,
                                    bgcolor: 'rgba(255,255,255,0.05)',
                                    '& .MuiLinearProgress-bar': {
                                        bgcolor: getHealthColor(metrics.sla_health.overall_score)
                                    }
                                }}
                            />
                            <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
                                <Box>
                                    <Typography variant="h6" sx={{ fontWeight: 800, color: '#00e676' }}>{metrics.sla_health.compliant}</Typography>
                                    <Typography variant="caption" color="text.secondary">Compliant</Typography>
                                </Box>
                                <Box>
                                    <Typography variant="h6" sx={{ fontWeight: 800, color: '#ff9800' }}>{metrics.sla_health.at_risk}</Typography>
                                    <Typography variant="caption" color="text.secondary">At Risk</Typography>
                                </Box>
                                <Box>
                                    <Typography variant="h6" sx={{ fontWeight: 800, color: '#ff1744' }}>{metrics.sla_health.breached}</Typography>
                                    <Typography variant="caption" color="text.secondary">Breached</Typography>
                                </Box>
                            </Stack>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Penalty Exposure */}
                <Grid item xs={12} md={3}>
                    <Card className="glass-card" sx={{ height: '100%' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Avatar sx={{ bgcolor: 'secondary.main', mr: 2 }}>
                                    <AttachMoney />
                                </Avatar>
                                <Box>
                                    <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 800 }}>
                                        Penalty Exposure
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">$ counter, live</Typography>
                                </Box>
                            </Box>
                            <Typography variant="h2" sx={{ fontWeight: 900, color: 'secondary.main', mb: 1 }}>
                                ${metrics.penalty_exposure.total.toLocaleString()}
                            </Typography>
                            <Chip
                                label={metrics.penalty_exposure.trend.toUpperCase()}
                                size="small"
                                color={metrics.penalty_exposure.trend === 'increasing' ? 'error' : 'success'}
                                sx={{ fontWeight: 700, mb: 2 }}
                            />
                            <Divider sx={{ my: 2 }} />
                            <Stack spacing={1}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <Typography variant="body2" color="text.secondary">Immediate</Typography>
                                    <Typography variant="body2" sx={{ fontWeight: 700 }}>${metrics.penalty_exposure.immediate.toLocaleString()}</Typography>
                                </Box>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <Typography variant="body2" color="text.secondary">Potential</Typography>
                                    <Typography variant="body2" sx={{ fontWeight: 700 }}>${metrics.penalty_exposure.potential.toLocaleString()}</Typography>
                                </Box>
                            </Stack>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Scope Burn */}
                <Grid item xs={12} md={3}>
                    <Card className="glass-card" sx={{ height: '100%' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                                    <Schedule />
                                </Avatar>
                                <Box>
                                    <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 800 }}>
                                        Scope Burn
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">Hours vs contract</Typography>
                                </Box>
                            </Box>
                            <Typography variant="h2" sx={{ fontWeight: 900, color: 'warning.main', mb: 1 }}>
                                {metrics.scope_burn.burn_percentage}%
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                {metrics.scope_burn.hours_burned} / {metrics.scope_burn.contract_hours} hours
                            </Typography>
                            <LinearProgress
                                variant="determinate"
                                value={metrics.scope_burn.burn_percentage}
                                sx={{
                                    height: 10,
                                    borderRadius: 5,
                                    bgcolor: 'rgba(255,255,255,0.05)',
                                    '& .MuiLinearProgress-bar': {
                                        bgcolor: 'warning.main'
                                    }
                                }}
                            />
                            {metrics.scope_burn.out_of_scope_items > 0 && (
                                <Alert severity="warning" sx={{ mt: 2, bgcolor: 'rgba(255, 152, 0, 0.1)' }}>
                                    {metrics.scope_burn.out_of_scope_items} out-of-scope items (${metrics.scope_burn.out_of_scope_value.toLocaleString()})
                                </Alert>
                            )}
                        </CardContent>
                    </Card>
                </Grid>

                {/* Breach Risk */}
                <Grid item xs={12} md={3}>
                    <Card className="glass-card" sx={{ height: '100%' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Avatar sx={{ bgcolor: getRiskColor(metrics.breach_risk.probability), mr: 2 }}>
                                    <Warning />
                                </Avatar>
                                <Box>
                                    <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 800 }}>
                                        Breach Risk
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">% probability</Typography>
                                </Box>
                            </Box>
                            <Typography variant="h2" sx={{ fontWeight: 900, color: getRiskColor(metrics.breach_risk.probability), mb: 1 }}>
                                {metrics.breach_risk.probability_percentage}%
                            </Typography>
                            <Chip
                                label={metrics.breach_risk.risk_level.toUpperCase()}
                                size="small"
                                sx={{
                                    fontWeight: 700,
                                    mb: 2,
                                    bgcolor: `${getRiskColor(metrics.breach_risk.probability)}20`,
                                    color: getRiskColor(metrics.breach_risk.probability)
                                }}
                            />
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                                Risk Factors:
                            </Typography>
                            {metrics.breach_risk.risk_factors.slice(0, 2).map((factor: any, idx: number) => (
                                <Typography key={idx} variant="body2" sx={{ fontSize: '0.75rem', mb: 0.5 }}>
                                    • {factor.factor}
                                </Typography>
                            ))}
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* AI Recommendation Panel */}
            <Paper className="glass-card" sx={{ p: 4, mb: 4, border: '2px solid', borderColor: 'primary.main' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <Avatar sx={{ bgcolor: 'primary.main', mr: 2, width: 56, height: 56 }}>
                        <TipsAndUpdates sx={{ fontSize: 32 }} />
                    </Avatar>
                    <Box>
                        <Typography variant="h5" sx={{ fontWeight: 800 }}>AI Recommendation Panel</Typography>
                        <Typography variant="body2" color="text.secondary">Actionable alerts • Liability flip detection • Draft change orders</Typography>
                    </Box>
                </Box>

                {recommendations.length === 0 ? (
                    <Alert severity="success" sx={{ bgcolor: 'rgba(0, 230, 118, 0.1)' }}>
                        No critical recommendations at this time. All metrics within acceptable ranges.
                    </Alert>
                ) : (
                    <Stack spacing={2}>
                        {recommendations.map((rec, idx) => (
                            <Card key={idx} sx={{ bgcolor: rec.priority === 'critical' ? 'rgba(255, 23, 68, 0.1)' : 'rgba(255, 152, 0, 0.1)' }}>
                                <CardContent>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                            {rec.priority === 'critical' ? <ErrorIcon color="error" /> : <Warning color="warning" />}
                                            <Box>
                                                <Typography variant="h6" sx={{ fontWeight: 800 }}>{rec.title}</Typography>
                                                <Typography variant="body2" color="text.secondary">{rec.description}</Typography>
                                            </Box>
                                        </Box>
                                        <Chip
                                            label={rec.priority.toUpperCase()}
                                            color={rec.priority === 'critical' ? 'error' : 'warning'}
                                            sx={{ fontWeight: 700 }}
                                        />
                                    </Box>
                                    <Typography variant="caption" sx={{ fontWeight: 800, color: 'text.secondary', textTransform: 'uppercase', display: 'block', mb: 1 }}>
                                        Recommended Actions:
                                    </Typography>
                                    <Stack spacing={0.5}>
                                        {rec.actions.map((action: string, i: number) => (
                                            <Typography key={i} variant="body2">• {action}</Typography>
                                        ))}
                                    </Stack>
                                </CardContent>
                            </Card>
                        ))}
                    </Stack>
                )}

                {/* Change Order Section */}
                {change_order.has_change_order && (
                    <Box sx={{ mt: 3, p: 3, bgcolor: 'rgba(0, 230, 118, 0.05)', borderRadius: 3, border: '1px solid rgba(0, 230, 118, 0.2)' }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                            <Box>
                                <Typography variant="h6" sx={{ fontWeight: 800, color: 'primary.main' }}>
                                    <Gavel sx={{ verticalAlign: 'middle', mr: 1 }} />
                                    Change Order Draft Ready
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {change_order.item_count} out-of-scope items • Total Value: ${change_order.total_value.toLocaleString()}
                                </Typography>
                            </Box>
                            <Button variant="contained" color="primary" sx={{ borderRadius: 2, fontWeight: 700 }}>
                                Review Draft
                            </Button>
                        </Box>
                    </Box>
                )}
            </Paper>

            {/* Margin Forecast */}
            <Card className="glass-card">
                <CardContent sx={{ p: 4 }}>
                    <Typography variant="h6" sx={{ fontWeight: 800, mb: 3 }}>Margin Forecast</Typography>
                    <Grid container spacing={3}>
                        <Grid item xs={12} md={4}>
                            <Box sx={{ textAlign: 'center', p: 3, bgcolor: 'rgba(0, 230, 118, 0.05)', borderRadius: 3 }}>
                                <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 800 }}>
                                    Current Margin
                                </Typography>
                                <Typography variant="h3" sx={{ fontWeight: 900, color: 'primary.main', my: 1 }}>
                                    {metrics.margin_forecast.current_margin_percentage}%
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    ${metrics.margin_forecast.current_margin.toLocaleString()}
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <Box sx={{ textAlign: 'center', p: 3, bgcolor: 'rgba(255, 152, 0, 0.05)', borderRadius: 3 }}>
                                <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 800 }}>
                                    Projected Margin
                                </Typography>
                                <Typography variant="h3" sx={{ fontWeight: 900, color: 'warning.main', my: 1 }}>
                                    {metrics.margin_forecast.projected_margin_percentage}%
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    ${metrics.margin_forecast.projected_margin.toLocaleString()}
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <Box sx={{ textAlign: 'center', p: 3, bgcolor: 'rgba(255, 23, 68, 0.05)', borderRadius: 3 }}>
                                <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 800 }}>
                                    Margin Erosion
                                </Typography>
                                <Typography variant="h3" sx={{ fontWeight: 900, color: 'secondary.main', my: 1 }}>
                                    ${metrics.margin_forecast.margin_erosion.toLocaleString()}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {metrics.margin_forecast.at_risk ? '⚠️ At Risk' : '✓ Healthy'}
                                </Typography>
                            </Box>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>
        </Container>
    );
};

export default LiveMonitoring;

// Made with Bob
