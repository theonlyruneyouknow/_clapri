# File: content_management/management/commands/create_test_content.py
# Location: C:\git\_clapri\content_management\management\commands\create_test_content.py

from django.core.management.base import BaseCommand
from content_management.models import PageContent, Theme
from datetime import datetime, timedelta
from bson import ObjectId

class Command(BaseCommand):
    help = 'Creates test content for development'

    def handle(self, *args, **options):
        # Create default theme
        try:
            # Clear existing themes and content for testing
            Theme.objects.delete()
            PageContent.objects.delete()
            
            # Create new theme
            theme = Theme(
                name='Default Theme',
                description='Default theme for testing'
            ).save()
            
            self.stdout.write(self.style.SUCCESS(f'Created theme: {theme.name} (ID: {theme.id})'))

            # Create content for each page type
            page_types = ['home', 'about', 'services']
            for page_type in page_types:
                content = PageContent(
                    title=f'Test {page_type.title()} Content',
                    content=f'''
                        <div class="container">
                            <div class="card">
                                <div class="card-body text-center">
                                    <div class="display-4 text-primary mb-3">
                                        <i class="bi bi-house"></i>
                                    </div>
                                    <h3>Test {page_type.title()} Page</h3>
                                    <p class="text-muted mb-4">Sample content for demonstration:</p>
                                    <ul class="list-unstyled">
                                        <li class="mb-2">
                                            <i class="bi bi-check2 text-success"></i> Sample Feature 1
                                        </li>
                                        <li class="mb-2">
                                            <i class="bi bi-check2 text-success"></i> Sample Feature 2
                                        </li>
                                        <li class="mb-2">
                                            <i class="bi bi-check2 text-success"></i> Sample Feature 3
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    ''',
                    page_type=page_type,
                    active=True,
                    display_from=datetime.now(),
                    display_until=datetime.now() + timedelta(days=30)
                )
                content.theme = theme
                content.save()
                
                self.stdout.write(self.style.SUCCESS(
                    f'Created {page_type} content with ID: {content.id}'
                ))

            # Verify content
            total_content = PageContent.objects.count()
            self.stdout.write(f'\nTotal content items created: {total_content}')
            
            for content in PageContent.objects:
                self.stdout.write(
                    f'- {content.page_type}: {content.title} '
                    f'(Active: {content.active}, Theme: {content.theme.name})'
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise e