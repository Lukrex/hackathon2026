// In-memory database for demo
export const database = {
  requests: [
    {
      id: 'req-001',
      title: 'Hľadáme senior React vývojára',
      description: 'Potrebujeme skúseného React vývojára na projekt. Min. 5 rokov skúsenosti s React.',
      category: 'hiring',
      priority: 'high',
      requester: { id: 'user-1', name: 'StartupXYZ', email: 'hello@startupxyz.sk' },
      createdAt: new Date('2026-03-20'),
      status: 'open',
      tags: ['tech', 'hiring', 'remote ok'],
      matchedUsers: [],
      resolved: false,
      value: 8
    },
    {
      id: 'req-002',
      title: 'Hľadáme VC pre seed financovanie',
      description: 'Máme vyvinutý MVP a hľadáme 200k EUR funding. B2B SaaS v oblasti HR tech.',
      category: 'investment',
      priority: 'high',
      requester: { id: 'user-2', name: 'TechStartupABC', email: 'founders@abc.sk' },
      createdAt: new Date('2026-03-18'),
      status: 'open',
      tags: ['finance', 'saas', 'seed'],
      matchedUsers: [],
      resolved: false,
      value: 9
    },
    {
      id: 'req-003',
      title: 'Pomoc s GTM stratégiou',
      description: 'Potrebujeme konzultáciu na go-to-market stratéiu pre europske trhy.',
      category: 'consulting',
      priority: 'medium',
      requester: { id: 'user-3', name: 'InnovateLabs', email: 'team@innovatelabs.sk' },
      createdAt: new Date('2026-03-15'),
      status: 'open',
      tags: ['strategy', 'gtm', 'expansion'],
      matchedUsers: [],
      resolved: false,
      value: 6
    },
    {
      id: 'req-004',
      title: 'Hľadáme speaker na tech event',
      description: 'Hľadáme skúseného tech speakera na konferenciu. Téma: AI v startupoch.',
      category: 'speaking',
      priority: 'low',
      requester: { id: 'user-4', name: 'TechConf2026', email: 'speakers@techconf.sk' },
      createdAt: new Date('2026-03-10'),
      status: 'open',
      tags: ['event', 'speaking', 'ai'],
      matchedUsers: [],
      resolved: false,
      value: 4
    },
    {
      id: 'req-005',
      title: 'Potrebujeme copywriting help',
      description: 'Pomoc s copywritingom pre web a marketing materiály.',
      category: 'marketing',
      priority: 'medium',
      requester: { id: 'user-5', name: 'DesignStudio', email: 'hello@designstudio.sk' },
      createdAt: new Date('2026-03-08'),
      status: 'in_progress',
      tags: ['marketing', 'content', 'copywriting'],
      matchedUsers: ['expert-3'],
      resolved: false,
      value: 5
    }
  ],
  experts: [
    {
      id: 'expert-1',
      name: 'Peter Kováč',
      email: 'peter@experts.sk',
      expertise: ['hiring', 'recruitment', 'hr', 'tech'],
      bio: 'Recruitment expert s 10 rokmi skúsenosti v tech industriii',
      helpProvided: 8
    },
    {
      id: 'expert-2',
      name: 'Jana Novotná',
      email: 'jana@vcfunduators.sk',
      expertise: ['investment', 'finance', 'saas', 'seed'],
      bio: 'VC investor zameraný na early-stage startupy v CEE regióne',
      helpProvided: 12
    },
    {
      id: 'expert-3',
      name: 'Marko Szabó',
      email: 'marko@marketing.sk',
      expertise: ['marketing', 'gtm', 'copywriting', 'content'],
      bio: 'Marketing strategist s skúsenosťou v európskych startupoch',
      helpProvided: 6
    },
    {
      id: 'expert-4',
      name: 'Lucia Poláčková',
      email: 'lucia@consulting.sk',
      expertise: ['consulting', 'strategy', 'expansion', 'business'],
      bio: 'Consulting expert na business development a market entry',
      helpProvided: 14
    },
    {
      id: 'expert-5',
      name: 'David Tóth',
      email: 'david@speaking.sk',
      expertise: ['speaking', 'ai', 'tech', 'event'],
      bio: 'Tech speaker a evangelist s vášňou pre AI',
      helpProvided: 9
    }
  ],
  metrics: {
    totalRequests: 5,
    resolvedRequests: 0,
    totalValue: 32,
    expertEngagements: 1
  }
};
