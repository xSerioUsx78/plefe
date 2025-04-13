from utils.test import CustomAPITestCase
from activity_logger.signals import action, action_bulk
from activity_logger.models import Log, LogDetail


class ActionHandlerTestCase(CustomAPITestCase):

    def test_action_handler__all(self):
        """
        We will pass all the possible kwargs
        """
        user = self.admin
        action.send(
            'test',
            user=user,
            category="user",
            action="create",
            title="User created",
            description=f'User with username "{user.username}" has been created by "{user.username}".',
            is_accounting=True,
            ip_address="127.0.0.1",
            target=user,
            details=[
                {'title': 'Detail1 title', "description": "Detail1 description"},
                {'title': 'Detail2 title', "description": "Detail2 description"},
                {'title': 'Detail3 title', "description": "Detail3 description"}
            ]
        )
        self.assertEqual(Log.objects.count(), 1)
        log = Log.objects.first()
        self.assertTrue(log.user)
        self.assertTrue(log.category)
        self.assertTrue(log.action)
        self.assertTrue(log.title)
        self.assertTrue(log.description)
        self.assertTrue(log.is_accounting)
        self.assertTrue(log.ip_address)
        self.assertTrue(log.content_type)
        self.assertEqual(log.content_type.model, 'user')
        self.assertTrue(log.object_id)
        self.assertEqual(log.object_id, self.admin.id)
        self.assertEqual(log.details.count(), 3)

        self.assertEqual(LogDetail.objects.count(), 3)
        log_detail = LogDetail.objects.all()
        for detail in log_detail:
            self.assertTrue(detail.title)
            self.assertTrue(detail.description)

    def test_action_handler__except_target(self):
        """
        We will pass all the possible kwargs except target
        """
        user = self.admin
        action.send(
            'test',
            user=user,
            category="user",
            action="create",
            title="User created",
            description=f'User with username "{user.username}" has been created by "{user.username}".',
            is_accounting=True,
            ip_address="127.0.0.1",
            details=[
                {'title': 'Detail1 title', "description": "Detail1 description"},
                {'title': 'Detail2 title', "description": "Detail2 description"},
                {'title': 'Detail3 title', "description": "Detail3 description"}
            ]
        )
        self.assertEqual(Log.objects.count(), 1)
        log = Log.objects.first()
        self.assertTrue(log.user)
        self.assertTrue(log.category)
        self.assertTrue(log.action)
        self.assertTrue(log.title)
        self.assertTrue(log.description)
        self.assertTrue(log.is_accounting)
        self.assertTrue(log.ip_address)
        self.assertEqual(log.details.count(), 3)

        self.assertEqual(LogDetail.objects.count(), 3)
        log_detail = LogDetail.objects.all()
        for detail in log_detail:
            self.assertTrue(detail.title)
            self.assertTrue(detail.description)

    def test_action_handler__except_details(self):
        """
        We will pass all the possible kwargs except target
        """
        user = self.admin
        action.send(
            'test',
            user=user,
            category="user",
            action="create",
            title="User created",
            description=f'User with username "{user.username}" has been created by "{user.username}".',
            is_accounting=True,
            ip_address="127.0.0.1",
            target=user,
        )
        self.assertEqual(Log.objects.count(), 1)
        log = Log.objects.first()
        self.assertTrue(log.user)
        self.assertTrue(log.category)
        self.assertTrue(log.action)
        self.assertTrue(log.title)
        self.assertTrue(log.description)
        self.assertTrue(log.is_accounting)
        self.assertTrue(log.ip_address)
        self.assertTrue(log.content_type)
        self.assertEqual(log.content_type.model, 'user')
        self.assertTrue(log.object_id)
        self.assertEqual(log.object_id, self.admin.id)
        self.assertEqual(log.details.count(), 0)

        self.assertEqual(LogDetail.objects.count(), 0)


class ActionBulkHandlerTestCase(CustomAPITestCase):

    def test_action_bulk_handler__all(self):
        """
        We will pass all the possible kwargs
        """
        user = self.admin
        logs = [
            {'user': user,
            'category': "user",
            'action': "create",
            'title': "User created",
            'description': f'User with username "{user.username}" has been created by "{user.username}".',
            'is_accounting': True,
            'ip_address': "127.0.0.1",
            'target': user,
            'details': [
                {'title': 'Detail1 title', "description": "Detail1 description"},
                {'title': 'Detail2 title', "description": "Detail2 description"},
                {'title': 'Detail3 title', "description": "Detail3 description"}
            ]},
            {'user': user,
            'category': "user",
            'action': "create",
            'title': "User created",
            'description': f'User with username "{user.username}" has been created by "{user.username}".',
            'is_accounting': True,
            'ip_address': "127.0.0.1",
            'target': user,
            'details': [
                {'title': 'Detail1 title', "description": "Detail1 description"},
                {'title': 'Detail2 title', "description": "Detail2 description"},
                {'title': 'Detail3 title', "description": "Detail3 description"}
            ]},
            {'user': user,
            'category': "user",
            'action': "create",
            'title': "User created",
            'description': f'User with username "{user.username}" has been created by "{user.username}".',
            'is_accounting': True,
            'ip_address': "127.0.0.1",
            'target': user,
            'details': [
                {'title': 'Detail1 title', "description": "Detail1 description"},
                {'title': 'Detail2 title', "description": "Detail2 description"},
                {'title': 'Detail3 title', "description": "Detail3 description"}
            ]}
        ]
        action_bulk.send(
            'test',
            logs=logs
        )
        self.assertEqual(Log.objects.count(), 3)
        logs = Log.objects.all()
        for log in logs:
            self.assertTrue(log.user)
            self.assertTrue(log.category)
            self.assertTrue(log.action)
            self.assertTrue(log.title)
            self.assertTrue(log.description)
            self.assertTrue(log.is_accounting)
            self.assertTrue(log.ip_address)
            self.assertTrue(log.content_type)
            self.assertEqual(log.content_type.model, 'user')
            self.assertTrue(log.object_id)
            self.assertEqual(log.object_id, self.admin.id)
            self.assertEqual(log.details.count(), 3)

        self.assertEqual(LogDetail.objects.count(), 9)
        log_detail = LogDetail.objects.all()
        for detail in log_detail:
            self.assertTrue(detail.title)
            self.assertTrue(detail.description)

    def test_action_bulk_handler__except_target(self):
        """
        We will pass all the possible kwargs except target
        """
        user = self.admin
        logs = [
            {'user': user,
            'category': "user",
            'action': "create",
            'title': "User created",
            'description': f'User with username "{user.username}" has been created by "{user.username}".',
            'is_accounting': True,
            'ip_address': "127.0.0.1",
            'details': [
                {'title': 'Detail1 title', "description": "Detail1 description"},
                {'title': 'Detail2 title', "description": "Detail2 description"},
                {'title': 'Detail3 title', "description": "Detail3 description"}
            ]},
            {'user': user,
            'category': "user",
            'action': "create",
            'title': "User created",
            'description': f'User with username "{user.username}" has been created by "{user.username}".',
            'is_accounting': True,
            'ip_address': "127.0.0.1",
            'details': [
                {'title': 'Detail1 title', "description": "Detail1 description"},
                {'title': 'Detail2 title', "description": "Detail2 description"},
                {'title': 'Detail3 title', "description": "Detail3 description"}
            ]},
            {'user': user,
            'category': "user",
            'action': "create",
            'title': "User created",
            'description': f'User with username "{user.username}" has been created by "{user.username}".',
            'is_accounting': True,
            'ip_address': "127.0.0.1",
            'details': [
                {'title': 'Detail1 title', "description": "Detail1 description"},
                {'title': 'Detail2 title', "description": "Detail2 description"},
                {'title': 'Detail3 title', "description": "Detail3 description"}
            ]}
        ]
        action_bulk.send(
            'test',
            logs=logs
        )
        self.assertEqual(Log.objects.count(), 3)
        logs = Log.objects.all()
        for log in logs:
            self.assertTrue(log.user)
            self.assertTrue(log.category)
            self.assertTrue(log.action)
            self.assertTrue(log.title)
            self.assertTrue(log.description)
            self.assertTrue(log.is_accounting)
            self.assertTrue(log.ip_address)
            self.assertEqual(log.details.count(), 3)

        self.assertEqual(LogDetail.objects.count(), 9)
        log_detail = LogDetail.objects.all()
        for detail in log_detail:
            self.assertTrue(detail.title)
            self.assertTrue(detail.description)

    def test_action_bulk_handler__except_details(self):
        """
        We will pass all the possible kwargs except target
        """
        user = self.admin
        logs = [
            {'user': user,
            'category': "user",
            'action': "create",
            'title': "User created",
            'description': f'User with username "{user.username}" has been created by "{user.username}".',
            'is_accounting': True,
            'ip_address': "127.0.0.1",
            'target': user},
            {'user': user,
            'category': "user",
            'action': "create",
            'title': "User created",
            'description': f'User with username "{user.username}" has been created by "{user.username}".',
            'is_accounting': True,
            'ip_address': "127.0.0.1",
            'target': user},
            {'user': user,
            'category': "user",
            'action': "create",
            'title': "User created",
            'description': f'User with username "{user.username}" has been created by "{user.username}".',
            'is_accounting': True,
            'ip_address': "127.0.0.1",
            'target': user}
        ]
        action_bulk.send(
            'test',
            logs=logs
        )
        self.assertEqual(Log.objects.count(), 3)
        logs = Log.objects.all()
        for log in logs:
            self.assertTrue(log.user)
            self.assertTrue(log.category)
            self.assertTrue(log.action)
            self.assertTrue(log.title)
            self.assertTrue(log.description)
            self.assertTrue(log.is_accounting)
            self.assertTrue(log.ip_address)
            self.assertTrue(log.content_type)
            self.assertEqual(log.content_type.model, 'user')
            self.assertTrue(log.object_id)
            self.assertEqual(log.object_id, self.admin.id)
            self.assertEqual(log.details.count(), 0)

        self.assertEqual(LogDetail.objects.count(), 0)