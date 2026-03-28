from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from server.models import Category, Skill, Expert, Request, ExpertMatch
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Create demo data for the Community Help System'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Creating demo data...")

        # Create categories
        categories_data = [
            ('hiring', '🔍 Hľadanie zamestnanca', 'Pomoc pri hľadaní talentov do tímu'),
            ('investment', '💰 Hľadanie investora', 'Získavanie financií a kapitálu'),
            ('consulting', '📊 Konzultácia', 'Odborné rady a stratégiu'),
            ('marketing', '📢 Marketing pomoc', 'Copywriting, branding, reklama'),
            ('speaking', '🎤 Speaking príležitosť', 'Event, konferencie, prednášky'),
            ('networking', '🤝 Networking', 'Spojenie s ľuďmi z komunity'),
            ('sales', '💼 Sales podpora', 'Pomoc s predajom a obchodom'),
        ]

        categories = {}
        for code, name, desc in categories_data:
            cat, created = Category.objects.get_or_create(
                name=code,
                defaults={'description': desc, 'icon': name.split()[0]}
            )
            categories[code] = cat
            if created:
                self.stdout.write(f"✅ Category created: {name}")

        skill_names = [
            'React', 'Node.js', 'GTM', 'Product Management',
            'Fundraising', 'Investor Relations', 'Business Strategy',
            'Digital Marketing', 'Branding', 'Copywriting', 'Sales',
            'Recruiting', 'HR', 'Team Building', 'Scaling', 'AI/ML', 'Web3'
        ]
        skills = {}
        for skill_name in skill_names:
            skill, _ = Skill.objects.get_or_create(name=skill_name)
            skills[skill_name] = skill

        # Create demo experts
        experts_data = [
            {
                'username': 'anna.novak',
                'first_name': 'Anna',
                'last_name': 'Nováková',
                'email': 'anna.novak@example.com',
                'bio': '10+ rokov skúseností v startupoch, specialista na GTM a scaling',
                'expertise': 'React, Node.js, GTM, Scaling, Product Management',
                'availability': 'high',
            },
            {
                'username': 'peter.sisko',
                'first_name': 'Peter',
                'last_name': 'Síšo',
                'email': 'peter.sisko@example.com',
                'bio': 'VC investor a mentor, pomáham startupom s fundraisingom',
                'expertise': 'Fundraising, Investor relations, VC, Business Strategy',
                'availability': 'medium',
            },
            {
                'username': 'maria.rehakova',
                'first_name': 'Mária',
                'last_name': 'Reháková',
                'email': 'maria.rehakova@example.com',
                'bio': 'Marketing guru s fokusom na digitálny marketing a branding',
                'expertise': 'Digital Marketing, Branding, Copywriting, Social Media',
                'availability': 'medium',
            },
            {
                'username': 'jozef.koval',
                'first_name': 'Jozef',
                'last_name': 'Kovál',
                'email': 'jozef.koval@example.com',
                'bio': 'HR expert a talent scout, pomáham startupom budovať tímy',
                'expertise': 'Recruiting, HR, Team Building, Culture',
                'availability': 'high',
            },
            {
                'username': 'lucia.svoboda',
                'first_name': 'Lucia',
                'last_name': 'Sloboda',
                'email': 'lucia.svoboda@example.com',
                'bio': 'Sales expert s 15+ rokmi v B2B, školiteľka a konsultantka',
                'expertise': 'Sales, B2B, Account Management, Sales Training',
                'availability': 'low',
            },
        ]

        experts = {}
        for exp_data in experts_data:
            user, created = User.objects.get_or_create(
                username=exp_data['username'],
                defaults={
                    'first_name': exp_data['first_name'],
                    'last_name': exp_data['last_name'],
                    'email': exp_data['email'],
                }
            )
            if created:
                user.set_password('demo123')
                user.save()

            expert, expert_created = Expert.objects.get_or_create(
                user=user,
                defaults={
                    'bio': exp_data['bio'],
                    'expertise': exp_data['expertise'],
                    'availability': exp_data['availability'],
                    'help_provided': random.randint(2, 12),
                }
            )

            # Assign skill objects based on expertise tags
            skill_set = []
            for part in exp_data['expertise'].split(','):
                key = part.strip()
                if key in skills:
                    skill_set.append(skills[key])
            if skill_set:
                expert.skills.set(skill_set)

            experts[exp_data['username']] = expert

            if expert_created:
                self.stdout.write(f"✅ Vytvorený expert: {exp_data['first_name']} {exp_data['last_name']}")

        # Create demo requests
        requests_data = [
            {
                'title': 'Looking for senior React developer',
                'description': 'Our startup is looking for a senior React developer to join the team. '
                              'Minimum 5 years experience in React + Node.js. Remote full-time.',
                'requester_name': 'Martin Gal',
                'requester_email': 'martin@startup.com',
                'is_corporate': True,
                'company_name': 'TechLaunch Inc.',
                'company_email': 'hr@techlaunch.com',
                'due_date': datetime.now().date() + timedelta(days=21),
                'target_experience': 'senior',
                'target_skills': [skills['React'], skills['Node.js']],
                'category': categories['hiring'],
                'priority': 'high',
                'value_score': 9,
            },
            {
                'title': 'Potrebujeme help s GTM stratégiou',
                'description': 'Máme nový produkt a potrebujeme poradiť s go-to-market stratégiou. '
                              'Hľadáme niekoho s skúsenosťami v scaling B2B startupov. '
                              'Chceme tím, ktorý nám pomôže s market entry a pricing stratégiou.',
                'requester_name': 'Zuzana Kováčová',
                'requester_email': 'zuzana@startup.sk',
                'category': categories['consulting'],
                'priority': 'high',
                'value_score': 8,
            },
            {
                'title': 'Hľadám investora pre nasz FinTech startup',
                'description': 'Naš fintech startup je v seed fáze a hľadáme seed investora alebo VC firmu. '
                              'Už máme MVP a pilotných klientov. Chceme poradiť aj s pitchingom.',
                'requester_name': 'Vladimír Horváth',
                'requester_email': 'vladimir@fintech.sk',
                'category': categories['investment'],
                'priority': 'critical',
                'value_score': 10,
            },
            {
                'title': 'Potrebujeme help s Instagram marketingom',
                'description': 'Máme e-commerce shop a nedarí sa nám s organic reach na Instagramme. '
                              'Potrebujeme niekoho, kto nám pomôže s content stratégiou, copywritingom a growth hackingom. '
                              'Máme budget na paid ads, ale chceme najskôr fix organic stratégiu.',
                'requester_name': 'Kristína Boháčová',
                'requester_email': 'kristina@eshop.sk',
                'category': categories['marketing'],
                'priority': 'medium',
                'value_score': 7,
            },
            {
                'title': 'Speaker potrebný na tech conference',
                'description': 'Organizujeme tech konferenciu v apríli a hľadáme zaujímavých speakerov. '
                              'Témy: AI/ML, Web3, Scaling. Záujem o skúsené founders a tech leaders. '
                              'Honorár + cestovné sa riešia.',
                'requester_name': 'Tomáš Šimko',
                'requester_email': 'tomas@allevents.sk',
                'category': categories['speaking'],
                'priority': 'medium',
                'value_score': 6,
            },
        ]

        requests_created = []
        for req_data in requests_data:
            req, created = Request.objects.get_or_create(
                title=req_data['title'],
                defaults={
                    'description': req_data.get('description', ''),
                    'requester_name': req_data.get('requester_name', ''),
                    'requester_email': req_data.get('requester_email', ''),
                    'category': req_data.get('category'),
                    'priority': req_data.get('priority', 'medium'),
                    'value_score': req_data.get('value_score', 5),
                    'status': random.choice(['open', 'in_review', 'in_progress']),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 10)),
                    'is_corporate': req_data.get('is_corporate', False),
                    'company_name': req_data.get('company_name', ''),
                    'company_email': req_data.get('company_email', ''),
                    'due_date': req_data.get('due_date'),
                    'requester_type': req_data.get('requester_type', 'community_member'),
                    'target_experience': req_data.get('target_experience', ''),
                }
            )

            if created:
                self.stdout.write(f"✅ Vytvorená žiadosť: {req_data['title']}")
                requests_created.append(req)

                # Assign target skills for corporate needs
                target_skills = req_data.get('target_skills', [])
                if target_skills:
                    req.target_skills.set(target_skills)

                # Assign random experts
                num_experts = random.randint(1, 3)
                random_experts = random.sample(list(experts.values()), min(num_experts, len(experts)))

                for expert in random_experts:
                    req.assigned_experts.add(expert)

                # Create expert matches
                for expert in list(experts.values())[:random.randint(2, 4)]:
                    match_score = random.randint(45, 95)
                    ExpertMatch.objects.get_or_create(
                        request=req,
                        expert=expert,
                        defaults={
                            'match_score': match_score,
                            'reasoning': 'Keyword overlap detektované, kategória zhodná',
                        }
                    )

        self.stdout.write(self.style.SUCCESS('\n✅ Demo data vytvorené úspešne!'))
        self.stdout.write(f"\nCreated:")
        self.stdout.write(f"  - {len(categories)} categories")
        self.stdout.write(f"  - {len(experts)} experts")
        self.stdout.write(f"  - {len(requests_created)} requests")
        self.stdout.write(f"\n🚀 Spustite Django development server:")
        self.stdout.write(f"  python manage.py runserver")
        self.stdout.write(f"\n📊 Pristúpte k admin panelu:")
        self.stdout.write(f"  http://localhost:8000/admin/")
        self.stdout.write(f"\n📱 API je dostupné na:")
        self.stdout.write(f"  http://localhost:8000/api/")
