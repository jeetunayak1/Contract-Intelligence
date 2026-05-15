import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Alert,
  Tabs,
  Tab,
  Paper,
  Divider,
  Badge,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  AttachMoney as MoneyIcon,
  Speed as SpeedIcon,
  Refresh as RefreshIcon,
  FiberManualRecord as LiveIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://localhost:8000/api/v1';

interface Incident {
  incident_id: string;
  source: string;
  priority: string;
  severity: string;
  service: string;
  title: string;
  description?: string;
  status: string;
  github_issue_number?: number;
  affected_users?: number;
  estimated_revenue_impact?: number;
  sla_analysis_started: boolean;
  sla_analysis_completed: boolean;
  crew_execution_id?: string;
  crew_status?: string;
  breach_detected: boolean;
  financial_exposure: number;
  penalty_waived: boolean;
  waiver_reason?: string;
  created_at: string;
  updated_at: string;
}

interface ReasoningLog {
  log_id: string;
  incident_id: string;
  timestamp: string;
  level: string;
  message: string;
  agent?: string;
  task?: string;
}

interface Contract {
  contract_id: string;
  filename: string;
  provider: string;
  uploaded_at: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`contract-tabpanel-${index}`}
      aria-labelledby={`contract-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const WarRoom: React.FC = () => {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [activeTab, setActiveTab] = useState(0);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [reasoningLogs, setReasoningLogs] = useState<Record<string, ReasoningLog[]>>({});
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [activeAgent, setActiveAgent] = useState<{agent: string, task: string} | null>(null);

  // Load contracts on mount
  useEffect(() => {
    loadContracts();
  }, []);

  // Auto-refresh incidents every 5 seconds
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        loadIncidents();
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  // Load incidents when tab changes
  useEffect(() => {
    if (contracts.length > 0) {
      loadIncidents();
    }
  }, [activeTab, contracts]);

  const loadContracts = async () => {
    try {
      const response = await fetch(`${API_BASE}/events/incidents/live`);
      const data = await response.json();
      
      // Get unique contracts from compliance API
      const contractsResponse = await fetch(`${API_BASE}/compliance/contracts`);
      const contractsData = await contractsResponse.json();
      
      if (contractsData.success && contractsData.contracts.length > 0) {
        setContracts(contractsData.contracts);
      }
    } catch (error) {
      console.error('Failed to load contracts:', error);
    }
  };

  const loadIncidents = async () => {
    try {
      const response = await fetch(`${API_BASE}/events/incidents/live?limit=100`);
      const data = await response.json();
      
      if (data.incidents) {
        setIncidents(data.incidents);
        setLastUpdate(new Date());
        
        // Load reasoning logs for incidents that are being analyzed
        data.incidents.forEach((incident: Incident) => {
          if (incident.sla_analysis_started && !incident.sla_analysis_completed) {
            loadReasoningLogs(incident.incident_id);
          }
        });
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Failed to load incidents:', error);
      setLoading(false);
    }
  };

  const loadReasoningLogs = async (incidentId: string) => {
    try {
      const response = await fetch(`${API_BASE}/events/reasoning/${incidentId}`);
      const data = await response.json();
      
      if (data.logs) {
        setReasoningLogs(prev => ({
          ...prev,
          [incidentId]: data.logs
        }));
        
        // Extract active agent from most recent log with agent info
        const logsWithAgent = data.logs.filter((log: ReasoningLog) => log.agent && log.task);
        if (logsWithAgent.length > 0) {
          const latestLog = logsWithAgent[logsWithAgent.length - 1];
          setActiveAgent({
            agent: latestLog.agent,
            task: latestLog.task
          });
        } else {
          setActiveAgent(null);
        }
      }
    } catch (error) {
      console.error(`Failed to load reasoning logs for ${incidentId}:`, error);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
  };

  const manualRefresh = () => {
    loadIncidents();
  };

  // Get incidents for current contract
  const getCurrentContractIncidents = () => {
    if (contracts.length === 0) return incidents;
    // For now, show all incidents. In production, filter by contract_id
    return incidents;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'OPEN': return 'error';
      case 'ACKNOWLEDGED': return 'warning';
      case 'INVESTIGATING': return 'info';
      case 'RESOLVED': return 'success';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'P1':
      case 'SEV1':
      case 'CRITICAL': return '#ff1744';
      case 'P2': return '#ff9100';
      case 'P3': return '#ffc107';
      case 'P4': return '#4caf50';
      default: return '#9e9e9e';
    }
  };

  const getSeverityBadge = (severity: string) => {
    const colors: Record<string, string> = {
      'CRITICAL': '#ff1744',
      'HIGH': '#ff9100',
      'MEDIUM': '#ffc107',
      'LOW': '#4caf50'
    };
    return colors[severity] || '#9e9e9e';
  };

  const currentIncidents = getCurrentContractIncidents();
  const activeIncidents = currentIncidents.filter(i => ['OPEN', 'ACKNOWLEDGED', 'INVESTIGATING'].includes(i.status));
  const totalExposure = currentIncidents.reduce((sum, i) => sum + (i.breach_detected && !i.penalty_waived ? i.financial_exposure : 0), 0);
  const totalWaived = currentIncidents.reduce((sum, i) => sum + (i.penalty_waived ? i.financial_exposure : 0), 0);
  const breachCount = currentIncidents.filter(i => i.breach_detected).length;

  return (
    <Box sx={{ p: 3, bgcolor: '#0a0e27', minHeight: '100vh' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="h3" sx={{ fontWeight: 800, color: 'white', display: 'flex', alignItems: 'center', gap: 2 }}>
              🚨 LIVE INCIDENT FEED
              {autoRefresh && (
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ repeat: Infinity, duration: 2 }}
                >
                  <LiveIcon sx={{ color: '#00e676', fontSize: 16 }} />
                </motion.div>
              )}
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
              Last update: {lastUpdate.toLocaleTimeString()}
            </Typography>
            <Tooltip title={autoRefresh ? "Disable auto-refresh" : "Enable auto-refresh"}>
              <IconButton 
                onClick={toggleAutoRefresh}
                sx={{ 
                  color: autoRefresh ? '#00e676' : 'rgba(255,255,255,0.3)',
                  border: '1px solid',
                  borderColor: autoRefresh ? '#00e676' : 'rgba(255,255,255,0.1)'
                }}
              >
                <LiveIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Refresh now">
              <IconButton onClick={manualRefresh} sx={{ color: 'white', border: '1px solid rgba(255,255,255,0.1)' }}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
          Autonomous Contract Risk Intelligence Platform - Real-time GitHub Webhook Integration
        </Typography>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card sx={{ bgcolor: 'rgba(0, 230, 118, 0.1)', border: '1px solid rgba(0, 230, 118, 0.3)', borderRadius: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', textTransform: 'uppercase', letterSpacing: 1 }}>
                    Active Incidents
                  </Typography>
                  <SpeedIcon sx={{ color: '#00e676' }} />
                </Box>
                <Typography variant="h3" sx={{ fontWeight: 800, color: 'white', mb: 1 }}>
                  {activeIncidents.length}
                </Typography>
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                  {currentIncidents.length} total incidents
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card sx={{ bgcolor: 'rgba(255, 23, 68, 0.1)', border: '1px solid rgba(255, 23, 68, 0.3)', borderRadius: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', textTransform: 'uppercase', letterSpacing: 1 }}>
                    SLA Breaches
                  </Typography>
                  <ErrorIcon sx={{ color: '#ff1744' }} />
                </Box>
                <Typography variant="h3" sx={{ fontWeight: 800, color: 'white', mb: 1 }}>
                  {breachCount}
                </Typography>
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                  {currentIncidents.filter(i => i.penalty_waived).length} waived by exclusions
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <Card sx={{ bgcolor: 'rgba(255, 193, 7, 0.1)', border: '1px solid rgba(255, 193, 7, 0.3)', borderRadius: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', textTransform: 'uppercase', letterSpacing: 1 }}>
                    Financial Exposure
                  </Typography>
                  <MoneyIcon sx={{ color: '#ffc107' }} />
                </Box>
                <Typography variant="h3" sx={{ fontWeight: 800, color: 'white', mb: 1 }}>
                  ${(totalExposure / 1000).toFixed(1)}K
                </Typography>
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                  ${(totalWaived / 1000).toFixed(1)}K waived
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <Card sx={{ bgcolor: 'rgba(33, 150, 243, 0.1)', border: '1px solid rgba(33, 150, 243, 0.3)', borderRadius: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', textTransform: 'uppercase', letterSpacing: 1 }}>
                    Analyzing Now
                  </Typography>
                  <CheckCircleIcon sx={{ color: '#2196f3' }} />
                </Box>
                <Typography variant="h3" sx={{ fontWeight: 800, color: 'white', mb: 1 }}>
                  {currentIncidents.filter(i => i.sla_analysis_started && !i.sla_analysis_completed).length}
                </Typography>
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                  Crew executions active
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Contract Tabs */}
      <Paper sx={{ bgcolor: '#151518', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 3, mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            borderBottom: '1px solid rgba(255,255,255,0.1)',
            '& .MuiTab-root': {
              color: 'rgba(255,255,255,0.5)',
              fontWeight: 600,
              textTransform: 'none',
              fontSize: '1rem'
            },
            '& .Mui-selected': {
              color: '#00e676 !important'
            },
            '& .MuiTabs-indicator': {
              backgroundColor: '#00e676'
            }
          }}
        >
          <Tab 
            label={
              <Badge badgeContent={activeIncidents.length} color="error">
                All Incidents
              </Badge>
            } 
          />
          {contracts.map((contract, index) => (
            <Tab
              key={contract.contract_id}
              label={
                <Badge badgeContent={0} color="error">
                  {contract.provider || `Contract ${index + 1}`}
                </Badge>
              }
            />
          ))}
        </Tabs>

        {/* Tab Panels */}
        <TabPanel value={activeTab} index={0}>
          <IncidentList 
            incidents={currentIncidents} 
            reasoningLogs={reasoningLogs}
            onRefresh={loadIncidents}
          />
        </TabPanel>
        
        {contracts.map((contract, index) => (
          <TabPanel key={contract.contract_id} value={activeTab} index={index + 1}>
            <IncidentList 
              incidents={currentIncidents.filter(i => true)} // Filter by contract in production
              reasoningLogs={reasoningLogs}
              onRefresh={loadIncidents}
              contractId={contract.contract_id}
            />
          </TabPanel>
        ))}
      </Paper>

      {/* Floating Active Agent Indicator - Bottom Right */}
      <AnimatePresence>
        {activeAgent && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            style={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              zIndex: 1000
            }}
          >
            <Card sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: '2px solid rgba(255,255,255,0.2)',
              boxShadow: '0 8px 32px rgba(102, 126, 234, 0.4)',
              minWidth: 280
            }}>
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
                  >
                    <Box sx={{
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #00e676 0%, #00c853 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: 20
                    }}>
                      🤖
                    </Box>
                  </motion.div>
                  
                  <Box sx={{ flex: 1 }}>
                    <Typography sx={{
                      color: 'white',
                      fontWeight: 700,
                      fontSize: 14,
                      mb: 0.5
                    }}>
                      {activeAgent.agent}
                    </Typography>
                    <Typography sx={{
                      color: 'rgba(255,255,255,0.8)',
                      fontSize: 12
                    }}>
                      {activeAgent.task}
                    </Typography>
                  </Box>
                  
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                  >
                    <LiveIcon sx={{ color: '#00e676', fontSize: 16 }} />
                  </motion.div>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </Box>
  );
};

// Incident List Component
interface IncidentListProps {
  incidents: Incident[];
  reasoningLogs: Record<string, ReasoningLog[]>;
  onRefresh: () => void;
  contractId?: string;
}

const IncidentList: React.FC<IncidentListProps> = ({ incidents, reasoningLogs, onRefresh, contractId }) => {
  const [expandedIncident, setExpandedIncident] = useState<string | null>(null);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'P1':
      case 'SEV1':
      case 'CRITICAL': return '#ff1744';
      case 'P2': return '#ff9100';
      case 'P3': return '#ffc107';
      case 'P4': return '#4caf50';
      default: return '#9e9e9e';
    }
  };

  if (incidents.length === 0) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.5)', mb: 2 }}>
          No incidents detected
        </Typography>
        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.3)' }}>
          Waiting for GitHub webhook events...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <AnimatePresence>
        {incidents.map((incident, index) => (
          <motion.div
            key={incident.incident_id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ delay: index * 0.05 }}
          >
            <Card 
              sx={{ 
                mb: 2,
                bgcolor: incident.breach_detected ? 'rgba(255, 23, 68, 0.05)' : 'rgba(0, 230, 118, 0.05)',
                border: `1px solid ${incident.breach_detected ? 'rgba(255, 23, 68, 0.3)' : 'rgba(0, 230, 118, 0.3)'}`,
                borderRadius: 2,
                cursor: 'pointer',
                transition: 'all 0.3s',
                '&:hover': {
                  transform: 'translateX(4px)',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
                }
              }}
              onClick={() => setExpandedIncident(expandedIncident === incident.incident_id ? null : incident.incident_id)}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                      <Typography variant="h6" sx={{ color: 'white', fontWeight: 700 }}>
                        {incident.incident_id}
                      </Typography>
                      <Chip 
                        label={incident.priority}
                        size="small"
                        sx={{ 
                          bgcolor: getPriorityColor(incident.priority),
                          color: 'white',
                          fontWeight: 700
                        }}
                      />
                      <Chip 
                        label={incident.status}
                        size="small"
                        variant="outlined"
                        sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.3)' }}
                      />
                      {incident.sla_analysis_started && !incident.sla_analysis_completed && (
                        <Chip 
                          label="ANALYZING"
                          size="small"
                          icon={<LiveIcon sx={{ fontSize: 12 }} />}
                          sx={{ bgcolor: 'rgba(33, 150, 243, 0.2)', color: '#2196f3', animation: 'pulse 2s infinite' }}
                        />
                      )}
                    </Box>
                    
                    <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.9)', mb: 1 }}>
                      {incident.title}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                        Service: {incident.service}
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                        Source: {incident.source}
                      </Typography>
                      {incident.affected_users && (
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                          Affected: {incident.affected_users.toLocaleString()} users
                        </Typography>
                      )}
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                        Created: {new Date(incident.created_at).toLocaleString()}
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ textAlign: 'right' }}>
                    {incident.breach_detected && (
                      <Box>
                        <Typography variant="h5" sx={{ color: incident.penalty_waived ? '#ffc107' : '#ff1744', fontWeight: 800 }}>
                          ${incident.financial_exposure.toLocaleString()}
                        </Typography>
                        {incident.penalty_waived && (
                          <Chip 
                            label="WAIVED"
                            size="small"
                            sx={{ bgcolor: 'rgba(76, 175, 80, 0.2)', color: '#4caf50', mt: 1 }}
                          />
                        )}
                      </Box>
                    )}
                  </Box>
                </Box>

                {/* Expanded Reasoning Logs */}
                {expandedIncident === incident.incident_id && reasoningLogs[incident.incident_id] && (
                  <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                    <Typography variant="subtitle2" sx={{ color: 'white', mb: 2, fontWeight: 700 }}>
                      🤖 AI Reasoning Stream
                    </Typography>
                    <Box sx={{ 
                      bgcolor: 'rgba(0,0,0,0.3)', 
                      borderRadius: 2, 
                      p: 2,
                      maxHeight: '300px',
                      overflowY: 'auto',
                      fontFamily: 'monospace',
                      fontSize: '0.85rem'
                    }}>
                      {reasoningLogs[incident.incident_id].map((log, idx) => (
                        <Box key={log.log_id} sx={{ mb: 1, display: 'flex', gap: 2 }}>
                          <Typography sx={{ 
                            color: log.level === 'ERROR' ? '#ff1744' : 
                                   log.level === 'WARNING' ? '#ffc107' : 
                                   log.level === 'SUCCESS' ? '#00e676' : '#2196f3',
                            minWidth: '60px'
                          }}>
                            [{new Date(log.timestamp).toLocaleTimeString()}]
                          </Typography>
                          <Typography sx={{ color: 'rgba(255,255,255,0.9)' }}>
                            {log.message}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </AnimatePresence>
    </Box>
  );
};

export default WarRoom;

// Made with Bob
