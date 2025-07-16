import React, { useState, useEffect } from 'react';
import './App.css';
import SankeyChart, { SankeyData } from './SankeyChart';

// --- Configuration ---
const API_BASE_URL = "http://192.168.1.13:8000"; // Reverted to original IP

// --- Type Definitions ---
interface Model {
  model_id: string;
  is_compliant: boolean;
  is_restricted: boolean;
  is_deployable: boolean;
  organization: string;
  risk_category: string;
}

interface PaginatedModelsResponse {
  total_models: number;
  models: Model[];
}

const ModelList = ({ title, models, isLoading }: { title: string, models: Model[], isLoading: boolean }) => (
  <div className="card">
    <div className="card-header">{title}</div>
    <ul className="list-group list-group-flush" style={{ minHeight: '200px' }}>
      {isLoading ? (
        <li className="list-group-item text-muted">Loading...</li>
      ) : models.length > 0 ? (
        models.map(model => (
          <li key={model.model_id} className="list-group-item">
            {model.model_id}
          </li>
        ))
      ) : (
        <li className="list-group-item text-muted">(None)</li>
      )}
    </ul>
  </div>
);

// Function to process API data into Sankey format
const processDataForSankey = (models: Model[]): SankeyData => {
  const nodes: { name: string }[] = [];
  const links: { source: number; target: number; value: number }[] = [];
  const nodeIndexMap = new Map<string, number>();

  const addNode = (name: string) => {
    if (!nodeIndexMap.has(name)) {
      nodeIndexMap.set(name, nodes.length);
      nodes.push({ name });
    }
  };

  models.forEach(model => {
    const org = model.organization || 'Unknown Org';
    const risk = model.risk_category || 'Unknown Risk';
    const status = model.is_deployable ? 'Deployable' : 'Prohibited';

    addNode(org);
    addNode(risk);
    addNode(status);

    links.push({ source: nodeIndexMap.get(org)!, target: nodeIndexMap.get(risk)!, value: 1 });
    links.push({ source: nodeIndexMap.get(risk)!, target: nodeIndexMap.get(status)!, value: 1 });
  });

  return { nodes, links };
};


function App() {
  const [paginatedModels, setPaginatedModels] = useState<Model[]>([]);
  const [sankeyData, setSankeyData] = useState<SankeyData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalModels, setTotalModels] = useState(0);
  const modelsPerPage = 10;

  // Effect for paginated models
  useEffect(() => {
    const fetchPaginatedData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const skip = (currentPage - 1) * modelsPerPage;
        const res = await fetch(`${API_BASE_URL}/api/v1/models?skip=${skip}&limit=${modelsPerPage}`);
        if (!res.ok) {
          throw new Error('Network response was not ok for paginated models');
        }
        const data: PaginatedModelsResponse = await res.json();
        setPaginatedModels(data.models);
        setTotalModels(data.total_models);
      } catch (e: any) {
        setError('Failed to fetch data from the Cyprus API. Is the backend server running?');
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPaginatedData();
  }, [currentPage]);

  // Effect for Sankey chart data (fetch all)
  useEffect(() => {
    const fetchAllForSankey = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/v1/models?limit=100`);
        // console.log()
        if (!res.ok) {
          throw new Error('Network response was not ok for sankey data');
        }
        const data: PaginatedModelsResponse = await res.json();
        setSankeyData(processDataForSankey(data.models));
      } catch (e: any) {
        // This error is handled by the main error state
        console.error("Failed to fetch sankey data", e);
      }
    };

    fetchAllForSankey();
  }, []); // Runs only once on mount

  const deployableModels = paginatedModels.filter(m => m.is_deployable);
  const prohibitedModels = paginatedModels.filter(m => m.is_restricted);
  const systemicRiskModels = paginatedModels.filter(m => m.risk_category === 'high_risk');
  const totalPages = Math.ceil(totalModels / modelsPerPage);

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  return (
    <div className="App container-fluid p-4">
      <header className="mb-4">
        <h1 className="display-6">Cyprus AI Policy Dashboard</h1>
        <p className="text-muted">
          An interactive dashboard for monitoring AI model compliance.
        </p>
      </header>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      <main>
        <section className="mb-4">
          <h2>Policy Flow</h2>
          <div className="bg-light border rounded p-3">
            {sankeyData ? <SankeyChart data={sankeyData} /> : <p className="text-center text-muted">Loading Chart Data...</p>}
          </div>
        </section>

        <section className="mb-4">
          <h2>Policy Thresholds</h2>
          <div className="row">
            <div className="col-md-6">
              <label htmlFor="compute-slider" className="form-label">Compute Threshold (FLOPs)</label>
              <input type="range" className="form-range" id="compute-slider" min="1e24" max="1e26" step="1e24" disabled />
              <p className="text-center text-muted small">(UI Placeholder - Not Functional)</p>
            </div>
            <div className="col-md-6">
              <label htmlFor="risk-slider" className="form-label">Risk Score Threshold</label>
              <input type="range" className="form-range" id="risk-slider" min="0" max="1" step="0.1" disabled />
              <p className="text-center text-muted small">(UI Placeholder - Not Functional)</p>
            </div>
          </div>
        </section>

        <section>
          <h2>Model Compliance Lists</h2>
          <div className="row">
            <div className="col-md-3">
              <ModelList title="Deployable" models={deployableModels} isLoading={isLoading} />
            </div>
            <div className="col-md-3">
              <ModelList title="Prohibited" models={prohibitedModels} isLoading={isLoading} />
            </div>
            <div className="col-md-3">
              <ModelList title="Systemic Risk" models={systemicRiskModels} isLoading={isLoading} />
            </div>
            <div className="col-md-3">
              <ModelList title="All Models (Paginated)" models={paginatedModels} isLoading={isLoading} />
              <div className="d-flex justify-content-between align-items-center mt-2">
                <button className="btn btn-secondary btn-sm" onClick={handlePrevPage} disabled={currentPage === 1}>
                  Previous
                </button>
                <span className="small text-muted">
                  Page {currentPage} of {totalPages}
                </span>
                <button className="btn btn-secondary btn-sm" onClick={handleNextPage} disabled={currentPage >= totalPages}>
                  Next
                </button>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
