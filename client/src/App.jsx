import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import Dashboard from './components/Dashboard';
import RequestList from './components/RequestList';
import NewRequestForm from './components/NewRequestForm';
import ExpertProfiles from './components/ExpertProfiles';
import Matchmaking from './components/Matchmaking';

const API_URL = 'http://localhost:3001/api';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [requests, setRequests] = useState([]);
  const [experts, setExperts] = useState([]);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRequests();
    fetchExperts();
  }, []);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/requests?sort=priority`);
      setRequests(response.data);
    } catch (error) {
      console.error('Failed to fetch requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchExperts = async () => {
    try {
      const response = await axios.get(`${API_URL}/matchmaking/experts/list/all`);
      setExperts(response.data);
    } catch (error) {
      console.error('Failed to fetch experts:', error);
    }
  };

  const handleNewRequest = async (formData) => {
    try {
      const response = await axios.post(`${API_URL}/requests`, {
        title: formData.title,
        description: formData.description,
        requester: {
          id: `user-${Date.now()}`,
          name: formData.requesterName,
          email: formData.requesterEmail
        },
        tags: formData.tags ? formData.tags.split(',').map(t => t.trim()) : [],
        value: parseInt(formData.value) || 5
      });

      await axios.post(`${API_URL}/email/send-confirmation`, {
        requestId: response.data.request.id
      });

      setShowForm(false);
      fetchRequests();
      alert('✅ Žiadosť bola vytvorená!');
    } catch (error) {
      alert('❌ Chyba pri vytáraní žiadosti');
      console.error(error);
    }
  };

  const handleSelectRequest = (request) => {
    setSelectedRequest(request);
    setCurrentView('matchmaking');
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>🤝 Community Help System</h1>
          <p>Efektívna správa žiadostí pomoci v komunite</p>
        </div>
        <nav className="nav">
          <button
            className={`nav-btn ${currentView === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentView('dashboard')}
          >
            📊 Dashboard
          </button>
          <button
            className={`nav-btn ${currentView === 'requests' ? 'active' : ''}`}
            onClick={() => setCurrentView('requests')}
          >
            📋 Žiadosti ({requests.length})
          </button>
          <button
            className={`nav-btn ${currentView === 'experts' ? 'active' : ''}`}
            onClick={() => setCurrentView('experts')}
          >
            👥 Experty ({experts.length})
          </button>
          <button
            className="nav-btn btn-new-request"
            onClick={() => setShowForm(true)}
          >
            ➕ Nová žiadosť
          </button>
        </nav>
      </header>

      <main className="main-content">
        {currentView === 'dashboard' && <Dashboard requests={requests} />}
        {currentView === 'requests' && (
          <RequestList
            requests={requests}
            onSelectRequest={handleSelectRequest}
            loading={loading}
          />
        )}
        {currentView === 'experts' && <ExpertProfiles experts={experts} />}
        {currentView === 'matchmaking' && selectedRequest && (
          <Matchmaking request={selectedRequest} onBack={() => setCurrentView('requests')} />
        )}
      </main>

      {showForm && (
        <NewRequestForm
          onSubmit={handleNewRequest}
          onClose={() => setShowForm(false)}
        />
      )}
    </div>
  );
}

export default App;
