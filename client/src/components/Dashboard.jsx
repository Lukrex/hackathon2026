import React, { useState, useEffect } from 'react';

const API_URL = 'http://localhost:3001/api';

export default function Dashboard({ requests }) {
  const [metrics, setMetrics] = useState({
    totalRequests: 0,
    openRequests: 0,
    inProgressRequests: 0,
    resolvedRequests: 0,
    totalValue: 0,
    expertEngagements: 0
  });

  useEffect(() => {
    const open = requests.filter(r => r.status === 'open').length;
    const inProgress = requests.filter(r => r.status === 'in_progress').length;
    const resolved = requests.filter(r => r.resolved).length;
    const totalValue = requests.reduce((sum, r) => sum + r.value, 0);

    setMetrics({
      totalRequests: requests.length,
      openRequests: open,
      inProgressRequests: inProgress,
      resolvedRequests: resolved,
      totalValue,
      expertEngagements: requests.reduce((sum, r) => sum + r.matchedUsers.length, 0)
    });
  }, [requests]);

  const categoryCount = {};
  requests.forEach(r => {
    categoryCount[r.category] = (categoryCount[r.category] || 0) + 1;
  });

  return (
    <div className="dashboard">
      <h2>📊 Prehľad systému</h2>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-value">{metrics.totalRequests}</div>
          <div className="metric-label">Celkové žiadosti</div>
        </div>
        <div className="metric-card highlight">
          <div className="metric-value">{metrics.openRequests}</div>
          <div className="metric-label">Otvorené žiadosti</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{metrics.inProgressRequests}</div>
          <div className="metric-label">V spracovaní</div>
        </div>
        <div className="metric-card success">
          <div className="metric-value">{metrics.resolvedRequests}</div>
          <div className="metric-label">Vyriešené</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{metrics.expertEngagements}</div>
          <div className="metric-label">Expertné zapojenia</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{metrics.totalValue}</div>
          <div className="metric-label">Celková hodnota</div>
        </div>
      </div>

      <div className="card">
        <h3>📂 Kategórie</h3>
        {Object.entries(categoryCount).map(([cat, count]) => (
          <div key={cat} style={{ marginBottom: '0.5rem' }}>
            <strong>{cat}:</strong> {count}
          </div>
        ))}
      </div>
    </div>
  );
}
