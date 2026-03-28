import express from 'express';
import { requestService } from '../services/requestService.js';
import { database } from '../database.js';

const router = express.Router();

router.get('/', (req, res) => {
  const sort = req.query.sort || 'priority';
  const requests = requestService.getAllRequests(sort);
  res.json(requests);
});

router.get('/:id', (req, res) => {
  const request = database.requests.find(r => r.id === req.params.id);
  if (!request) {
    return res.status(404).json({ error: 'Request not found' });
  }
  res.json(request);
});

router.post('/', (req, res) => {
  const { title, description, requester, tags, value } = req.body;

  if (!title || !description || !requester) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const { request, matches } = requestService.createRequest({
    title,
    description,
    requester,
    tags,
    value
  });

  res.status(201).json({ request, matches });
});

router.put('/:id', (req, res) => {
  const request = requestService.updateRequest(req.params.id, req.body);
  if (!request) {
    return res.status(404).json({ error: 'Request not found' });
  }
  res.json(request);
});

export { router as requestRoutes };
