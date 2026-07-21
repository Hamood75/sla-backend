from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from accounts.models import Department
from cms.models import (
    AboutSection,
    AnnouncementBar,
    BrandValue,
    DonateModalCopy,
    DonationTier,
    Event,
    GallerySection,
    HeroProgressBar,
    HeroSection,
    HeroTag,
    ImpactStat,
    NavItem,
    OrgChartNode,
    PaymentMethod,
    Product,
    Program,
    Project,
    SiteSettings,
    SocialLink,
    TeamMember,
)
from profiles.models import EmployeeProfile, ProfileSocialLink
from qr.models import QRCode, QRCodeLink

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed CMS content, demo profiles, and Smart QR examples'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Street Labs Africa platform...')

        settings = SiteSettings.load()
        settings.org_name = 'Street Digital Labs Africa'
        settings.tagline = 'Inclusion for All!'
        settings.address = 'Morogoro, Tanzania'
        settings.phone = '+255 800 123 456'
        settings.email = 'info@streetlabsafrica.org'
        settings.save()

        DonateModalCopy.load()

        if not AnnouncementBar.objects.exists():
            AnnouncementBar.objects.create(
                message='Help us empower 10,000 more youth this year —',
                cta_label='Donate Now →',
            )

        nav_items = [
            ('Home', '#home', 1),
            ('About', '#about', 2),
            ('Programs', '#services', 3),
            ('Values', '#values', 4),
            ('Team', '#team', 5),
            ('Contact', '#contact', 6),
        ]
        if not NavItem.objects.exists():
            for label, href, order in nav_items:
                NavItem.objects.create(label=label, href=href, order=order)

        hero, _ = HeroSection.objects.get_or_create(
            pk=1,
            defaults={
                'title_line_1': 'Empowering Africa',
                'title_accent': 'One Skill at a Time.',
                'description': (
                    'Street Digital Labs Africa is a digital skills and innovation hub '
                    'building inclusive futures across the continent.'
                ),
            },
        )
        if not hero.tags.exists():
            for i, label in enumerate(['Inclusion', 'Innovation', 'Empowerment', 'Community'], start=1):
                HeroTag.objects.create(hero=hero, label=label, order=i)
        if not hero.progress_bars.exists():
            HeroProgressBar.objects.create(
                hero=hero, label='Youth Trained', display_value='10,000+', percent=78, color_variant='orange', order=1,
            )
            HeroProgressBar.objects.create(
                hero=hero, label='States Reached', display_value='36 / 36', percent=100, color_variant='green', order=2,
            )

        stats = [
            ('10K+', 'Youth Trained', 'hero', 1),
            ('36', 'States Reached', 'hero', 2),
            ('98%', 'Success Rate', 'hero', 3),
            ('50+', 'Expert Trainers', 'hero', 4),
            ('10K+', 'Youth Trained', 'about', 1),
            ('36', 'States Reached', 'about', 2),
            ('98%', 'Success Rate', 'about', 3),
            ('50+', 'Expert Trainers', 'about', 4),
            ('10K+', 'Youth Empowered', 'gallery', 1),
            ('36', 'States Covered', 'gallery', 2),
            ('98%', 'Success Rate', 'gallery', 3),
            ('50+', 'Programs Run', 'gallery', 4),
        ]
        if not ImpactStat.objects.exists():
            for value, label, placement, order in stats:
                ImpactStat.objects.create(value=value, label=label, placement=placement, order=order)

        GallerySection.objects.get_or_create(
            pk=1,
            defaults={
                'eyebrow': 'Our Community In Action',
                'title': 'Hands On at SLA',
                'description': 'Workshops, labs, and mentorship moments from across Street Labs Africa.',
            },
        )

        AboutSection.objects.get_or_create(
            pk=1,
            defaults={
                'description': (
                    'Street Digital Labs Africa empowers communities with digital skills, '
                    'innovation pathways, and inclusive technology education.'
                ),
                'mission_text': 'Empower Africans with digital skills, innovation, and opportunity.',
                'vision_text': 'An inclusive Africa where every community thrives through technology.',
            },
        )

        values = [
            ('🤲', 'Inclusion', 'Everyone belongs in the digital future.', '#ff6a00'),
            ('💡', 'Innovation', 'We build practical solutions for real communities.', '#0a7a3d'),
            ('🎓', 'Empowerment', 'Skills that unlock independence and leadership.', '#ff6a00'),
            ('🤝', 'Integrity', 'Transparent partnerships and accountable impact.', '#0a7a3d'),
            ('🌐', 'Community', 'Growth that lifts neighborhoods and nations.', '#ff6a00'),
        ]
        if not BrandValue.objects.exists():
            for i, (emoji, title, desc, color) in enumerate(values, start=1):
                BrandValue.objects.create(emoji=emoji, title=title, description=desc, color=color, order=i)

        programs = [
            ('💻', 'Digital Skills Training', 'Hands-on digital literacy and career-ready skills.', 'Flagship', '#ff6a00'),
            ('🚀', 'Innovation Lab', 'Prototyping spaces for youth-led solutions.', 'Innovation', '#0a7a3d'),
            ('🎓', 'Mentorship & Coaching', 'Guided growth with industry mentors.', 'Empowerment', '#ff6a00'),
            ('🤝', 'Community Outreach', 'Bringing training to underserved communities.', 'Inclusion', '#0a7a3d'),
        ]
        if not Program.objects.exists():
            for i, (emoji, title, desc, tag, color) in enumerate(programs, start=1):
                Program.objects.create(
                    emoji=emoji, title=title, description=desc, tag=tag, tag_color=color, order=i, is_featured=True,
                )

        if not OrgChartNode.objects.exists():
            root = OrgChartNode.objects.create(title='Africa Think Tank Commission', level=1, order=1, icon='🌍')
            ceo = OrgChartNode.objects.create(title='Chief Executive Officer', subtitle='(CEO)', parent=root, level=2, order=1, icon='👤')
            coo = OrgChartNode.objects.create(title='Chief Operating Officer', subtitle='(COO)', parent=ceo, level=3, order=1, icon='⚙️')
            for i, title in enumerate([
                'Director of Operations',
                'Director of Corporate Events',
                'Director of Innovation',
                'Chief Financial Officer',
                'Chief Technology Officer',
                'Director of Creative',
            ], start=1):
                OrgChartNode.objects.create(title=title, parent=coo, level=4, order=i)

        team = [
            ('Anna Joseph Msulla', 'COO', 'AM'),
            ('Abud Hamidu Abdu', 'Director of Operations', 'AA'),
            ('Vicent Johanes Mirumbe', 'Director of Corporate Events', 'VM'),
            ('Mahmoud Mohamed Mahmoud', 'Director of Innovation', 'MM'),
            ('Gervass Orgeness Urassa', 'Chief Financial Officer', 'GU'),
            ('Jenadius Nicholaus Kaimkilwa', 'Chief Technology Officer', 'JK'),
        ]
        if not TeamMember.objects.exists():
            for i, (name, role, initials) in enumerate(team, start=1):
                TeamMember.objects.create(name=name, role=role, initials=initials, order=i)

        if not SocialLink.objects.exists():
            for i, (platform, icon) in enumerate([
                ('facebook', 'f'), ('twitter', '𝕏'), ('linkedin', 'in'), ('youtube', '▶'),
            ], start=1):
                SocialLink.objects.create(
                    platform=platform,
                    url=f'https://streetlabsafrica.org/#{platform}',
                    icon_label=icon,
                    order=i,
                )

        if not DonationTier.objects.exists():
            tiers = [
                (10, '$10', 'Funds 1 day of digital training'),
                (25, '$25', 'Supports a learner toolkit'),
                (50, '$50', 'Sponsors a workshop seat'),
                (100, '$100', 'Funds a week of mentorship'),
                (250, '$250', 'Equips a mini lab station'),
                (500, '$500', 'Powers a community outreach day'),
            ]
            for i, (amount, label, impact) in enumerate(tiers, start=1):
                DonationTier.objects.create(amount=amount, label=label, impact=impact, order=i)

        if not PaymentMethod.objects.exists():
            methods = [
                ('selcom', 'Selcom', True, 1),
                ('mpesa', 'M-Pesa', True, 2),
                ('airtel', 'Airtel Money', True, 3),
                ('card', 'Card', False, 4),
            ]
            for code, name, phone, order in methods:
                PaymentMethod.objects.create(code=code, name=name, requires_phone=phone, order=order)

        innovation, _ = Department.objects.get_or_create(
            slug='innovation',
            defaults={'name': 'Innovation', 'description': 'Labs, R&D, and product experiments'},
        )
        Department.objects.get_or_create(slug='operations', defaults={'name': 'Operations'})
        Department.objects.get_or_create(slug='technology', defaults={'name': 'Technology'})

        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@streetlabsafrica.org',
                'first_name': 'Platform',
                'last_name': 'Admin',
                'role': User.Role.SUPER_ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'job_title': 'Platform Administrator',
                'department': innovation,
            },
        )
        if created:
            admin_user.set_password('admin123!')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin / admin123!'))

        hamood, created = User.objects.get_or_create(
            username='hamood',
            defaults={
                'email': 'hamood@streetlabsafrica.org',
                'first_name': 'Mahmoud',
                'last_name': 'Mahmoud',
                'role': User.Role.EMPLOYEE,
                'job_title': 'Director of Innovation',
                'department': innovation,
                'phone': '+255700000001',
            },
        )
        if created:
            hamood.set_password('hamood123!')
            hamood.save()

        profile, _ = EmployeeProfile.objects.get_or_create(
            user=hamood,
            defaults={
                'username': 'hamood',
                'display_name': 'Mahmoud Mohamed Mahmoud',
                'position': 'Director of Innovation',
                'bio': 'Building innovation pathways and digital products across Street Labs Africa.',
                'email': 'hamood@streetlabsafrica.org',
                'phone': '+255700000001',
                'website': 'https://streetlabsafrica.org',
                'location': 'Morogoro, Tanzania',
                'department': innovation,
            },
        )
        if not profile.social_links.exists():
            ProfileSocialLink.objects.create(
                profile=profile, platform='linkedin', label='LinkedIn',
                url='https://linkedin.com', order=1,
            )
            ProfileSocialLink.objects.create(
                profile=profile, platform='email', label='Email',
                url='mailto:hamood@streetlabsafrica.org', order=2,
            )

        project, _ = Project.objects.get_or_create(
            slug='ai-lab',
            defaults={
                'title': 'AI Lab',
                'summary': 'Applied AI research and youth innovation studio.',
                'description': 'A Street Labs Africa project exploring practical AI for African communities.',
            },
        )
        Event.objects.get_or_create(
            slug='digital-skills-summit',
            defaults={
                'title': 'Digital Skills Summit',
                'summary': 'Annual gathering of trainers, partners, and youth leaders.',
                'location': 'Morogoro, Tanzania',
            },
        )
        Product.objects.get_or_create(
            slug='smart-qr-platform',
            defaults={
                'title': 'Smart QR Platform',
                'summary': 'Company-wide digital identity and dynamic QR hub.',
            },
        )

        if not QRCode.objects.filter(title='Hamood Smart Hub').exists():
            qr = QRCode.objects.create(
                owner=hamood,
                title='Hamood Smart Hub',
                description='Director of Innovation — Street Labs Africa',
                destination_type=QRCode.DestinationType.HUB,
                code='A91KXT',
                slug='a91kxt',
            )
            links = [
                ('Website', 'website', 'https://streetlabsafrica.org'),
                ('Employee Profile', 'profile', f'{settings.website_url}/profiles/hamood'),
                ('LinkedIn', 'linkedin', 'https://linkedin.com'),
                ('Email', 'email', 'mailto:hamood@streetlabsafrica.org'),
                ('WhatsApp', 'whatsapp', 'https://wa.me/255700000001'),
                ('Book Meeting', 'meeting', 'https://calendly.com/'),
                ('Download Contact', 'contact', f'{settings.website_url}/api/profiles/hamood/vcard/'),
            ]
            for i, (label, icon, url) in enumerate(links, start=1):
                QRCodeLink.objects.create(qr=qr, label=label, icon=icon, url=url, order=i)

        if not QRCode.objects.filter(code='C28LMN').exists():
            QRCode.objects.create(
                owner=admin_user,
                title='AI Lab',
                destination_type=QRCode.DestinationType.PROJECT,
                destination_url=f'{settings.website_url}/projects/ai-lab',
                code='C28LMN',
                slug='c28lmn',
            )

        self.stdout.write(self.style.SUCCESS('Seed complete.'))
        self.stdout.write('Login: admin / admin123!  |  Employee: hamood / hamood123!')
        self.stdout.write('Demo QR: /qr/A91KXT')
