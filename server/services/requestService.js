import { database } from '../database.js';

export const requestService = {
  categorizeRequest(title, description) {
    const text = (title + ' ' + description).toLowerCase();

    const categories = {
      'hiring': ['vývojár', 'developer', 'programátor', 'hľadáme', 'need', 'react', 'javascript', 'python'],
      'investment': ['financovanie', 'funding', 'investor', 'seed', 'vc', 'capital'],
      'consulting': ['konzultácia', 'stratégia', 'strategy', 'advise', 'gtm'],
      'marketing': ['marketing', 'copywriting', 'content', 'seo'],
      'speaking': ['speaker', 'event', 'konferencia'],
      'networking': ['spoznať', 'connect', 'network']
    };

    for (const [category, keywords] of Object.entries(categories)) {
      if (keywords.some(k => text.includes(k))) {
        return category;
      }
    }
    return 'other';
  },

  prioritizeRequest(request) {
    let score = 0;
    const daysOld = (new Date() - new Date(request.createdAt)) / (1000 * 60 * 60 * 24);
    score += Math.max(10 - daysOld, 0);
    score -= request.matchedUsers.length * 2;

    const text = (request.title + ' ' + request.description).toLowerCase();
    if (text.includes('urgent') || text.includes('asap')) score += 5;

    if (request.status === 'open') score += 4;

    if (score >= 14) return 'high';
    if (score >= 8) return 'medium';
    return 'low';
  },

  findMatches(request) {
    const requestCategory = request.category;
    const matches = database.experts
      .map(expert => {
        let score = 0;
        if (expert.expertise.includes(requestCategory)) score += 5;

        const keywords = expert.expertise;
        const reqText = (request.title + ' ' + request.description).toLowerCase();
        const matchingKeywords = keywords.filter(k => reqText.includes(k)).length;
        score += matchingKeywords;

        const availabilityScore = { high: 3, medium: 1, low: 0 };
        score += availabilityScore[expert.availability] || 0;
        score += Math.max(10 - expert.helpProvided, 0) * 0.5;

        return { expert, score };
      })
      .filter(m => m.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 3);

    return matches;
  },

  createRequest(data) {
    const category = this.categorizeRequest(data.title, data.description);
    const priority = this.prioritizeRequest({
      ...data,
      category,
      status: 'open',
      matchedUsers: [],
      createdAt: new Date()
    });

    const newRequest = {
      id: `req-${Date.now()}`,
      title: data.title,
      description: data.description,
      category,
      priority,
      requester: data.requester,
      createdAt: new Date(),
      status: 'open',
      tags: data.tags || [],
      matchedUsers: [],
      resolved: false,
      value: data.value || 5
    };

    database.requests.push(newRequest);
    database.metrics.totalRequests++;

    const matches = this.findMatches(newRequest);
    return { request: newRequest, matches };
  },

  getAllRequests(sort = 'priority') {
    let requests = [...database.requests];

    if (sort === 'priority') {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      requests.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
    } else if (sort === 'recent') {
      requests.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    }

    return requests;
  },

  updateRequest(requestId, updates) {
    const request = database.requests.find(r => r.id === requestId);
    if (!request) return null;

    Object.assign(request, updates);
    if (updates.resolved === true) {
      database.metrics.resolvedRequests++;
    }

    return request;
  }
};
