from django.core.mail import send_mail
from django.contrib.auth.models import User, Group
from fileup.settings import EMAIL_HOST_USER


def email_groups(group_ids,  sender_email, subject, body):
    """
    Send emails to all the members of the group, except the member
    that initiated the email request.             
    """
    emails = []
    for id in group_ids:
        emails += list(User.objects.filter(groups__id=id).values('email'))

    # Only get unique emails
    recipient_set = set()
    for email in emails:
        if (email['email'] != sender_email):
            recipient_set.add(email['email'])

    if (len(recipient_set) != 0):
        send_mail(
            subject,
            body,
            EMAIL_HOST_USER,
            recipient_set,
            fail_silently=True,
        )


def email_users(user_ids,  sender_email, subject, body):
    """
    Send emails to all users of in user_uds, except the user
    that initiated the email request.             
    """
    emails = list(User.objects.filter(id__in=user_ids).values('email'))

    # Convert dict[] to single value list
    recipient_set = set()
    for email in emails:
        if (email['email'] != sender_email):
            recipient_set.add(email['email'])

    if (len(emails) != 0):
        send_mail(
            subject,
            body,
            EMAIL_HOST_USER,
            recipient_set,
            fail_silently=True,
        )
