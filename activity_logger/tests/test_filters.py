from django.utils import timezone
from utils.test import CustomAPITestCase
from activity_logger.models import Log
from activity_logger.filters import LogFilter


class LogFilterTestCase(CustomAPITestCase):

    def test_q__base_on_title(self):
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged in."
        )
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged out."
        )
        Log.objects.create(
            user=self.user,
            ip_address="127.1.0.5",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged out",
            description="user logged in."
        )
        data = {
            'q': "logged in"
        }
        log_filter = LogFilter(data)
        self.assertEqual(log_filter.qs.count(), 2)

    def test_q__base_on_user_username(self):
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged in."
        )
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged out."
        )
        Log.objects.create(
            user=self.user,
            ip_address="127.1.0.5",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged out",
            description="user logged in."
        )
        data = {
            'q': "user"
        }
        log_filter = LogFilter(data)
        self.assertEqual(log_filter.qs.count(), 1)

    def test_q__base_on_ip_address(self):
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged in."
        )
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged out."
        )
        Log.objects.create(
            user=self.user,
            ip_address="127.1.0.5",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged out",
            description="user logged in."
        )
        data = {
            'q': "127.0"
        }
        log_filter = LogFilter(data)
        self.assertEqual(log_filter.qs.count(), 2)

    def test_is_authentication(self):
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged in."
        )
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_accounting=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged out."
        )
        Log.objects.create(
            user=self.user,
            ip_address="127.1.0.5",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged out",
            description="user logged in."
        )
        data = {
            'is_authentication': 'true'
        }
        log_filter = LogFilter(data)
        self.assertEqual(log_filter.qs.count(), 2)

    def test_is_authorization(self):
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_authorization=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged in."
        )
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_accounting=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged out."
        )
        Log.objects.create(
            user=self.user,
            ip_address="127.1.0.5",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged out",
            description="user logged in."
        )
        data = {
            'is_authorization': 'true'
        }
        log_filter = LogFilter(data)
        self.assertEqual(log_filter.qs.count(), 1)

    def test_is_accounting(self):
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_accounting=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged in."
        )
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_accounting=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged out."
        )
        Log.objects.create(
            user=self.user,
            ip_address="127.1.0.5",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged out",
            description="user logged in."
        )
        data = {
            'is_accounting': 'true'
        }
        log_filter = LogFilter(data)
        self.assertEqual(log_filter.qs.count(), 2)

    def test_category(self):
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged in."
        )
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_accounting=True,
            category="not_user",
            action="login",
            title="Logged in",
            description="admin logged out."
        )
        Log.objects.create(
            user=self.user,
            ip_address="127.1.0.5",
            is_authentication=True,
            category="not_user",
            action="login",
            title="Logged out",
            description="user logged in."
        )
        data = {
            'category': 'user'
        }
        log_filter = LogFilter(data)
        self.assertEqual(log_filter.qs.count(), 1)

    def test_action(self):
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged in."
        )
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_accounting=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged out."
        )
        Log.objects.create(
            user=self.user,
            ip_address="127.1.0.5",
            is_authentication=True,
            category="user",
            action="logout",
            title="Logged out",
            description="user logged in."
        )

        data = {
            'action': 'login'
        }
        log_filter = LogFilter(data)
        self.assertEqual(log_filter.qs.count(), 2)

    def test_date(self):
        now = timezone.now()
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged in."
        )
        log2 = Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_accounting=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged out."
        )
        three_years_ago = now - timezone.timedelta(days=365*3) # 3 Years ago
        """
        Because created_at is auto_now_add so if i provide 
        the datetime when creating the object django will
        ignore it and set the created_at dattime at now
        so first we create the object and then update the object
        at the time we want.
        """
        log2.created_at = three_years_ago
        log2.save(update_fields=['created_at'])
        log2.refresh_from_db()
        four_years_ago = now - timezone.timedelta(days=365*4) # 4 Years ago
        log3 = Log.objects.create(
            user=self.user,
            ip_address="127.1.0.5",
            is_authentication=True,
            category="user",
            action="logout",
            title="Logged out",
            description="user logged in."
        )
        log3.created_at = four_years_ago
        log3.save(update_fields=['created_at'])
        log3.refresh_from_db()
        formated_string = "%Y-%m-%d"
        data = {
            'date_after': three_years_ago.strftime(formated_string), 
            'date_before': now.strftime(formated_string)
        }
        log_filter = LogFilter(data)
        self.assertEqual(log_filter.qs.count(), 2)