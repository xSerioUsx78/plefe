from rest_framework import status
from utils.test import CustomAPITestCase
from activity_logger.models import Log, LogDetail


class LogTestCase(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.url = '/api/log/'

    def test_list__admin(self):
        Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged in."
        )
        self.authenticate(self.admin)
        
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = res.json()
        
        self.assertIn('results', data)
        
        self.assertEqual(data['count'], Log.objects.count())
        
        results = data['results']
        
        for result in results:
            self.assertIn('id', result)
            self.assertIn('user', result)
            self.assertEqual(type(result['user']), dict)
            self.assertIn('ip_address', result)
            self.assertIn('category', result)
            self.assertIn('action', result)
            self.assertIn('title', result)
            self.assertIn('description', result)
            self.assertIn('created_at', result)
            self.assertIn('created_at_timesince', result)
            self.assertIn('details_count', result)

    def test_list__user(self):
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
            user=self.user,
            ip_address="127.0.0.1",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="user logged in."
        )
        self.authenticate(self.user)
        
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = res.json()
        
        self.assertIn('results', data)
        
        self.assertEqual(data['count'], Log.objects.filter(user=self.user).count())
        
        results = data['results']
        
        for result in results:
            self.assertIn('id', result)
            self.assertIn('user', result)
            self.assertEqual(type(result['user']), dict)
            self.assertIn('ip_address', result)
            self.assertIn('category', result)
            self.assertIn('action', result)
            self.assertIn('title', result)
            self.assertIn('description', result)
            self.assertIn('created_at', result)
            self.assertIn('created_at_timesince', result)
            self.assertIn('details_count', result)
        
    def test_log_details_list_success__admin(self):
        log = Log.objects.create(
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
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged in."
        )
        LogDetail.objects.create(
            log=log,
            title="Detail1",
            description="Detail1"
        )
        LogDetail.objects.create(
            log=log,
            title="Detail2",
            description="Detail2"
        )
        LogDetail.objects.create(
            log=log,
            title="Detail3",
            description="Detail3"
        )
        LogDetail.objects.create(
            log=log2,
            title="Detail4",
            description="Detail4"
        )
        self.authenticate(self.admin)
        
        res = self.client.get(f'{self.url}{log.id}/details/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        results = res.json()
        
        self.assertEqual(len(results), LogDetail.objects.filter(log=log).count())
        
        for result in results:
            self.assertIn('id', result)
            self.assertIn('log', result)
            self.assertIn('title', result)
            self.assertIn('description', result)

    def test_log_details_list_success__admin_can_see_also_other_users_log_details(self):
        log = Log.objects.create(
            user=self.user,
            ip_address="127.0.0.1",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged in."
        )
        LogDetail.objects.create(
            log=log,
            title="Detail1",
            description="Detail1"
        )
        LogDetail.objects.create(
            log=log,
            title="Detail2",
            description="Detail2"
        )
        LogDetail.objects.create(
            log=log,
            title="Detail3",
            description="Detail3"
        )
        self.authenticate(self.admin)
        
        res = self.client.get(f'{self.url}{log.id}/details/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        results = res.json()
        
        self.assertEqual(len(results), LogDetail.objects.filter(log=log).count())
        
        for result in results:
            self.assertIn('id', result)
            self.assertIn('log', result)
            self.assertIn('title', result)
            self.assertIn('description', result)

    def test_log_details_list_success__user_can_see_his_log_details(self):
        log = Log.objects.create(
            user=self.user,
            ip_address="127.0.0.1",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged in."
        )
        LogDetail.objects.create(
            log=log,
            title="Detail1",
            description="Detail1"
        )
        LogDetail.objects.create(
            log=log,
            title="Detail2",
            description="Detail2"
        )
        LogDetail.objects.create(
            log=log,
            title="Detail3",
            description="Detail3"
        )
        self.authenticate(self.user)
        
        res = self.client.get(f'{self.url}{log.id}/details/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        results = res.json()
        self.assertEqual(len(results), LogDetail.objects.filter(log=log).count())

        for result in results:
            self.assertIn('id', result)
            self.assertIn('log', result)
            self.assertIn('title', result)
            self.assertIn('description', result) 

    def test_log_details_list_failed__user_cant_access_other_users_log_details(self):
        log = Log.objects.create(
            user=self.admin,
            ip_address="127.0.0.1",
            is_authentication=True,
            category="user",
            action="login",
            title="Logged in",
            description="admin logged in."
        )
        LogDetail.objects.create(
            log=log,
            title="Detail1",
            description="Detail1"
        )
        self.authenticate(self.user)
        
        res = self.client.get(f'{self.url}{log.id}/details/')

        """
        it will raise 404 because drf will fetch the log object base
        on filtered queryset and there we controlled that the user can
        only see his log objects.
        """
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)