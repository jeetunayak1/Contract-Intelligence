import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Alert,
  Button,
  IconButton,
  Tabs,
  Tab,
  Paper,
  Divider,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Refresh as RefreshIcon,
  PlayArrow as PlayArrowIcon,
  Shield as ShieldIcon,
  AttachMoney as MoneyIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const API_BASE = 'http://localhost:8000/api/v1';

interface ComplianceReport {
  report_id: string;
  overall_status: string;
  breach_severity: string;
  incident_analysis: any[];
  kpi_analysis: any[];
  financial_summary: {
    total_estimated_exposure: number;
    total_waived_penalties: number;
    net_exposure: number;
    exposure_percentage: number;
    incidents_with_exposure: number;
    incidents_waived: number;
  };
  reasoning_stream: Array<{
    timestamp: string;
    message: string;
    level: string;
  }>;
  total_incidents: number;
  breached_incidents: number;
  waived_incidents: number;
}

const WarRoom: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState<ComplianceReport | null>(null);
  const [contracts, setContracts] = useState<any[]>([]);
  const [selectedContract, setSelectedContract] = useState<string>('');
  const [activeTab, setActiveTab] = useState(0);
  const [reasoningIndex, setReasoningIndex] = useState(0);

  useEffect(() => {
    loadContracts();
  }, []);

  useEffect(() => {
    if (report && report.reasoning_stream.length > 0) {
      const timer = setInterval(() => {
        setReasoningIndex(prev => {
          if (prev < report.reasoning_stream.length - 1) {
            return prev + 1;
          }
          clearInterval(timer);
          return prev;
        });
      }, 300);
      return () => clearInterval(timer);
    }
  }, [report]);

  const loadContracts = async () => {
    try {
      const response = await fetch(`${API_BASE}/compliance/contracts`);
      const data = await response.json();
      if (data.success && data.contracts.length > 0) {
        setContracts(data.contracts);
        setSelectedContract(data.contracts[0].contract_id);
      }
    } catch (error) {
      console.error('Failed to load contracts:', error);
    }
  };

  const runAnalysis = async () => {
    if (!selectedContract) return;
    
    setAnalyzing(true);
    setReasoningIndex(0);
    
    try {
      const response = await fetch(
        `${API_BASE}/compliance/analyze?contract_id=${selectedContract}&monthly_fee=100000`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }
      
      const data = await response.json();
      setReport(data);
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Analysis failed. Please check console for details.');
    } finally {
      setAnalyzing(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLIANT': return '#00e676';
      case 'BREACH': return '#ff1744';
      case 'WARNING': return '#ffc107';
      case 'WAIVED': return '#00bcd4';
      default: return '#9e9e9e';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return '#ff1744';
      case 'HIGH': return '#ff9100';
      case 'MEDIUM': return '#ffc107';
      case 'LOW': return '#00e676';
      default: return '#9e9e9e';
    }
  };

  return (
    <Box sx={{ p: 3, bgcolor: '#0a0a0c', minHeight: '100vh' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <ShieldIcon sx={{ fontSize: 48, color: 'primary.main' }} />
            <Box>
              <Typography variant="h3" sx={{ fontWeight: 800, color: 'white' }}>
                AI SLA <span style={{ color: '#00e676' }}>WAR ROOM</span>
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                Autonomous Contract Risk Intelligence Platform
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <FormControl sx={{ minWidth: 300 }}>
              <InputLabel sx={{ color: 'rgba(255,255,255,0.7)' }}>Select Contract</InputLabel>
              <Select
                value={selectedContract}
                onChange={(e) => setSelectedContract(e.target.value)}
                label="Select Contract"
                sx={{
                  color: 'white',
                  bgcolor: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(0, 230, 118, 0.3)',
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'rgba(0, 230, 118, 0.3)'
                  },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'rgba(0, 230, 118, 0.5)'
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main'
                  }
                }}
              >
                {contracts.map((contract) => (
                  <MenuItem key={contract.contract_id} value={contract.contract_id}>
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {contract.provider || 'Unknown Provider'}
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                        {contract.filename}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Button
              variant="contained"
              size="large"
              startIcon={analyzing ? <CircularProgress size={20} /> : <PlayArrowIcon />}
              onClick={runAnalysis}
              disabled={analyzing || !selectedContract}
              sx={{
                bgcolor: 'primary.main',
                color: 'black',
                fontWeight: 700,
                px: 4,
                py: 1.5,
                '&:hover': { bgcolor: 'primary.light' }
              }}
            >
              {analyzing ? 'ANALYZING...' : 'RUN ANALYSIS'}
            </Button>
          </Box>
        </Box>
        
        {selectedContract && contracts.length > 0 && (
          <Alert
            severity="info"
            sx={{
              bgcolor: 'rgba(0, 188, 212, 0.1)',
              border: '1px solid rgba(0, 188, 212, 0.3)',
              color: 'white'
            }}
          >
            <Typography variant="body2">
              <strong>Selected Contract:</strong> {contracts.find(c => c.contract_id === selectedContract)?.provider} - {contracts.find(c => c.contract_id === selectedContract)?.filename}
            </Typography>
          </Alert>
        )}
      </Box>

      {/* KPI Cards */}
      {report && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Card sx={{ 
                bgcolor: 'rgba(0, 230, 118, 0.1)', 
                border: '1px solid rgba(0, 230, 118, 0.3)',
                borderRadius: 3
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', textTransform: 'uppercase', letterSpacing: 1 }}>
                      SLA Health
                    </Typography>
                    <SpeedIcon sx={{ color: 'primary.main' }} />
                  </Box>
                  <Typography variant="h3" sx={{ fontWeight: 800, color: 'white', mb: 1 }}>
                    {Math.round(((report.total_incidents - report.breached_incidents) / report.total_incidents) * 100)}%
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                    {report.total_incidents - report.breached_incidents} of {report.total_incidents} compliant
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <Card sx={{ 
                bgcolor: 'rgba(255, 23, 68, 0.1)', 
                border: '1px solid rgba(255, 23, 68, 0.3)',
                borderRadius: 3
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', textTransform: 'uppercase', letterSpacing: 1 }}>
                      Active Breaches
                    </Typography>
                    <ErrorIcon sx={{ color: '#ff1744' }} />
                  </Box>
                  <Typography variant="h3" sx={{ fontWeight: 800, color: 'white', mb: 1 }}>
                    {report.breached_incidents}
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                    {report.waived_incidents} waived by exclusions
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Card sx={{ 
                bgcolor: 'rgba(255, 193, 7, 0.1)', 
                border: '1px solid rgba(255, 193, 7, 0.3)',
                borderRadius: 3
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', textTransform: 'uppercase', letterSpacing: 1 }}>
                      Financial Exposure
                    </Typography>
                    <MoneyIcon sx={{ color: '#ffc107' }} />
                  </Box>
                  <Typography variant="h3" sx={{ fontWeight: 800, color: 'white', mb: 1 }}>
                    ${(report.financial_summary.net_exposure / 1000).toFixed(1)}K
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                    {report.financial_summary.exposure_percentage.toFixed(1)}% of monthly fee
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <Card sx={{ 
                bgcolor: 'rgba(0, 188, 212, 0.1)', 
                border: '1px solid rgba(0, 188, 212, 0.3)',
                borderRadius: 3
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', textTransform: 'uppercase', letterSpacing: 1 }}>
                      Waived Penalties
                    </Typography>
                    <CheckCircleIcon sx={{ color: '#00bcd4' }} />
                  </Box>
                  <Typography variant="h3" sx={{ fontWeight: 800, color: 'white', mb: 1 }}>
                    ${(report.financial_summary.total_waived_penalties / 1000).toFixed(1)}K
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                    Liability exclusions applied
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </Grid>
      )}

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* AI Reasoning Stream */}
        <Grid item xs={12} md={6}>
          <Card sx={{
            bgcolor: '#151518',
            border: '1px solid rgba(0, 230, 118, 0.2)',
            borderRadius: 3,
            height: 'calc(100vh - 450px)',
            minHeight: '400px',
            maxHeight: '700px',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2, flexShrink: 0 }}>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'white' }}>
                  🤖 AI Reasoning Stream
                </Typography>
                <Box className="agent-pulse" sx={{ width: 8, height: 8, bgcolor: 'primary.main', borderRadius: '50%' }} />
              </Box>
              
              <Box sx={{
                flex: 1,
                bgcolor: 'rgba(0,0,0,0.3)',
                borderRadius: 2,
                p: 2,
                fontFamily: 'monospace',
                fontSize: '0.85rem',
                overflowY: 'auto',
                overflowX: 'hidden',
                border: '1px solid rgba(0, 230, 118, 0.1)',
                minHeight: 0
              }}>
                <AnimatePresence>
                  {report && report.reasoning_stream.slice(0, reasoningIndex + 1).map((step, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3 }}
                      style={{ marginBottom: '12px' }}
                    >
                      <Box sx={{ display: 'flex', gap: 2 }}>
                        <Typography sx={{ 
                          color: step.level === 'ERROR' ? '#ff1744' : 
                                 step.level === 'WARNING' ? '#ffc107' : 
                                 '#00e676',
                          minWidth: '60px'
                        }}>
                          [{new Date(step.timestamp).toLocaleTimeString()}]
                        </Typography>
                        <Typography sx={{ color: 'rgba(255,255,255,0.9)' }}>
                          {step.message}
                        </Typography>
                      </Box>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Incident Analysis */}
        <Grid item xs={12} md={6}>
          <Card sx={{
            bgcolor: '#151518',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
            height: 'calc(100vh - 450px)',
            minHeight: '400px',
            maxHeight: '700px',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, color: 'white', mb: 2, flexShrink: 0 }}>
                🚨 Incident Analysis
              </Typography>
              
              <Box sx={{ flex: 1, overflowY: 'auto', minHeight: 0 }}>
                {report && report.incident_analysis.map((incident, index) => (
                  <motion.div
                    key={incident.incident_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                  >
                    <Card sx={{ 
                      mb: 2, 
                      bgcolor: incident.breach_detected ? 'rgba(255, 23, 68, 0.1)' : 'rgba(0, 230, 118, 0.1)',
                      border: `1px solid ${incident.breach_detected ? 'rgba(255, 23, 68, 0.3)' : 'rgba(0, 230, 118, 0.3)'}`,
                      borderRadius: 2
                    }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'white' }}>
                            {incident.incident_id}
                          </Typography>
                          <Chip 
                            label={incident.priority} 
                            size="small"
                            sx={{ 
                              bgcolor: getSeverityColor(incident.breach_severity),
                              color: 'black',
                              fontWeight: 700
                            }}
                          />
                        </Box>
                        
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', display: 'block', mb: 1 }}>
                          {incident.title}
                        </Typography>
                        
                        <Box sx={{ display: 'flex', gap: 2, mb: 1 }}>
                          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                            Target: {incident.sla_target_hours}h
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                            Actual: {incident.actual_resolution_hours}h
                          </Typography>
                        </Box>
                        
                        {incident.liability_exclusion_applied && (
                          <Alert severity="info" sx={{ mt: 1, py: 0 }}>
                            <Typography variant="caption">
                              ✅ Penalty waived: ${incident.waived_amount.toLocaleString()}
                            </Typography>
                          </Alert>
                        )}
                        
                        {incident.breach_detected && !incident.liability_exclusion_applied && (
                          <Alert severity="error" sx={{ mt: 1, py: 0 }}>
                            <Typography variant="caption">
                              💰 Exposure: ${incident.financial_exposure.toLocaleString()}
                            </Typography>
                          </Alert>
                        )}
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Loading State */}
      {analyzing && !report && (
        <Box sx={{ 
          position: 'fixed', 
          top: 0, 
          left: 0, 
          right: 0, 
          bottom: 0, 
          bgcolor: 'rgba(0,0,0,0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999
        }}>
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress size={60} sx={{ color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" sx={{ color: 'white' }}>
              Running Compliance Analysis...
            </Typography>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default WarRoom;

// Made with Bob
