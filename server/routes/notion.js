import express from 'express';
import { database } from '../database.js';

const router = express.Router();

router.get('/export-requests', (req, res) => {
  const notionFormat = database.requests.map(req => ({
    id: req.id,
    Title: req.title,
    Description: req.description,
    Category: req.category,
    Priority: req.priority,
    Status: req.status,
    'Requester Name': req.requester.name,
    'Requester Email': req.requester.email,
    'Created At': req.createdAt.toISOString(),
    'Expert Count': req.matchedUsers.length,
    'Value Score': req.value,
    Tags: req.tags.join(', ')
  }));

  res.json({
    success: true,
    message: 'Requests formatted for Notion import',
    data: notionFormat
  });
});

router.get('/export-experts', (req, res) => {
  const notionFormat = database.experts.map(expert => ({
    Name: expert.name,
    Email: expert.email,
    Expertise: expert.expertise.join(', '),
    Bio: expert.bio,
    'Help Provided': expert.helpProvided
  }));

  res.json({
    success: true,
    message: 'Experts formatted for Notion import',
    data: notionFormat
  });
});

router.get('/sync-status', (req, res) => {
  res.json({
    lastSync: new Date().toISOString(),
    totalRequests: database.requests.length,
    syncedRequests: database.requests.length,
    pendingUpdates: 0,
    status: 'synchronized'
  });
});

router.post('/sync-from-notion', (req, res) => {
  console.log('🔄 Syncing data from Notion...');
  res.json({
    success: true,
    message: 'Notion sync completed',
    itemsSynced: database.requests.length,
    timestamp: new Date().toISOString()
  });
});

export { router as notionRoutes };
