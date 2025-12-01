import { execSync } from 'child_process';

export default async function globalSetup() {
  execSync('python manage.py migrate --noinput', { stdio: 'inherit', cwd: '..' });
  execSync(
    "python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.update_or_create(email='demo@example.com', defaults={'username': 'demo', 'is_staff': True})\"",
    {
      stdio: 'inherit',
      cwd: '..',
    },
  );
}
