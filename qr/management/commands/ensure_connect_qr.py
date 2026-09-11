"""Create / update the org Connect QR that opens /connect after scan."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from qr.models import QRCode
from qr.services import build_qr_image

User = get_user_model()

CONNECT_CODE = 'SLAORG'


class Command(BaseCommand):
    help = 'Ensure Street Labs Connect QR (code=SLAORG) redirects to /connect'

    def handle(self, *args, **options):
        owner = (
            User.objects.filter(is_superuser=True).order_by('id').first()
            or User.objects.filter(is_staff=True).order_by('id').first()
            or User.objects.order_by('id').first()
        )
        if not owner:
            self.stderr.write(self.style.ERROR('No user found — create a backoffice user first.'))
            return

        base = (getattr(settings, 'PUBLIC_SITE_URL', None) or 'https://streetlabsafrica.org').rstrip('/')
        destination = f'{base}/connect'

        qr, created = QRCode.objects.update_or_create(
            code=CONNECT_CODE,
            defaults={
                'owner': owner,
                'title': 'Street Labs Connect',
                'description': 'Welcome hub — socials, website, and contact.',
                'destination_type': QRCode.DestinationType.CUSTOM,
                'destination_url': destination,
                'slug': 'slaorg',
                'theme': QRCode.Theme.BRAND,
                'primary_color': '#ff6a00',
                'secondary_color': '#0a1f44',
                'is_active': True,
                'show_logo': True,
            },
        )
        # Hub mode wins if any active links exist — keep this QR as redirect-only.
        qr.links.all().delete()

        build_qr_image(qr, fmt='png')

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f'{action} Connect QR {qr.code}\n'
            f'  Scan URL:  {qr.public_url}\n'
            f'  Opens:     {destination}\n'
            f'  Image:     /api/qr/{qr.code}/image/?export=png'
        ))
