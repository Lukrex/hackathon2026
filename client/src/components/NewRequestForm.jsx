import React from 'react';

export default function NewRequestForm({ onSubmit, onClose }) {
  const [formData, setFormData] = React.useState({
    title: '',
    description: '',
    requesterName: '',
    requesterEmail: '',
    tags: '',
    value: '5'
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
    setFormData({
      title: '',
      description: '',
      requesterName: '',
      requesterEmail: '',
      tags: '',
      value: '5'
    });
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <div className="modal-header">
          <h2>➕ Nová žiadosť o pomoc</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="requesterName">Vaše meno</label>
            <input
              type="text"
              id="requesterName"
              name="requesterName"
              value={formData.requesterName}
              onChange={handleChange}
              placeholder="Startup/Osoba"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="requesterEmail">Váš email</label>
            <input
              type="email"
              id="requesterEmail"
              name="requesterEmail"
              value={formData.requesterEmail}
              onChange={handleChange}
              placeholder="hello@example.sk"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="title">Názov žiadosti</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="Napr. Hľadáme senior React vývojára"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Podrobný popis</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Popíšte čo presne potrebujete..."
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="tags">Tagy (odddelené čiarkami)</label>
            <input
              type="text"
              id="tags"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              placeholder="tech, remote, startup..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="value">Hodnota žiadosti (1-10)</label>
            <select
              id="value"
              name="value"
              value={formData.value}
              onChange={handleChange}
            >
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(v => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
          </div>

          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Zrušiť
            </button>
            <button type="submit" className="btn btn-primary">
              ✓ Vytvoriť žiadosť
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
