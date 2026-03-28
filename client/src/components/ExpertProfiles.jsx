import React from 'react';

export default function ExpertProfiles({ experts }) {
  return (
    <div className="experts-container">
      <h2>👥 Komunita expertov ({experts.length})</h2>

      <div className="experts-grid">
        {experts.map(expert => (
          <div key={expert.id} className="expert-card card">
            <h3>{expert.name}</h3>
            <p>{expert.bio}</p>

            <div className="expertise-section">
              <h4>Odbornosti:</h4>
              <div className="expertise-list">
                {expert.expertise.map(exp => (
                  <span key={exp} className="expertise-tag">{exp}</span>
                ))}
              </div>
            </div>

            <div className="expert-stats">
              <div className="stat">
                <span className="stat-value">{expert.helpProvided}</span>
                <span className="stat-label">Pomoci</span>
              </div>
              <div className="stat">
                <span className="stat-value">{expert.availability}</span>
                <span className="stat-label">Dostupnosť</span>
              </div>
            </div>

            <a href={`mailto:${expert.email}`} className="btn btn-primary" style={{ display: 'block', textAlign: 'center', textDecoration: 'none' }}>
              📧 Kontaktovať
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
