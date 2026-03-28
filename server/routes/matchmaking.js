import express from 'express';
import { requestService } from '../services/requestService.js';
import { database } from '../database.js';

const router = express.Router();

router.get('/request/:id', (req, res) => {
  const request = database.requests.find(r => r.id === req.params.id);
  if (!request) {
    return res.status(404).json({ error: 'Request not found' });
  }

  const matches = requestService.findMatches(request);
  const enrichedMatches = matches.map(m => ({
    expert: m.expert,
    matchScore: (m.score * 100 / 10).toFixed(1) + '%',
    rawScore: m.score,
    suggestion: `${m.expert.name} is an excellent match with ${m.expert.expertise.join(', ')} expertise.`
  }));

  res.json(enrichedMatches);
});

router.get('/expert/:id', (req, res) => {
  const expert = database.experts.find(e => e.id === req.params.id);
  if (!expert) {
    return res.status(404).json({ error: 'Expert not found' });
  }
  res.json(expert);
});

router.post('/assign', (req, res) => {
  const { requestId, expertId } = req.body;

  const request = database.requests.find(r => r.id === requestId);
  const expert = database.experts.find(e => e.id === expertId);

  if (!request || !expert) {
    return res.status(404).json({ error: 'Request or expert not found' });
  }

  if (!request.matchedUsers.includes(expertId)) {
    request.matchedUsers.push(expertId);
    expert.helpProvided++;
    request.status = 'in_progress';
  }

  res.json({ message: 'Expert assigned successfully', request, expert });
});

router.get('/experts/list/all', (req, res) => {
  res.json(database.experts);
});

export { router as matchmakingRoutes };
