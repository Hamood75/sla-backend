import io
import uuid

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image

from events.models import (
    BoothApplication,
    EventStat,
    ExpoEvent,
    ExpoVillage,
    FocusArea,
    MediaAsset,
    Partner,
    Registration,
    Session,
    Speaker,
    VillageBooth,
    VillageGallery,
    VillageSchedule,
)


def make_image_file(width, height, color):
    """Generate a PNG image and return a ContentFile ready for ImageField."""
    img = Image.new('RGB', (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    name = f'seed_{uuid.uuid4().hex[:8]}.png'
    return ContentFile(buf.getvalue(), name=name)


class Command(BaseCommand):
    help = 'Seed expo event data with generated placeholder images'

    def handle(self, *args, **options):
        self.stdout.write('Seeding expo events data...')

        if ExpoEvent.objects.filter(year=2026).exists():
            self.stdout.write(self.style.WARNING('Events data already exists. Skipping.'))
            return

        # --- Event ---
        event = ExpoEvent.objects.create(
            year=2026,
            title='Tanzania DPI Expo 2026',
            tagline='Building Digital Foundation',
            description=(
                'The Tanzania DPI Expo 2026 brings together government agencies, '
                'private sector leaders, and innovators to showcase and advance '
                'Digital Public Infrastructure across East Africa.'
            ),
            start_date='2026-11-18T11:00:00+03:00',
            end_date='2026-11-19T21:00:00+03:00',
            venue_name='Diamond Jubilee Hall',
            venue_address='Ohio Street, Dar es Salaam',
            venue_lat=-6.8161,
            venue_lng=39.2804,
            hero_images=[default_storage.save(f'events/heroes/seed_{uuid.uuid4().hex[:8]}.png', make_image_file(1920, 600, '#1E40AF'))],
            is_active=True,
            is_published=True,
        )
        self.stdout.write(f'  Created event: {event.title}')

        # --- Event Stats ---
        stats_data = [
            ('Speakers', '50+', 1),
            ('Exhibitors', '120+', 2),
            ('Villages', '6', 3),
            ('Attendees', '5000+', 4),
        ]
        for label, value, order in stats_data:
            EventStat.objects.create(event=event, label=label, value=value, order=order)
        self.stdout.write(f'  Created {len(stats_data)} event stats')

        # --- Focus Areas ---
        focus_areas_data = [
            ('01', 'Keynotes', 'Inspiring talks from global DPI leaders', '#F97316', '#EA580C'),
            ('02', 'Workshops', 'Hands-on sessions for practical skills', '#2563EB', '#1D4ED8'),
            ('03', 'Exhibitions', 'Live demos of digital platforms', '#059669', '#047857'),
            ('04', 'Networking', 'Connect with industry peers', '#7C3AED', '#6D28D9'),
        ]
        for num, title, desc, accent, badge in focus_areas_data:
            fa = FocusArea(
                event=event, num=num, title=title, description=desc,
                accent_color=accent, badge_color=badge,
                order=int(num),
            )
            fa.image.save(f'focus_{num}.png', make_image_file(800, 600, accent), save=False)
            fa.save()
        self.stdout.write(f'  Created {len(focus_areas_data)} focus areas')

        # --- Partners ---
        partners_data = [
            ('iDEA', 'HOST', '#1E40AF'),
            ('Tanzania ICT Authority', 'LEAD_PARTNER', '#059669'),
            ('GSMA', 'PARTNER', '#7C3AED'),
            ('World Bank', 'PARTNER', '#F97316'),
            ('Smart Africa', 'MEDIA', '#DC2626'),
        ]
        for name, tier, color in partners_data:
            p = Partner(
                event=event, name=name, tier=tier,
                website_url=f'https://example.com/{name.lower().replace(" ", "-")}',
                order=partners_data.index((name, tier, color)) + 1,
            )
            p.logo.save(f'{name.lower().replace(" ", "_")}.png', make_image_file(400, 200, color), save=False)
            p.save()
        self.stdout.write(f'  Created {len(partners_data)} partners')

        # --- Villages ---
        villages_data = [
            ('govtech', 'GovTech Village', 'Hall A', '🏛️', '#2563EB',
             'Transforming Public Services',
             'Live demos of e-Government platforms, digital identity, and citizen service portals.'),
            ('fintech', 'FinTech Village', 'Hall B', '💳', '#059669',
             'Digital Payments for All',
             'Mobile money, instant payments, and financial inclusion innovations.'),
            ('agritech', 'AgriTech Village', 'Hall C', '🌾', '#F97316',
             'Smart Agriculture',
             'IoT sensors, drone mapping, and data-driven farming solutions.'),
            ('healthtech', 'HealthTech Village', 'Hall D', '🏥', '#DC2626',
             'Digital Health',
             'Telemedicine, health records, and AI diagnostics platforms.'),
            ('edtech', 'EdTech Village', 'Hall E', '📚', '#7C3AED',
             'Learning Reimagined',
             'E-learning platforms, digital classrooms, and skills development tools.'),
            ('startup', 'Startup Village', 'Hall F', '🚀', '#0891B2',
             'Innovation Showcase',
             'Early-stage startups presenting DPI solutions and prototypes.'),
        ]

        villages = {}
        for i, (slug, name, hall, emoji, color, tagline, desc) in enumerate(villages_data, start=1):
            village = ExpoVillage(
                event=event, slug=slug, name=name, hall=hall, emoji=emoji,
                theme_color=color, tagline=tagline, description=desc,
                stats=[{'label': 'Booths', 'value': f'{10+i}'}, {'label': 'Demos', 'value': f'{5+i}'}],
                order=i,
            )
            village.hero_image.save(f'{slug}.png', make_image_file(1200, 400, color), save=False)
            village.save()
            villages[slug] = village
        self.stdout.write(f'  Created {len(villages_data)} villages')

        # --- Village Booths ---
        booths_data = {
            'govtech': [
                ('GovNet & e-GA Gateway', 'e-Government Authority', 'A-01', 'Infrastructure', True),
                ('Tanzania e-ID System', 'NIDA', 'A-02', 'Identity', False),
                ('Citizen Service Portal', 'e-GA', 'A-03', 'Services', False),
            ],
            'fintech': [
                ('M-Pesa API Hub', 'Vodacom', 'B-01', 'Payments', True),
                ('Selcom Payment Gateway', 'Selcom', 'B-02', 'Payments', False),
                ('Akiba Digital Wallet', 'Akiba Bank', 'B-03', 'Wallet', False),
            ],
            'agritech': [
                ('Drone Crop Mapping', 'AgriDrone TZ', 'C-01', 'Drones', True),
                ('Soil Sensor IoT', 'FarmTech', 'C-02', 'IoT', False),
            ],
        }
        booth_count = 0
        for slug, booths in booths_data.items():
            for j, (name, org, btno, tag, featured) in enumerate(booths, start=1):
                booth = VillageBooth(
                    village=villages[slug], name=name, org=org, booth_number=btno,
                    tag=tag, description=f'{name} by {org}.',
                    live_demo=f'{10+j}:00 AM — Live Demo' if featured else '',
                    website_url=f'https://example.com/{slug}/{j}',
                    is_featured=featured, order=j,
                )
                booth.logo.save(f'{slug}_booth_{j}.png', make_image_file(300, 150, villages[slug].theme_color), save=False)
                booth.save()
                booth_count += 1
        self.stdout.write(f'  Created {booth_count} village booths')

        # --- Village Schedules ---
        schedules_data = {
            'govtech': [
                ('09:30 AM', 'Open-Source Public Digital Stack', 'Eng. Baraka Mtalo', 'Stage A', 1),
                ('11:00 AM', 'e-Government Interoperability', 'Dr. Aisha Mwakyusa', 'Stage A', 1),
                ('02:00 PM', 'Digital Identity for Citizens', 'NIDA Team', 'Booth A-02', 1),
            ],
            'fintech': [
                ('10:00 AM', 'Instant Payments Ecosystem', 'Joseph Mmbando', 'Stage B', 1),
                ('01:30 PM', 'Financial Inclusion via Mobile', 'Sarah Komba', 'Stage B', 1),
            ],
        }
        sched_count = 0
        for slug, scheds in schedules_data.items():
            for j, (time, title, presenter, stage, day) in enumerate(scheds, start=1):
                VillageSchedule.objects.create(
                    village=villages[slug], time=time, title=title,
                    presenter=presenter, booth_or_stage=stage,
                    day_number=day, order=j,
                )
                sched_count += 1
        self.stdout.write(f'  Created {sched_count} village schedules')

        # --- Village Galleries ---
        gallery_data = {
            'govtech': [
                ('Citizen Portal Launch', 'One-stop government services', 2026),
                ('e-ID Registration Drive', 'National digital identity rollout', 2026),
            ],
            'fintech': [
                ('Mobile Money Summit', 'Cross-border payment innovations', 2026),
            ],
        }
        gallery_count = 0
        for slug, galleries in gallery_data.items():
            for j, (title, caption, year) in enumerate(galleries, start=1):
                vg = VillageGallery(
                    village=villages[slug],
                    title=title, caption=caption,
                    edition_year=year, order=j,
                )
                vg.image.save(f'{slug}_gallery_{j}.png', make_image_file(800, 600, villages[slug].theme_color), save=False)
                vg.save()
                gallery_count += 1
        self.stdout.write(f'  Created {gallery_count} village gallery items')

        # --- Speakers ---
        speakers_data = [
            ('Dr. Fatma Hassan', 'Minister of ICT', 'Government of Tanzania', 'FH', '#1E40AF', '#DBEAFE'),
            ('Eng. Baraka Mtalo', 'CTO', 'e-Government Authority', 'BM', '#059669', '#D1FAE5'),
            ('Sarah Komba', 'Director of Fintech', 'Bank of Tanzania', 'SK', '#F97316', '#FED7AA'),
            ('Joseph Mmbando', 'Head of Innovation', 'Vodacom Tanzania', 'JM', '#7C3AED', '#EDE9FE'),
            ('Dr. Aisha Mwakyusa', 'Senior Advisor', 'World Bank Tanzania', 'AM', '#DC2626', '#FEE2E2'),
        ]
        speakers = []
        for i, (name, title, org, initials, color, accent) in enumerate(speakers_data, start=1):
            speaker = Speaker(
                event=event, name=name, title=title, org=org,
                initials=initials, color=color, accent_light=accent,
                bio=f'{name} is a leading expert in digital infrastructure.',
                order=i, is_confirmed=True,
            )
            speaker.photo.save(f'{initials}.png', make_image_file(400, 400, color), save=False)
            speaker.save()
            speakers.append(speaker)
        self.stdout.write(f'  Created {len(speakers_data)} speakers')

        # --- Sessions ---
        sessions_data = [
            (1, '09:00', '10:00', 'Opening Keynote: DPI for Africa', 'KEYNOTE', 0, 'Main Hall'),
            (1, '10:00', '10:15', 'Coffee Break', 'BREAK', None, 'Foyer'),
            (1, '10:15', '11:30', 'Digital Identity Panel', 'PANEL', 0, 'Main Hall'),
            (1, '11:30', '12:30', 'Mobile Money Workshop', 'WORKSHOP', 1, 'Workshop Room 1'),
            (1, '12:30', '13:30', 'Lunch Break', 'BREAK', None, 'Dining Area'),
            (1, '13:30', '15:00', 'Exhibition Tour', 'EXHIBITION', None, 'Exhibition Hall'),
            (1, '15:00', '16:00', 'AI for Public Services', 'WORKSHOP', 3, 'Workshop Room 2'),
            (2, '09:00', '10:00', 'Day 2 Keynote: Future of DPI', 'KEYNOTE', 4, 'Main Hall'),
            (2, '10:00', '11:30', 'Cross-Border Payments Panel', 'PANEL', 2, 'Main Hall'),
            (2, '11:30', '12:30', 'AgriTech Innovations Workshop', 'WORKSHOP', None, 'Workshop Room 1'),
        ]
        for i, (day, start, end, title, stype, speaker_idx, location) in enumerate(sessions_data, start=1):
            speaker = speakers[speaker_idx] if speaker_idx is not None and speaker_idx < len(speakers) else None
            Session.objects.create(
                event=event, day_number=day, start_time=start, end_time=end,
                title=title, type=stype, speaker=speaker,
                speaker_text='' if speaker else 'Various Speakers',
                location=location, order=i,
            )
        self.stdout.write(f'  Created {len(sessions_data)} sessions')

        # --- Booth Applications ---
        booth_apps_data = [
            (villages['govtech'], 'TechCo Tanzania', 'Fintech', 'STANDARD', 'AI Demo Platform',
             'AI-powered government service automation', ['Projector', 'WiFi'], 'PENDING_REVIEW'),
            (villages['fintech'], 'PaySmart Ltd', 'Payments', 'PREMIUM', 'Instant Payment Hub',
             'Real-time cross-border payment solution', ['Large Screen', 'Power'], 'APPROVED'),
            (villages['agritech'], 'AgriTech Solutions', 'Agriculture', 'STANDARD', 'Drone Crop Scanner',
             'Drone-based crop health monitoring', ['Outdoor Space'], 'ALLOCATED'),
        ]
        for i, (village, company, sector, pkg, showcase_title, showcase_desc, tech_reqs, status) in enumerate(booth_apps_data, start=1):
            BoothApplication.objects.create(
                event=event, village=village,
                company_name=company, company_website=f'https://example.com/{company.lower().replace(" ", "")}',
                company_sector=sector, booth_package=pkg,
                showcase_title=showcase_title, showcase_desc=showcase_desc,
                tech_requirements=tech_reqs, co_exhibitors='',
                first_name='Alice', last_name='Kimaro',
                email=f'alice{i}@{company.lower().replace(" ", "")}.com',
                phone=f'+2557000001{i:02d}', job_title='Head of Partnerships',
                country='Tanzania', status=status,
                assigned_booth_no=f'{village.hall[-1]}-{i:02d}' if status == 'ALLOCATED' else '',
            )
        self.stdout.write(f'  Created {len(booth_apps_data)} booth applications')

        # --- Registrations ---
        registrations_data = [
            ('GUEST', 'John', 'Doe', 'john.doe@example.com', 'Tanzania', 'Tech Corp', 'CONFIRMED'),
            ('GUEST', 'Jane', 'Smith', 'jane.smith@example.com', 'Kenya', 'Innovation Hub', 'CONFIRMED'),
            ('SPEAKER', 'Dr. Fatma', 'Hassan', 'fatma.hassan@gov.go.tz', 'Tanzania', 'Government', 'CONFIRMED'),
            ('VOLUNTEER', 'Michael', 'Mushi', 'michael.mushi@volunteer.org', 'Tanzania', '', 'PENDING_REVIEW'),
            ('GUEST', 'Amina', 'Said', 'amina.said@example.com', 'Zanzibar', 'ZANTEL', 'APPROVED'),
        ]
        for i, (rtype, fname, lname, email, country, org, status) in enumerate(registrations_data, start=1):
            extra = {}
            if rtype == 'GUEST':
                extra = {'guest_category': 'General', 'dietary_reqs': ''}
            elif rtype == 'SPEAKER':
                extra = {'linked_in': '', 'talk_title': '', 'speaker_bio': '', 'talk_abstract': '', 'previous_speaking': ''}
            elif rtype == 'VOLUNTEER':
                extra = {'role': 'Guide', 'availability': 'Both days'}

            Registration.objects.create(
                event=event, type=rtype,
                first_name=fname, last_name=lname,
                email=email, phone=f'+255700000{i:03d}',
                country=country, organization=org,
                extra_data=extra, status=status,
            )
        self.stdout.write(f'  Created {len(registrations_data)} registrations')

        # --- Media Assets ---
        media_data = [
            ('heroes', 'Hero Banner', '#1E40AF', 1920, 600),
            ('speakers', 'Speaker Photo', '#059669', 400, 400),
            ('villages', 'Village Hero', '#F97316', 1200, 400),
            ('gallery', 'Gallery Photo', '#7C3AED', 800, 600),
            ('logos', 'Partner Logo', '#DC2626', 400, 200),
        ]
        for folder, alt, color, w, h in media_data:
            img_file = make_image_file(w, h, color)
            asset = MediaAsset(
                event=event,
                original_name=img_file.name,
                file_name=img_file.name,
                mime_type='image/png',
                size_bytes=img_file.size,
                folder=folder,
                alt_text=alt,
                width=w,
                height=h,
            )
            asset.file.save(img_file.name, img_file, save=False)
            asset.save()
        self.stdout.write(f'  Created {len(media_data)} media assets')

        self.stdout.write(self.style.SUCCESS('Events seed complete!'))
        self.stdout.write('Event year: 2026 | Admin: admin / pass123')
