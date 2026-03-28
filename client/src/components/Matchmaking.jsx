import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:3001/api';

export default function Matchmaking({ request, onBack }) {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMatches();
  }, [request]);

  const fetchMatches = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/matchmaking/request/${request.id}`);
      setMatches(response.data);
    } catch (error) {
      console.error('Failed to fetch matches:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAssignExpert = async (expertId) => {
    try {
      await axios.post(`${API_URL}/matchmaking/assign`, {
        requestId: request.id,
        expertId
      });
      alert('✅ Expert bol priradený!');
      onBack();
    } catch (error) {
      alert('❌ Chyba pri priradení');
    }
  };

  return (
    <div className="matchmaking-container">
      <button className="btn btn-secondary" onClick={onBack}>← Späť</button>

      <div className="card">
        <h2>{request.title}</h2>
        <p>{request.description}</p>
        <div>
          <span className={`badge category-${request.category}`}>{request.category}</span>
          <span className={`badge priority-${request.priority}`}>{request.priority}</span>
        </div>
      </div>

      <h3>👥 Odporúčaní experty</h3>

      {loading ? (
        <p>Hľadám expertov...</p>
      ) : matches.length === 0 ? (
        <p>Žiadni vhodní experty nenájdení.</p>
      ) : (
        <div className="matches-grid">
          {matches.map((match, idx) => (
            <div key={match.expert.id} className="match-card card">
              <div className="match-rank">#{idx + 1}</div>
              <div className="match-score">{match.matchScore}</div>
              <h4>{match.expert.name}</h4>
              <p>{match.expert.bio}</p>
              <div>
                {match.expert.expertise.slice(0, 3).map(exp => (
                  <span key={exp} className="tag">{exp}</span>
                ))}
              </div>
              <button
                className="btn btn-success"
                onClick={() => handleAssignExpert(match.expert.id)}
              >
                ✓ Priradiť
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
