"""
Notion API Integration for Community Help System

Syncs requests and expert data to Notion database
"""
import json
import requests
from django.conf import settings
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class NotionIntegrator:
    """Handle integration with Notion API"""

    BASE_URL = 'https://api.notion.com/v1'
    VERSION = '2023-06-21'

    def __init__(self):
        self.api_key = settings.NOTION_API_KEY
        self.database_id = settings.NOTION_DATABASE_ID
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Notion-Version': self.VERSION,
            'Content-Type': 'application/json',
        }

    def is_configured(self) -> bool:
        """Check if Notion is properly configured"""
        return bool(self.api_key and self.database_id)

    def export_requests_to_csv(self, requests_queryset) -> List[Dict]:
        """Export requests in CSV-compatible format"""
        data = []
        for req in requests_queryset:
            data.append({
                'ID': req.id,
                'Title': req.title,
                'Status': req.get_status_display(),
                'Priority': req.get_priority_display(),
                'Category': req.get_category_display() if req.category else '',
                'Created': req.created_at.isoformat(),
                'Requester': req.requester_name,
                'Email': req.requester_email,
                'Value Score': req.value_score,
                'Assigned Experts': ', '.join([
                    e.user.get_full_name() for e in req.assigned_experts.all()
                ]),
            })
        return data

    def export_experts_to_csv(self, experts_queryset) -> List[Dict]:
        """Export experts in CSV-compatible format"""
        data = []
        for expert in experts_queryset:
            data.append({
                'Name': expert.user.get_full_name(),
                'Email': expert.user.email,
                'Bio': expert.bio,
                'Expertise': expert.expertise,
                'Availability': expert.get_availability_display(),
                'Help Provided': expert.help_provided,
                'Joined': expert.created_at.isoformat(),
            })
        return data

    def sync_requests_to_notion(self, requests_queryset):
        """
        Sync requests to Notion database
        Requires Notion database with properties:
        - Title (title)
        - Status (select)
        - Priority (select)
        - Category (select)
        - Requester (text)
        - Email (email)
        - Value (number)
        - Experts (relation)
        """
        if not self.is_configured():
            logger.warning("Notion not configured. Skipping sync.")
            return False

        try:
            for req in requests_queryset:
                # Prepare Notion page properties
                properties = {
                    'Title': {
                        'title': [
                            {
                                'text': {
                                    'content': req.title,
                                }
                            }
                        ]
                    },
                    'Status': {
                        'select': {
                            'name': req.get_status_display()
                        }
                    },
                    'Priority': {
                        'select': {
                            'name': req.get_priority_display()
                        }
                    },
                    'Category': {
                        'select': {
                            'name': req.get_category_display() if req.category else 'Other'
                        }
                    },
                    'Requester': {
                        'rich_text': [
                            {
                                'text': {
                                    'content': req.requester_name
                                }
                            }
                        ]
                    },
                    'Email': {
                        'email': req.requester_email
                    },
                    'Value': {
                        'number': req.value_score
                    },
                    'Description': {
                        'rich_text': [
                            {
                                'text': {
                                    'content': req.description[:2000]  # Notion limit
                                }
                            }
                        ]
                    }
                }

                # Create or update page
                response = requests.post(
                    f'{self.BASE_URL}/pages',
                    headers=self.headers,
                    json={
                        'parent': {'database_id': self.database_id},
                        'properties': properties
                    }
                )

                if response.status_code != 200:
                    logger.error(f"Failed to sync request {req.id}: {response.text}")

            return True

        except Exception as e:
            logger.error(f"Error syncing to Notion: {str(e)}")
            return False

    def sync_from_notion(self):
        """Fetch updates from Notion database"""
        if not self.is_configured():
            logger.warning("Notion not configured. Skipping sync.")
            return []

        try:
            response = requests.post(
                f'{self.BASE_URL}/databases/{self.database_id}/query',
                headers=self.headers,
                json={}
            )

            if response.status_code == 200:
                return response.json().get('results', [])
            else:
                logger.error(f"Failed to query Notion: {response.text}")
                return []

        except Exception as e:
            logger.error(f"Error syncing from Notion: {str(e)}")
            return []


def create_notion_database_template():
    """
    Generate instructions for creating Notion database template
    with correct properties
    """
    return {
        'database_name': 'Community Help System - Requests',
        'properties': {
            'Title': {'type': 'title'},
            'Status': {
                'type': 'select',
                'options': ['🟢 Otvorená', '🟡 V preverovaní', '🟠 V riešení', '✅ Vyriešená', '❌ Zamietnutá']
            },
            'Priority': {
                'type': 'select',
                'options': ['🔵 Nízka', '🟡 Stredná', '🔴 Vysoká', '🔴🔴 Kritická']
            },
            'Category': {
                'type': 'select',
                'options': ['🔍 Hiring', '💰 Investment', '📊 Consulting', '📢 Marketing', '🎤 Speaking', '🤝 Networking']
            },
            'Requester': {'type': 'rich_text'},
            'Email': {'type': 'email'},
            'Value': {'type': 'number'},
            'Description': {'type': 'rich_text'},
            'Assigned Experts': {'type': 'relation'},
        }
    }
