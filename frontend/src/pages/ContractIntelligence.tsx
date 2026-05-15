import React, { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Grid,
  LinearProgress,
  Paper,
  Stack,
  Tab,
  Tabs,
  Typography,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  IconButton,
} from '@mui/material';
import {
  CloudUpload,
  Psychology,
  Security,
  Gavel,
  TrendingUp,
  AttachMoney,
  CalendarMonth,
  DoneAll,
  Warning,
  Delete,
} from '@mui/icons-material';
import { toast } from 'react-toastify';

interface ContractMetadata {
  contract_id: string;
  client_name: string;
  provider_name: string;
  effective_date?: string;
  contract_period_years?: number;
}

interface IncidentSLA {
  priority: string;
  acknowledge_minutes?: number;
  workaround_hours?: number;
  resolution_hours?: number;
  rca_deadline_hours?: number;
  availability_window?: string;
}

interface AvailabilitySLA {
  tier: string;
  target_uptime_percent: number;
  max_downtime_minutes?: number;
  measurement_tool?: string;
}

interface ServiceCredit {
  priority?: string;
  breach_condition: string;
  credit_percent: number;
  monthly_cap_percent?: number;
}

interface ComplianceObligations {
  incident_slas: IncidentSLA[];
  availability_slas: AvailabilitySLA[];
  quality_kpis: any[];
  governance_rules: any[];
  escalation_rules: any[];
}

interface RiskObligations {
  service_credits: ServiceCredit[];
  financial_caps: any[];
  commercial_penalties: any[];
  revenue_controls: any[];
}

interface LiabilityExclusion {
  exclusion_type: string;
  description?: string;
}

interface ClientObligation {
  obligation: string;
  sla_days?: number;
}

interface TerminationClause {
  termination_type: string;
  notice_period_days?: number;
}

interface LegalConstraint {
  type: string;
  details: string;
}

interface LiabilityObligations {
  liability_exclusions: LiabilityExclusion[];
  client_obligations: ClientObligation[];
  termination_clauses: TerminationClause[];
  legal_constraints: LegalConstraint[];
}

interface ExtractedContract {
  contract_metadata: ContractMetadata;
  compliance_obligations: ComplianceObligations;
  risk_obligations: RiskObligations;
  liability_obligations: LiabilityObligations;
  // Backward compatibility - these will be computed from categorized data
  incident_slas?: IncidentSLA[];
  availability_slas?: AvailabilitySLA[];
  service_credits?: ServiceCredit[];
  liability_exclusions?: string[];
  quality_kpis?: any[];
  governance_rules?: any[];
  escalation_matrix?: any[];
}

interface Contract {
  contract_id: string;
  filename: string;
  extracted_data: ExtractedContract;
  processed_at: string;
  extraction_status: string;
}

const API_BASE = 'http://localhost:8000/api/v1/contracts';

const ContractIntelligence: React.FC = () => {
  const [tab, setTab] = useState(0);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStep, setUploadStep] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [contractToDelete, setContractToDelete] = useState<Contract | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    void loadContracts();
  }, []);

  const loadContracts = async () => {
    try {
      const response = await fetch(`${API_BASE}/list`);
      if (!response.ok) throw new Error('Failed to load contracts');
      const data = await response.json();
      setContracts(data.contracts || []);
      if (data.contracts?.length > 0 && !selectedContract) {
        setSelectedContract(data.contracts[0]);
      }
    } catch (error) {
      console.error(error);
      toast.error('Failed to load contracts');
    }
  };

  const handleFileUpload = async (file: File) => {
    setUploading(true);
    setUploadProgress(10);
    setUploadStep('Parsing document structure...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Simulate progress steps
      const simulateSteps = async () => {
        await new Promise(r => setTimeout(r, 1500));
        setUploadProgress(40);
        setUploadStep('Extracting SLA obligations...');
        await new Promise(r => setTimeout(r, 2000));
        setUploadProgress(70);
        setUploadStep('Normalizing compliance rules...');
        await new Promise(r => setTimeout(r, 1500));
        setUploadProgress(90);
        setUploadStep('Storing contract data...');
      };

      const uploadPromise = fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });

      void simulateSteps();
      const response = await uploadPromise;

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await response.json();
      toast.success('Contract processed successfully!');
      
      await loadContracts();
      
      // Select the newly uploaded contract
      const newContract = contracts.find(c => c.contract_id === data.contract_id);
      if (newContract) {
        setSelectedContract(newContract);
      }
      
      setTab(1);
    } catch (error) {
      console.error(error);
      toast.error(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setUploading(false);
      setUploadProgress(0);
      setUploadStep('');
    }
  };

  const handleDeleteClick = (contract: Contract, event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent contract selection
    setContractToDelete(contract);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!contractToDelete) return;

    setDeleting(true);
    try {
      const response = await fetch(`${API_BASE}/${contractToDelete.contract_id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to delete contract');
      }

      toast.success('Contract deleted successfully!');
      
      // If the deleted contract was selected, clear selection
      if (selectedContract?.contract_id === contractToDelete.contract_id) {
        setSelectedContract(null);
      }
      
      // Reload contracts list
      await loadContracts();
      
    } catch (error) {
      console.error(error);
      toast.error(error instanceof Error ? error.message : 'Failed to delete contract');
    } finally {
      setDeleting(false);
      setDeleteDialogOpen(false);
      setContractToDelete(null);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setContractToDelete(null);
  };

  const renderRiskChip = (priority?: string) => {
    const p = (priority || 'P3').toUpperCase();
    const isHigh = p === 'P1' || p === 'P2';
    return (
      <Chip
        size="small"
        label={p}
        sx={{
          fontWeight: 900,
          fontSize: '0.65rem',
          height: 20,
          bgcolor: isHigh ? 'rgba(255, 23, 68, 0.15)' : 'rgba(0, 230, 118, 0.15)',
          color: isHigh ? '#ff1744' : '#00e676',
          border: `1px solid ${isHigh ? 'rgba(255, 23, 68, 0.3)' : 'rgba(0, 230, 118, 0.3)'}`,
        }}
      />
    );
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Upload Overlay */}
      {uploading && (
        <Box
          sx={{
            position: 'fixed',
            top: 0, left: 0, right: 0, bottom: 0,
            bgcolor: 'rgba(10, 10, 12, 0.9)',
            zIndex: 9999,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            backdropFilter: 'blur(10px)'
          }}
        >
          <Box sx={{ width: '400px', textAlign: 'center' }}>
            <Box className="agent-pulse" sx={{ width: 80, height: 80, bgcolor: 'primary.main', mx: 'auto', mb: 4, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Psychology sx={{ fontSize: 40, color: '#000' }} />
            </Box>
            <Typography variant="h4" sx={{ fontWeight: 800, mb: 1 }}>
              Contract <span className="gradient-text">Intelligence</span>
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
              AI is extracting SLA obligations...
            </Typography>

            <Box sx={{ mb: 4 }}>
              <LinearProgress variant="determinate" value={uploadProgress} sx={{ height: 10, borderRadius: 5, bgcolor: 'rgba(255,255,255,0.05)' }} />
              <Typography variant="caption" sx={{ mt: 2, display: 'block', fontWeight: 700, color: 'primary.main', textTransform: 'uppercase', letterSpacing: 1 }}>
                {uploadStep}
              </Typography>
            </Box>

            <Stack spacing={2} sx={{ textAlign: 'left', opacity: 0.6 }}>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                <DoneAll sx={{ color: uploadProgress > 30 ? 'primary.main' : 'text.disabled' }} />
                <Typography variant="body2">Document Parsing & Text Extraction</Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                <DoneAll sx={{ color: uploadProgress > 60 ? 'primary.main' : 'text.disabled' }} />
                <Typography variant="body2">SLA & Penalty Extraction</Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                <DoneAll sx={{ color: uploadProgress > 85 ? 'primary.main' : 'text.disabled' }} />
                <Typography variant="body2">Compliance Rule Normalization</Typography>
              </Box>
            </Stack>
          </Box>
        </Box>
      )}

      {/* Header */}
      <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h3" sx={{ fontWeight: 800, mb: 1 }}>
            Contract <span className="gradient-text">Intelligence</span>
          </Typography>
          <Typography variant="body1" color="text.secondary">
            AI-powered SLA extraction and compliance monitoring
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<CloudUpload />}
          onClick={() => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.pdf,.docx,.txt';
            input.onchange = (e: any) => {
              const file = e.target.files?.[0];
              if (file) handleFileUpload(file);
            };
            input.click();
          }}
          sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700 }}
        >
          Upload Contract
        </Button>
      </Box>

      <Grid container spacing={4}>
        {/* Left: Contract List */}
        <Grid item xs={12} md={4}>
          <Typography variant="h6" sx={{ fontWeight: 800, mb: 3 }}>
            Processed Contracts
          </Typography>
          <Stack spacing={2}>
            {contracts.map((contract) => (
              <Box
                key={contract.contract_id}
                onClick={() => setSelectedContract(contract)}
                sx={{
                  p: 3,
                  borderRadius: 4,
                  cursor: 'pointer',
                  bgcolor: selectedContract?.contract_id === contract.contract_id ? 'rgba(0, 230, 118, 0.05)' : 'rgba(255,255,255,0.02)',
                  border: selectedContract?.contract_id === contract.contract_id ? '1px solid #00e676' : '1px solid rgba(255,255,255,0.05)',
                  transition: 'all 0.2s',
                  '&:hover': { bgcolor: 'rgba(255,255,255,0.05)' },
                  position: 'relative'
                }}
              >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 800 }}>
                      {contract.extracted_data.contract_metadata.client_name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
                      {contract.filename}
                    </Typography>
                    <Chip
                      size="small"
                      label={contract.extraction_status}
                      color="success"
                      sx={{ fontWeight: 900, fontSize: '0.6rem', height: 18 }}
                    />
                  </Box>
                  <IconButton
                    size="small"
                    onClick={(e) => handleDeleteClick(contract, e)}
                    sx={{
                      color: 'error.main',
                      '&:hover': {
                        bgcolor: 'rgba(255, 23, 68, 0.1)',
                      }
                    }}
                  >
                    <Delete fontSize="small" />
                  </IconButton>
                </Box>
              </Box>
            ))}
          </Stack>
        </Grid>

        {/* Right: Contract Details */}
        <Grid item xs={12} md={8}>
          {!selectedContract ? (
            <Paper className="glass-card" sx={{ p: 10, textAlign: 'center' }}>
              <Psychology sx={{ fontSize: 60, opacity: 0.1, mb: 2 }} />
              <Typography color="text.secondary">
                Select a contract or upload a new one to begin analysis
              </Typography>
            </Paper>
          ) : (
            <Stack spacing={4}>
              {/* Tabs */}
              <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={tab} onChange={(_, v) => setTab(v)} textColor="primary" indicatorColor="primary">
                  <Tab label="Overview" sx={{ fontWeight: 800, textTransform: 'none' }} />
                  <Tab label={`Incident SLAs (${selectedContract.extracted_data.compliance_obligations.incident_slas.length})`} sx={{ fontWeight: 800, textTransform: 'none' }} />
                  <Tab label={`Service Credits (${selectedContract.extracted_data.risk_obligations.service_credits.length})`} sx={{ fontWeight: 800, textTransform: 'none' }} />
                </Tabs>
              </Box>

              {/* Overview Tab */}
              {tab === 0 && (
                <Stack spacing={4}>
                  {/* Metadata */}
                  <Card className="glass-card">
                    <CardContent sx={{ p: 4 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2 }}>
                        <Avatar sx={{ bgcolor: 'primary.main' }}><Gavel /></Avatar>
                        <Box>
                          <Typography variant="h6" sx={{ fontWeight: 800 }}>Contract Metadata</Typography>
                          <Typography variant="caption" color="text.secondary">Basic Information</Typography>
                        </Box>
                      </Box>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Client</Typography>
                          <Typography variant="body1" sx={{ fontWeight: 700 }}>
                            {selectedContract.extracted_data.contract_metadata.client_name}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Provider</Typography>
                          <Typography variant="body1" sx={{ fontWeight: 700 }}>
                            {selectedContract.extracted_data.contract_metadata.provider_name}
                          </Typography>
                        </Grid>
                        {selectedContract.extracted_data.contract_metadata.effective_date && (
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Effective Date</Typography>
                            <Typography variant="body1" sx={{ fontWeight: 700 }}>
                              {selectedContract.extracted_data.contract_metadata.effective_date}
                            </Typography>
                          </Grid>
                        )}
                        {selectedContract.extracted_data.contract_metadata.contract_period_years && (
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Contract Period</Typography>
                            <Typography variant="body1" sx={{ fontWeight: 700 }}>
                              {selectedContract.extracted_data.contract_metadata.contract_period_years} years
                            </Typography>
                          </Grid>
                        )}
                      </Grid>
                    </CardContent>
                  </Card>

                  {/* Summary Stats */}
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={3}>
                      <Paper sx={{ p: 3, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 3 }}>
                        <Typography variant="h3" sx={{ fontWeight: 900, color: 'primary.main' }}>
                          {selectedContract.extracted_data.compliance_obligations.incident_slas.length}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">Incident SLAs</Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Paper sx={{ p: 3, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 3 }}>
                        <Typography variant="h3" sx={{ fontWeight: 900, color: 'warning.main' }}>
                          {selectedContract.extracted_data.compliance_obligations.availability_slas.length}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">Availability SLAs</Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Paper sx={{ p: 3, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 3 }}>
                        <Typography variant="h3" sx={{ fontWeight: 900, color: 'secondary.main' }}>
                          {selectedContract.extracted_data.risk_obligations.service_credits.length}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">Service Credits</Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Paper sx={{ p: 3, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 3 }}>
                        <Typography variant="h3" sx={{ fontWeight: 900, color: 'info.main' }}>
                          {selectedContract.extracted_data.liability_obligations.liability_exclusions.length}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">Exclusions</Typography>
                      </Paper>
                    </Grid>
                  </Grid>

                  {/* Liability Exclusions */}
                  {selectedContract.extracted_data.liability_obligations.liability_exclusions.length > 0 && (
                    <Card className="glass-card">
                      <CardContent sx={{ p: 4 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2 }}>
                          <Avatar sx={{ bgcolor: 'warning.main' }}><Warning /></Avatar>
                          <Box>
                            <Typography variant="h6" sx={{ fontWeight: 800 }}>Liability Exclusions</Typography>
                            <Typography variant="caption" color="text.secondary">Force Majeure & Exceptions</Typography>
                          </Box>
                        </Box>
                        <Stack spacing={1}>
                          {selectedContract.extracted_data.liability_obligations.liability_exclusions.map((exclusion, i) => (
                            <Box key={i} sx={{ p: 2, bgcolor: 'rgba(255, 152, 0, 0.05)', borderRadius: 2, border: '1px solid rgba(255, 152, 0, 0.1)' }}>
                              <Typography variant="body2" sx={{ fontWeight: 700, mb: 0.5 }}>
                                {exclusion.exclusion_type}
                              </Typography>
                              {exclusion.description && (
                                <Typography variant="caption" color="text.secondary">
                                  {exclusion.description}
                                </Typography>
                              )}
                            </Box>
                          ))}
                        </Stack>
                      </CardContent>
                    </Card>
                  )}
                </Stack>
              )}

              {/* Incident SLAs Tab */}
              {tab === 1 && (
                <Card className="glass-card">
                  <CardContent sx={{ p: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2 }}>
                      <Avatar sx={{ bgcolor: 'primary.main' }}><Security /></Avatar>
                      <Box>
                        <Typography variant="h6" sx={{ fontWeight: 800 }}>Incident Response SLAs</Typography>
                        <Typography variant="caption" color="text.secondary">Response & Resolution Times</Typography>
                      </Box>
                    </Box>
                    <Box sx={{ overflowX: 'auto' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                            <th style={{ padding: '12px', textAlign: 'left' }}>Priority</th>
                            <th style={{ padding: '12px', textAlign: 'left' }}>Acknowledge</th>
                            <th style={{ padding: '12px', textAlign: 'left' }}>Workaround</th>
                            <th style={{ padding: '12px', textAlign: 'left' }}>Resolution</th>
                            <th style={{ padding: '12px', textAlign: 'left' }}>RCA</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedContract.extracted_data.compliance_obligations.incident_slas.map((sla, i) => (
                            <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                              <td style={{ padding: '12px' }}>{renderRiskChip(sla.priority)}</td>
                              <td style={{ padding: '12px' }}>{sla.acknowledge_minutes ? `${sla.acknowledge_minutes} min` : '-'}</td>
                              <td style={{ padding: '12px' }}>{sla.workaround_hours ? `${sla.workaround_hours} hrs` : '-'}</td>
                              <td style={{ padding: '12px' }}>{sla.resolution_hours ? `${sla.resolution_hours} hrs` : '-'}</td>
                              <td style={{ padding: '12px' }}>{sla.rca_deadline_hours ? `${sla.rca_deadline_hours} hrs` : '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </Box>
                  </CardContent>
                </Card>
              )}

              {/* Service Credits Tab */}
              {tab === 2 && (
                <Card className="glass-card">
                  <CardContent sx={{ p: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2 }}>
                      <Avatar sx={{ bgcolor: 'secondary.main' }}><AttachMoney /></Avatar>
                      <Box>
                        <Typography variant="h6" sx={{ fontWeight: 800 }}>Service Credits & Penalties</Typography>
                        <Typography variant="caption" color="text.secondary">Financial Exposure</Typography>
                      </Box>
                    </Box>
                    <Stack spacing={2}>
                      {selectedContract.extracted_data.risk_obligations.service_credits.map((credit, i) => (
                        <Box key={i} sx={{ p: 3, bgcolor: 'rgba(244, 143, 177, 0.05)', borderRadius: 3, border: '1px solid rgba(244, 143, 177, 0.1)' }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 800, color: 'secondary.main', mb: 1 }}>
                            {credit.breach_condition}
                          </Typography>
                          <Grid container spacing={2}>
                            <Grid item xs={6}>
                              <Typography variant="caption" color="text.secondary">Credit</Typography>
                              <Typography variant="h6" sx={{ fontWeight: 900 }}>{credit.credit_percent}%</Typography>
                            </Grid>
                            {credit.monthly_cap_percent && (
                              <Grid item xs={6}>
                                <Typography variant="caption" color="text.secondary">Monthly Cap</Typography>
                                <Typography variant="h6" sx={{ fontWeight: 900 }}>{credit.monthly_cap_percent}%</Typography>
                              </Grid>
                            )}
                          </Grid>
                        </Box>
                      ))}
                    </Stack>
                  </CardContent>
                </Card>
              )}
            </Stack>
          )}
        </Grid>
      </Grid>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        PaperProps={{
          sx: {
            bgcolor: 'rgba(20, 20, 24, 0.95)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
          }
        }}
      >
        <DialogTitle sx={{ fontWeight: 800 }}>
          Delete Contract
        </DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ color: 'text.secondary' }}>
            Are you sure you want to delete the contract for{' '}
            <strong style={{ color: '#00e676' }}>
              {contractToDelete?.extracted_data.contract_metadata.client_name}
            </strong>
            ? This action cannot be undone and will permanently remove the contract from the database.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 0 }}>
          <Button
            onClick={handleDeleteCancel}
            disabled={deleting}
            sx={{ textTransform: 'none', fontWeight: 700 }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            variant="contained"
            color="error"
            disabled={deleting}
            sx={{ textTransform: 'none', fontWeight: 700 }}
          >
            {deleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ContractIntelligence;

// Made with Bob
