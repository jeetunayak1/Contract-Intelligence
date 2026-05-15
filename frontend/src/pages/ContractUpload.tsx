/**
 * Contract Upload Page
 * Frontend integration for Contract Intelligence Agent
 */
import React, { useState } from 'react';

interface IncidentSLA {
  priority: string;
  acknowledge_minutes: number | null;
  workaround_hours: number | null;
  resolution_hours: number | null;
  rca_deadline_hours: number | null;
  availability_window: string | null;
}

interface AvailabilitySLA {
  tier: string;
  target_uptime_percent: number;
  max_downtime_minutes: number | null;
  measurement_tool: string | null;
  measurement_period: string | null;
}

interface ServiceCredit {
  priority: string | null;
  breach_condition: string;
  credit_percent: number;
  monthly_cap_percent: number | null;
  calculation_method: string | null;
}

interface ExtractedContract {
  contract_metadata: {
    contract_id: string;
    client_name: string;
    provider_name: string;
    effective_date: string | null;
    end_date: string | null;
    contract_period_years: number | null;
  };
  incident_slas: IncidentSLA[];
  availability_slas: AvailabilitySLA[];
  service_credits: ServiceCredit[];
  liability_exclusions: string[];
  quality_kpis: any[];
  governance_rules: any[];
  escalation_matrix: any[];
}

interface UploadResponse {
  success: boolean;
  contract_id: string;
  filename: string;
  data: ExtractedContract;
  message?: string;
}

const ContractUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadResponse | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/contracts/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data: UploadResponse = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <h1 className="text-3xl font-bold mb-6">Contract Intelligence Agent</h1>
      
      {/* Upload Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Upload Contract</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Contract File (PDF, DOCX, or TXT)
          </label>
          <input
            type="file"
            accept=".pdf,.docx,.doc,.txt"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
          />
        </div>

        {file && (
          <div className="mb-4 text-sm text-gray-600">
            Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? 'Processing...' : 'Upload & Extract'}
        </button>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
            {error}
          </div>
        )}
      </div>

      {/* Results Section */}
      {result && (
        <div className="space-y-6">
          {/* Contract Metadata */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Contract Metadata</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="font-medium">Contract ID:</span> {result.contract_id}
              </div>
              <div>
                <span className="font-medium">Filename:</span> {result.filename}
              </div>
              <div>
                <span className="font-medium">Client:</span> {result.data.contract_metadata.client_name}
              </div>
              <div>
                <span className="font-medium">Provider:</span> {result.data.contract_metadata.provider_name}
              </div>
              {result.data.contract_metadata.effective_date && (
                <div>
                  <span className="font-medium">Effective Date:</span> {result.data.contract_metadata.effective_date}
                </div>
              )}
              {result.data.contract_metadata.contract_period_years && (
                <div>
                  <span className="font-medium">Contract Period:</span> {result.data.contract_metadata.contract_period_years} years
                </div>
              )}
            </div>
          </div>

          {/* Incident SLAs */}
          {result.data.incident_slas.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Incident SLAs</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acknowledge</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Workaround</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Resolution</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">RCA</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {result.data.incident_slas.map((sla, idx) => (
                      <tr key={idx}>
                        <td className="px-4 py-3 whitespace-nowrap font-medium">{sla.priority}</td>
                        <td className="px-4 py-3 whitespace-nowrap">{sla.acknowledge_minutes ? `${sla.acknowledge_minutes} min` : '-'}</td>
                        <td className="px-4 py-3 whitespace-nowrap">{sla.workaround_hours ? `${sla.workaround_hours} hrs` : '-'}</td>
                        <td className="px-4 py-3 whitespace-nowrap">{sla.resolution_hours ? `${sla.resolution_hours} hrs` : '-'}</td>
                        <td className="px-4 py-3 whitespace-nowrap">{sla.rca_deadline_hours ? `${sla.rca_deadline_hours} hrs` : '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Availability SLAs */}
          {result.data.availability_slas.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Availability SLAs</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tier</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Target Uptime</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Max Downtime</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Measurement Tool</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {result.data.availability_slas.map((sla, idx) => (
                      <tr key={idx}>
                        <td className="px-4 py-3 whitespace-nowrap font-medium">{sla.tier}</td>
                        <td className="px-4 py-3 whitespace-nowrap">{sla.target_uptime_percent}%</td>
                        <td className="px-4 py-3 whitespace-nowrap">{sla.max_downtime_minutes ? `${sla.max_downtime_minutes} min` : '-'}</td>
                        <td className="px-4 py-3 whitespace-nowrap">{sla.measurement_tool || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Service Credits */}
          {result.data.service_credits.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Service Credits</h2>
              <div className="space-y-3">
                {result.data.service_credits.map((credit, idx) => (
                  <div key={idx} className="border-l-4 border-yellow-500 pl-4 py-2">
                    <div className="font-medium">{credit.breach_condition}</div>
                    <div className="text-sm text-gray-600">
                      Credit: {credit.credit_percent}%
                      {credit.monthly_cap_percent && ` (Monthly cap: ${credit.monthly_cap_percent}%)`}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Liability Exclusions */}
          {result.data.liability_exclusions.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Liability Exclusions</h2>
              <ul className="list-disc list-inside space-y-2">
                {result.data.liability_exclusions.map((exclusion, idx) => (
                  <li key={idx} className="text-gray-700">{exclusion}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Raw JSON */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Raw JSON Data</h2>
            <pre className="bg-gray-50 p-4 rounded-md overflow-x-auto text-xs">
              {JSON.stringify(result.data, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContractUpload;

// Made with Bob
