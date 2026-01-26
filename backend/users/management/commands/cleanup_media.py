import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from users.models import UserFile
from django.conf import settings


class Command(BaseCommand):
    help = 'Clean up old and unused media files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Clean files older than specified days (default: 30)'
        )
        parser.add_argument(
            '--delete-db-records',
            action='store_true',
            help='Also delete database records for cleaned files'
        )

    def handle(self, *args, **options):
        days = options['days']
        delete_db = options['delete_db_records']
        cutoff_date = timezone.now() - timedelta(days=days)

        self.stdout.write(
            self.style.WARNING(f'Looking for files older than {days} days...')
        )

        # Find old UserFile records
        old_files = UserFile.objects.filter(uploaded_at__lt=cutoff_date)

        deleted_count = 0
        size_freed = 0

        for user_file in old_files:
            if user_file.file and os.path.exists(user_file.file.path):
                file_size = os.path.getsize(user_file.file.path)
                try:
                    os.remove(user_file.file.path)
                    size_freed += file_size
                    deleted_count += 1
                    
                    if delete_db:
                        user_file.delete()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Deleted file and DB record: {user_file.original_filename}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Deleted file only: {user_file.original_filename} '
                                f'(size: {file_size} bytes)'
                            )
                        )
                except OSError as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error deleting file {user_file.file.path}: {e}'
                        )
                    )
            else:
                # File doesn't exist on disk but record does - handle based on options
                if delete_db:
                    user_file.delete()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Deleted orphaned DB record: {user_file.original_filename}'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully cleaned up {deleted_count} files, '
                f'reclaiming {size_freed} bytes'
            )
        )