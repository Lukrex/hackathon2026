import React from 'react';

export default function RequestList({ requests, onSelectRequest, loading }) {
  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <p>Načítavam žiadosti...</p>
      </div>
    );
  }

  return (
    <div className="request-list">
      <h2>📋 Všetky žiadosti ({requests.length})</h2>

      {requests.length === 0 ? (
        <div className="card">
          <p>Nie sú žiadne žiadosti.</p>
        </div>
      ) : (
        <div className="requests-table-container">
          <table className="requests-table">
            <thead>
              <tr>
                <th>Názov</th>
                <th>Kategória</th>
                <th>Priorita</th>
                <th>Stav</th>
                <th>Experty</th>
                <th>Akcia</th>
              </tr>
            </thead>
            <tbody>
              {requests.map(req => (
                <tr key={req.id}>
                  <td><strong>{req.title}</strong></td>
                  <td><span className={`badge category-${req.category}`}>{req.category}</span></td>
                  <td><span className={`badge priority-${req.priority}`}>{req.priority}</span></td>
                  <td><span className={`badge status-${req.status}`}>{req.status}</span></td>
                  <td>{req.matchedUsers.length}</td>
                  <td>
                    <button className="btn-small" onClick={() => onSelectRequest(req)}>
                      🎯 Match
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
