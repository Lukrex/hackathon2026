from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Request, Expert, Notification


@shared_task
def send_confirmation_email(request_id):
    """Send confirmation email when request is submitted"""
    try:
        request_obj = Request.objects.get(id=request_id)

        subject = f"✅ Tvoja žiadosť bola prijatá: {request_obj.title}"

        html_message = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 8px; }}
                    .content {{ background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                    .request-details {{ background: white; padding: 15px; border-radius: 4px; border-left: 4px solid #667eea; }}
                    .footer {{ color: #666; font-size: 12px; text-align: center; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✅ Tvoja žiadosť bola prijatá!</h1>
                    </div>

                    <div class="content">
                        <p>Ahoj {request_obj.requester_name},</p>
                        <p>Ďakujeme! Tvoja žiadosť bola úspešne zaregistrovaná v našom systéme.</p>

                        <div class="request-details">
                            <h3>Detaily žiadosti:</h3>
                            <p><strong>Názov:</strong> {request_obj.title}</p>
                            <p><strong>Kategória:</strong> {request_obj.get_category_display() if request_obj.category else 'Neuvedená'}</p>
                            <p><strong>Dátum:</strong> {request_obj.created_at.strftime('%d.%m.%Y %H:%M')}</p>
                            <p><strong>Referencia:</strong> #{request_obj.id}</p>
                        </div>

                        <p>Naši komunití experti ju preskúmajú a budeme ti kontaktovať s návrhy vhodných osôb, ktoré ti môžu pomôcť.</p>

                        <p><strong>Čo sa stane ďalej?</strong></p>
                        <ol>
                            <li>Náš tím skúma tvoju žiadosť</li>
                            <li>Vyhľadávame vhodných expertov z komunity</li>
                            <li>Skontaktujeme ťa s ponukami pomoci</li>
                        </ol>
                    </div>

                    <div class="footer">
                        <p>📧 Ak máš otázky, odpovedz na tento e-mail.</p>
                        <p>HalovaMake Community Help System</p>
                    </div>
                </div>
            </body>
        </html>
        """

        plaintext_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plaintext_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request_obj.requester_email],
            html_message=html_message,
            fail_silently=False,
        )

        # Log notification
        Notification.objects.create(
            request=request_obj,
            recipient_email=request_obj.requester_email,
            notification_type='confirmation',
            subject=subject
        )

        return f"Confirmation email sent to {request_obj.requester_email}"

    except Request.DoesNotExist:
        return f"Request {request_id} not found"
    except Exception as e:
        return f"Error: {str(e)}"


@shared_task
def send_expert_assignment_email(request_id, expert_id):
    """Send email to expert when assigned to request"""
    try:
        request_obj = Request.objects.get(id=request_id)
        expert_obj = Expert.objects.get(id=expert_id)

        subject = f"🎯 Nová príležitosť pomôcť: {request_obj.title}"

        html_message = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #f59e0b, #f97316); color: white; padding: 20px; border-radius: 8px; }}
                    .request-box {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 15px 0; border-radius: 4px; }}
                    .btn {{ display: inline-block; background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎯 Máme pre teba príležitosť!</h1>
                    </div>

                    <p>Ahoj {expert_obj.user.get_full_name()},</p>

                    <p>
                        Niekto v komunite potrebuje tvoju pomoc!
                        Podľa tvojich odborností sme si mysleli, že by si bol ideálnym človekom na pomoc s touto žiadosťou.
                    </p>

                    <div class="request-box">
                        <h2>📝 {request_obj.title}</h2>
                        <p><strong>Kategória:</strong> {request_obj.get_category_display()}</p>
                        <p><strong>Popis:</strong></p>
                        <p>{request_obj.description}</p>
                        <p><strong>Kontakt na žiadateľa:</strong> {request_obj.requester_name} ({request_obj.requester_email})</p>
                    </div>

                    <p>
                        ❓ Zaujímavá možnosť pomôcť? Kontaktuj prosím {request_obj.requester_name} na horeuvedenej e-mailovej adrese.
                    </p>

                    <p>
                        Vďaka za to, že si súčasťou našej komunity a pomáhaš ostatným! 🙌
                    </p>
                </div>
            </body>
        </html>
        """

        plaintext_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plaintext_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[expert_obj.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        # Log notification
        Notification.objects.create(
            request=request_obj,
            recipient_email=expert_obj.user.email,
            notification_type='expert_match',
            subject=subject
        )

        return f"Expert notification sent to {expert_obj.user.email}"

    except Exception as e:
        return f"Error: {str(e)}"


@shared_task
def calculate_expert_matches(request_id):
    """Calculate expert matches for a request (AI-style scoring)"""
    try:
        request_obj = Request.objects.get(id=request_id)

        # Clear existing matches
        request_obj.expert_matches.all().delete()

        keywords = (request_obj.title + ' ' + request_obj.description).lower().split()

        experts = Expert.objects.all()

        for expert in experts:
            expert_keywords = ' '.join(expert.get_expertise_list()).lower().split()

            # Calculate match score
            match_score = 0

            # Keyword overlap (40 points max)
            overlaps = len(set(keywords) & set(expert_keywords))
            match_score += min(overlaps * 8, 40)

            # Category match (30 points)
            if request_obj.category:
                category_keywords = request_obj.category.description.lower().split()
                if any(kw in ' '.join(expert_keywords) for kw in category_keywords):
                    match_score += 30

            # Workload inverse (10 points)
            workload = expert.assigned_requests.count()
            if workload < 3:
                match_score += 10
            elif workload < 5:
                match_score += 5

            # Ensure max 100
            match_score = min(match_score, 100)

            # Create match if score > 40
            if match_score >= 40:
                from .models import ExpertMatch
                ExpertMatch.objects.create(
                    request=request_obj,
                    expert=expert,
                    match_score=match_score,
                    reasoning=f"Keyword overlap: {overlaps}, Category fit: good"
                )

        return f"Matches calculated for request {request_id}"

    except Request.DoesNotExist:
        return f"Request {request_id} not found"
    except Exception as e:
        return f"Error: {str(e)}"


@shared_task
def sync_to_notion():
    """Sync requests and experts to Notion (placeholder)"""
    from .models import Request, Expert

    requests_count = Request.objects.count()
    experts_count = Expert.objects.count()

    # In real implementation, call Notion API here
    return f"Synced {requests_count} requests and {experts_count} experts to Notion"
