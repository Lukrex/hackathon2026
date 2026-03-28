import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { requestRoutes } from './routes/requests.js';
import { matchmakingRoutes } from './routes/matchmaking.js';
import { emailRoutes } from './routes/email.js';
import { notionRoutes } from './routes/notion.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/requests', requestRoutes);
app.use('/api/matchmaking', matchmakingRoutes);
app.use('/api/email', emailRoutes);
app.use('/api/notion', notionRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`\n🚀 Community Help System API running on http://localhost:${PORT}`);
  console.log(`📊 Dashboard: http://localhost:3000`);
  console.log(`📝 API Docs: http://localhost:${PORT}/api/health\n`);
});

export default app;
