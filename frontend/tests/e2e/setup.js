import { execSync } from 'child_process';

export default async function globalSetup() {
  execSync('python manage.py migrate --noinput', { stdio: 'inherit', cwd: '..' });
  execSync(
    "python manage.py shell -c \"from django.contrib.auth import get_user_model; from backend.apps.accounts.models import UserSettings, Country, SearchSource; User = get_user_model(); user, _ = User.objects.update_or_create(email='demo@example.com', defaults={'is_staff': True, 'is_superuser': True, 'phone_number': '+79000000000'}); user.set_password('password'); user.save(); UserSettings.objects.update_or_create(user=user, defaults={'country': Country.RUSSIA, 'default_search_source': SearchSource.ARMTEK})\"",
    {
      stdio: 'inherit',
      cwd: '..',
    },
  );
}
