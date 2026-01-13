from django.core.management.base import BaseCommand
from tasks.models import Task
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Удаляет задачи старше 30 дней со статусом "done"'

    def handle(self, *args, **options):
        threshold = timezone.now() - timedelta(days=30)
        deleted_count, _ = Task.objects.filter(
            status='done',
            updated_at__lt=threshold
        ).delete()

        self.stdout.write(self.style.SUCCESS(
            f'Удалено {deleted_count} старых завершённых задач'
        ))