import React, { useState, useEffect } from "react";
import "./Insights.css";

interface InsightData {
  id: number;
  insight: string;
  created_at: string;
  type: string;
}

interface ApiService {
  name: string;
  endpoint: string;
  label: string;
}

interface KpiData {
  volume?: {
    total_opportunities: number;
    total_won: number;
    total_lost: number;
    win_rate: number;
    lost_rate: number;
    open_opportunities: number;
  };
  financials?: {
    won_order_value: number;
    avg_won_deal_size: number;
    expected_revenue: number;
    revenue_realization_rate: number;
  };
  product_region?: {
    product: {
      product_wise_orders: { [key: string]: number };
    };
  };
}

interface AiInsightsData {
  kpis?: {
    volume?: any;
    financials?: any;
    product_summary?: any;
  };
  insights?: string;
}

const typeServices: ApiService[] = [
  { name: "kpi", endpoint: "http://localhost:8000/kpi-all", label: "KPI" },
  { name: "ai-insights", endpoint: "http://localhost:8000/ai-insights", label: "AI Insights" }
];

const Insights: React.FC = () => {
  const [insights, setInsights] = useState<InsightData[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [activeFilter, setActiveFilter] = useState<string>("ai-insights");
  const [kpiData, setKpiData] = useState<KpiData | null>(null);
  const [aiInsightsData, setAiInsightsData] = useState<AiInsightsData | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Transform /ai-insights: split the `insights` string by newlines and clean each line
  const transformAiInsights = (data: any): InsightData[] => {
    const raw = data?.insights;
    if (!raw || typeof raw !== "string") return [];

    // split by newline and remove empty/whitespace lines
    const lines = raw
      .split("\n")
      .map((l: string) => l.trim())
      .filter((l: string) => l.length > 0)
      .map((l: string) => l.replace(/^[-\u2022\s]+/, "")); // remove leading - or • or spaces

    return lines.map((text: string, i: number) => ({
      id: i + 1,
      insight: text,
      created_at: new Date().toISOString(),
      type: "ai-insights"
    }));
  };

  // Transform /kpi-all response into KPI object
  const transformKpi = (data: any) => {
    if (!data) {
      setKpiData(null);
      return;
    }

    setKpiData(data);
  };

  const fetchSingle = async (service: ApiService) => {
    if (!service.endpoint) return { ok: true, data: null };
    const res = await fetch(service.endpoint, { cache: "no-store" });
    if (!res.ok) throw new Error(`${service.name} HTTP ${res.status}`);
    const data = await res.json();
    return { ok: true, data };
  };

  const fetchInsights = async (filterType: string) => {
    setLoading(true);
    setErrorMessage(null);
    setKpiData(null);
    setAiInsightsData(null);
    setInsights([]);
    
    try {
      const service = typeServices.find((s) => s.name === filterType);
      if (!service) {
        setErrorMessage("Unknown filter selected.");
        return;
      }

      const res = await fetchSingle(service);
      const data = res.data;

      if (service.name === "kpi") {
        transformKpi(data);
      } else if (service.name === "ai-insights") {
        setAiInsightsData(data);
        const insightsList = transformAiInsights(data);
        setInsights(insightsList);
      }
    } catch (error: any) {
      console.error("Error fetching insights:", error);
      setErrorMessage("Failed to load insights. See console for details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights(activeFilter);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeFilter]);

  const handleTypeFilter = (filterName: string) => {
    setActiveFilter(filterName);
  };

  return (
    <div className="insights-container">
      <div className="insights-header">
        <h1 className="insights-title">TTL AI Analysis</h1>
      </div>

      <div className="filter-section">
        <div className="filter-group">
          <div className="filter-buttons">
            {typeServices.map((service) => (
              <button
                key={service.name}
                className={`filter-btn ${activeFilter === service.name ? "filter-active" : ""}`}
                onClick={() => handleTypeFilter(service.name)}
                aria-pressed={activeFilter === service.name}
              >
                {service.label} {activeFilter === service.name ? "▾" : "↓"}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner" />
          <p>Loading insights...</p>
        </div>
      ) : (
        <div className="insights-list-wrapper">
          {activeFilter === "kpi" && kpiData && (
            <>
              <h2 className="section-title">Volume Metrics</h2>
              <div className="kpi-cards">
                <div className="kpi-card">
                  <div className="kpi-value">{kpiData.volume?.total_opportunities ?? "—"}</div>
                  <div className="kpi-label">Total Opportunities</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-value">{kpiData.volume?.total_won ?? "—"}</div>
                  <div className="kpi-label">Won</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-value">{kpiData.volume?.total_lost ?? "—"}</div>
                  <div className="kpi-label">Lost</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-value">
                    {kpiData.volume?.win_rate ? `${kpiData.volume.win_rate.toFixed(2)}%` : "—"}
                  </div>
                  <div className="kpi-label">Win Rate</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-value">
                    {kpiData.volume?.lost_rate ? `${kpiData.volume.lost_rate.toFixed(2)}%` : "—"}
                  </div>
                  <div className="kpi-label">Lost Rate</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-value">{kpiData.volume?.open_opportunities ?? "—"}</div>
                  <div className="kpi-label">Open Opportunities</div>
                </div>
              </div>

              <h2 className="section-title">Financial Metrics</h2>
              <div className="kpi-cards">
                <div className="kpi-card kpi-card-large">
                  <div className="kpi-value">
                    {kpiData.financials?.won_order_value
                      ? `₹${(kpiData.financials.won_order_value / 1e9).toFixed(2)}B`
                      : "—"}
                  </div>
                  <div className="kpi-label">Won Order Value</div>
                </div>
                <div className="kpi-card kpi-card-large">
                  <div className="kpi-value">
                    {kpiData.financials?.avg_won_deal_size
                      ? `₹${(kpiData.financials.avg_won_deal_size / 1e6).toFixed(2)}M`
                      : "—"}
                  </div>
                  <div className="kpi-label">Avg Won Deal Size</div>
                </div>
                <div className="kpi-card kpi-card-large">
                  <div className="kpi-value">
                    {kpiData.financials?.expected_revenue
                      ? `₹${(kpiData.financials.expected_revenue / 1e9).toFixed(2)}B`
                      : "—"}
                  </div>
                  <div className="kpi-label">Expected Revenue</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-value">
                    {kpiData.financials?.revenue_realization_rate
                      ? `${kpiData.financials.revenue_realization_rate.toFixed(1)}%`
                      : "—"}
                  </div>
                  <div className="kpi-label">Revenue Realization</div>
                </div>
              </div>

              {kpiData.product_region?.product?.product_wise_orders && (
                <>
                  <h2 className="section-title">Product-wise Orders</h2>
                  <div className="kpi-cards">
                    {Object.entries(kpiData.product_region.product.product_wise_orders).map(
                      ([product, count]) => (
                        <div className="kpi-card" key={product}>
                          <div className="kpi-value">{count}</div>
                          <div className="kpi-label">{product}</div>
                        </div>
                      )
                    )}
                  </div>
                </>
              )}
            </>
          )}

          {activeFilter === "ai-insights" && aiInsightsData && (
            <>
              <h2 className="section-title">Key Performance Indicators</h2>
              <div className="kpi-cards">
                <div className="kpi-card">
                  <div className="kpi-value">
                    {aiInsightsData.kpis?.volume?.total_opportunities ?? "—"}
                  </div>
                  <div className="kpi-label">Total Opportunities</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-value">{aiInsightsData.kpis?.volume?.total_won ?? "—"}</div>
                  <div className="kpi-label">Won</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-value">{aiInsightsData.kpis?.volume?.total_lost ?? "—"}</div>
                  <div className="kpi-label">Lost</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-value">
                    {aiInsightsData.kpis?.volume?.win_rate
                      ? `${aiInsightsData.kpis.volume.win_rate.toFixed(2)}%`
                      : "—"}
                  </div>
                  <div className="kpi-label">Win Rate</div>
                </div>
              </div>

              <div className="kpi-cards">
                <div className="kpi-card kpi-card-large">
                  <div className="kpi-value">
                    {aiInsightsData.kpis?.financials?.won_order_value
                      ? `₹${(aiInsightsData.kpis.financials.won_order_value / 1e9).toFixed(2)}B`
                      : "—"}
                  </div>
                  <div className="kpi-label">Won Order Value</div>
                </div>
                <div className="kpi-card kpi-card-large">
                  <div className="kpi-value">
                    {aiInsightsData.kpis?.financials?.expected_revenue
                      ? `₹${(aiInsightsData.kpis.financials.expected_revenue / 1e9).toFixed(2)}B`
                      : "—"}
                  </div>
                  <div className="kpi-label">Expected Revenue</div>
                </div>
              </div>

              <h2 className="section-title">AI-Generated Insights</h2>
              {insights.length > 0 && (
                <div className="insights-list">
                  {insights.map((insight, index) => (
                    <div key={`${insight.type}-${insight.id}-${index}`} className="insight-card">
                      <div className="insight-icon" aria-hidden>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                          <path
                            d="M13 7L19 13L13 19M5 7L11 13L5 19"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      </div>
                      <div className="insight-content">
                        <p className="insight-text">
                          <span className="insight-number">{index + 1}.</span> {insight.insight}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          {errorMessage && (
            <div className="error-state">
              <p>{errorMessage}</p>
            </div>
          )}

          {!errorMessage && !kpiData && !aiInsightsData && insights.length === 0 && (
            <div className="no-data">
              <p>No data available for the selected filter.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Insights;