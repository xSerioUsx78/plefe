from django.contrib.auth import get_user_model
from rest_framework import status
from utils.test import CustomAPITestCase
from watchlist import models
from signalapp import models as signal_models


User = get_user_model()


class TaskTestCase(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.url = '/api/v1/watchlist/task/'

    def test_task_create(self):
        self.authenticate(self.superuser)
        
        data = {
            "title": "First Task",
            "description": "First Task Desc"
        }
        res = self.client.post(self.url, data, json=True)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        obj = models.Task.objects.first()
        self.assertTrue(obj.user)
        self.assertTrue(obj.title)
        self.assertTrue(obj.description)
        self.assertEqual(obj.user, self.superuser)

    def test_task_update(self):
        self.authenticate(self.superuser)

        obj = models.Task.objects.create(
            user=self.superuser,
            title="First Title",
            description="First Desc"
        )
        
        data = {
            "title": "First Title Edited",
            "description": "First Desc Edited"
        }
        res = self.client.put(f'{self.url}{obj.id}/', data, json=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        updated_obj = models.Task.objects.first()
        self.assertNotEqual(obj.title, updated_obj.title)
        self.assertNotEqual(obj.description, updated_obj.description)
        self.assertEqual(obj.user, updated_obj.user)

    def test_task_delete(self):
        self.authenticate(self.superuser)
        obj = models.Task.objects.create(
            user=self.superuser,
            title="First Title",
            description="First Desc"
        )
        res = self.client.delete(f'{self.url}{obj.id}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            models.Task.objects.count(),
            0
        )

    def test_task_bulk_delete(self):
        self.authenticate(self.superuser)
        obj1 = models.Task.objects.create(
            user=self.superuser,
            title="First Title",
            description="First Desc"
        )
        obj2 = models.Task.objects.create(
            user=self.superuser,
            title="Second Title",
            description="Second Desc"
        )
        obj3 = models.Task.objects.create(
            user=self.superuser,
            title="Third Title",
            description="Third Desc"
        )
        data = {
            'ids': [obj1.id, obj2.id, obj3.id]
        }
        res = self.client.delete(f'{self.url}bulk/', data, json=True)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            models.Task.objects.count(),
            0
        )

    def test_task_list(self):
        self.authenticate(self.superuser)
        models.Task.objects.create(
            user=self.superuser,
            title="First Title",
            description="First Desc"
        )
        models.Task.objects.create(
            user=self.superuser,
            title="Second Title",
            description="Second Desc"
        )
        models.Task.objects.create(
            user=self.superuser,
            title="Third Title",
            description="Third Desc"
        )

        res = self.client.get(f'{self.url}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        results = res.json()['results']
        self.assertEqual(len(results), 3)

    def test_get_task_checklist(self):
        self.authenticate(self.user)
        obj1 = models.Task.objects.create(
            user=self.superuser,
            title="First Title",
            description="First Desc"
        )
        obj2 = models.Task.objects.create(
            user=self.superuser,
            title="Second Title",
            description="Second Desc"
        )
        models.TaskChecklist.objects.create(
            task=obj1,
            text="First checklist"
        )
        models.TaskChecklist.objects.create(
            task=obj1,
            text="Second checklist"
        )
        models.TaskChecklist.objects.create(
            task=obj2,
            text="First checklist"
        )
        res = self.client.get(f'{self.url}{obj1.pk}/checklist/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(len(data), 2)


    def task_change_phase_success__performer_to_deputy(self):
        self.authenticate(self.user)

        task = models.Task.objects.create(
            user=self.superuser,
            title="First Title",
            description="First Desc"
        )
        models.TaskUser.objects.create(
            task=task,
            user=self.user,
            role=models.TaskUser.ROLE_PERFORMER
        )

        data = {
            'phase': models.Task.PHASE_DEPUTY
        }

        url = f'{self.url}{task.pk}/phase/'
        res = self.client.put(url, data, json=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        task.refresh_from_db()

        self.assertEqual(int(task.phase), models.Task.PHASE_DEPUTY)

    def task_change_phase_error__performer_change_phase_from_deputy(self):
        self.authenticate(self.user)

        task = models.Task.objects.create(
            user=self.superuser,
            title="First Title",
            description="First Desc",
            phase=models.Task.PHASE_DEPUTY
        )
        models.TaskUser.objects.create(
            task=task,
            user=self.user,
            role=models.TaskUser.ROLE_PERFORMER
        )

        data = {
            'phase': models.Task.PHASE_DEPUTY
        }

        url = f'{self.url}{task.pk}/phase/'
        res = self.client.put(url, data, json=True)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        task.refresh_from_db()

        self.assertEqual(int(task.phase), models.Task.PHASE_DEPUTY)

    def task_change_phase_error__performer_change_phase_from_manager(self):
        self.authenticate(self.user)

        task = models.Task.objects.create(
            user=self.superuser,
            title="First Title",
            description="First Desc",
            phase=models.Task.PHASE_MANAGER
        )
        models.TaskUser.objects.create(
            task=task,
            user=self.user,
            role=models.TaskUser.ROLE_PERFORMER
        )

        data = {
            'phase': models.Task.PHASE_DEPUTY
        }

        url = f'{self.url}{task.pk}/phase/'
        res = self.client.put(url, data, json=True)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        task.refresh_from_db()

        self.assertEqual(int(task.phase), models.Task.PHASE_MANAGER)

    def task_change_phase_error__performer_to_manager(self):
        self.authenticate(self.user)

        task = models.Task.objects.create(
            user=self.superuser,
            title="First Title",
            description="First Desc"
        )
        models.TaskUser.objects.create(
            task=task,
            user=self.user,
            role=models.TaskUser.ROLE_PERFORMER
        )

        data = {
            'phase': models.Task.PHASE_MANAGER
        }

        url = f'{self.url}{task.pk}/phase/'
        res = self.client.put(url, data, json=True)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        task.refresh_from_db()

        self.assertEqual(int(task.phase), models.Task.PHASE_PERFORMER)


    def task_change_phase_success__deputy_to_manager(self):
            self.authenticate(self.user)

            task = models.Task.objects.create(
                user=self.superuser,
                title="First Title",
                description="First Desc",
                phase=models.Task.PHASE_DEPUTY
            )
            models.TaskUser.objects.create(
                task=task,
                user=self.user,
                role=models.TaskUser.ROLE_DEPUTY
            )

            data = {
                'phase': models.Task.PHASE_MANAGER
            }

            url = f'{self.url}{task.pk}/phase/'
            res = self.client.put(url, data, json=True)
            self.assertEqual(res.status_code, status.HTTP_200_OK)

            task.refresh_from_db()

            self.assertEqual(int(task.phase), models.Task.PHASE_MANAGER)

    def task_change_phase_success__deputy_to_peformer(self):
        self.authenticate(self.user)

        task = models.Task.objects.create(
            user=self.superuser,
            title="First Title",
            description="First Desc",
            phase=models.Task.PHASE_DEPUTY
        )
        models.TaskUser.objects.create(
            task=task,
            user=self.user,
            role=models.TaskUser.ROLE_DEPUTY
        )

        data = {
            'phase': models.Task.PHASE_PERFORMER
        }

        url = f'{self.url}{task.pk}/phase/'
        res = self.client.put(url, data, json=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        task.refresh_from_db()

        self.assertEqual(int(task.phase), models.Task.PHASE_PERFORMER)

    def task_change_phase_error__deputy_change_phase_from_performer(self):
        self.authenticate(self.user)

        task = models.Task.objects.create(
            user=self.superuser,
            title="First Title",
            description="First Desc"
        )
        models.TaskUser.objects.create(
            task=task,
            user=self.user,
            role=models.TaskUser.ROLE_DEPUTY
        )

        data = {
            'phase': models.Task.PHASE_MANAGER
        }

        url = f'{self.url}{task.pk}/phase/'
        res = self.client.put(url, data, json=True)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        task.refresh_from_db()

        self.assertEqual(int(task.phase), models.Task.PHASE_PERFORMER)

    def task_change_phase_error__deputy_change_phase_from_manager(self):
        self.authenticate(self.user)

        task = models.Task.objects.create(
            user=self.superuser,
            title="First Title",
            description="First Desc",
            phase=models.Task.PHASE_MANAGER
        )
        models.TaskUser.objects.create(
            task=task,
            user=self.user,
            role=models.TaskUser.ROLE_DEPUTY
        )

        data = {
            'phase': models.Task.PHASE_MANAGER
        }

        url = f'{self.url}{task.pk}/phase/'
        res = self.client.put(url, data, json=True)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        task.refresh_from_db()

        self.assertEqual(int(task.phase), models.Task.PHASE_MANAGER)

    def task_change_phase_success_superuser(self):
            self.authenticate(self.superuser)

            task = models.Task.objects.create(
                user=self.superuser,
                title="First Title",
                description="First Desc",
                phase=models.Task.PHASE_DEPUTY
            )

            data = {
                'phase': models.Task.PHASE_PERFORMER
            }

            url = f'{self.url}{task.pk}/phase/'
            res = self.client.put(url, data, json=True)
            self.assertEqual(res.status_code, status.HTTP_200_OK)

            task.refresh_from_db()

            self.assertEqual(int(task.phase), models.Task.PHASE_PERFORMER)

    def task_change_phase_success_manager(self):
            self.authenticate(self.user)

            task = models.Task.objects.create(
                user=self.user,
                title="First Title",
                description="First Desc",
                phase=models.Task.PHASE_MANAGER
            )
            models.TaskUser.objects.create(
                task=task,
                user=self.user,
                role=models.TaskUser.ROLE_MANAGER
            )

            data = {
                'phase': models.Task.PHASE_DEPUTY
            }

            url = f'{self.url}{task.pk}/phase/'
            res = self.client.put(url, data, json=True)
            self.assertEqual(res.status_code, status.HTTP_200_OK)

            task.refresh_from_db()

            self.assertEqual(int(task.phase), models.Task.PHASE_DEPUTY)

    def task_change_phase_error__no_task_user(self):
        self.authenticate(self.user)

        task = models.Task.objects.create(
            user=self.superuser,
            title="First Title",
            description="First Desc"
        )

        data = {
            'phase': models.Task.PHASE_DEPUTY
        }

        url = f'{self.url}{task.pk}/phase/'
        res = self.client.put(url, data, json=True)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        task.refresh_from_db()

        self.assertEqual(int(task.phase), models.Task.PHASE_PERFORMER)


class TaskUserTestCase(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.url = '/api/v1/watchlist/task/user/'

        self.task = models.Task.objects.create(
            user=self.superuser,
            title="First Task",
            description="First Desc"
        )

    def test_task_user_create(self):
        self.authenticate(self.superuser)
        
        data = {
            "task": self.task.id,
            "user": self.user.id,
            "role": models.TaskUser.ROLE_PERFORMER
        }
        res = self.client.post(self.url, data, json=True)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        obj = models.TaskUser.objects.first()
        self.assertTrue(obj.user)
        self.assertTrue(obj.task)
        self.assertTrue(obj.role)

        self.assertEqual(obj.task, self.task)
        self.assertEqual(obj.user, self.user)
        self.assertEqual(obj.role, models.TaskUser.ROLE_PERFORMER)

    def test_task_user_update(self):
        self.authenticate(self.superuser)

        obj = models.TaskUser.objects.create(
            task=self.task,
            user=self.user,
            role=models.TaskUser.ROLE_PERFORMER
        )
        
        data = {
            "task": self.task.id,
            "user": self.admin.id,
            "role": models.TaskUser.ROLE_DEPUTY
        }
        res = self.client.put(f'{self.url}{obj.id}/', data, json=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        updated_obj = models.TaskUser.objects.first()
        self.assertNotEqual(obj.user, updated_obj.user)
        self.assertNotEqual(obj.role, updated_obj.role)
        self.assertEqual(obj.task, updated_obj.task)

    def test_task_user_delete(self):
        self.authenticate(self.superuser)
        obj = models.TaskUser.objects.create(
            task=self.task,
            user=self.user,
            role=models.TaskUser.ROLE_PERFORMER
        )
        res = self.client.delete(f'{self.url}{obj.id}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            models.TaskUser.objects.count(),
            0
        )

    def test_task_user_bulk_delete(self):
        self.authenticate(self.superuser)
        obj1 = models.TaskUser.objects.create(
            task=self.task,
            user=self.user,
            role=models.TaskUser.ROLE_PERFORMER
        )
        obj2 = models.TaskUser.objects.create(
            task=self.task,
            user=self.user,
            role=models.TaskUser.ROLE_PERFORMER
        )
        obj3 = models.TaskUser.objects.create(
            task=self.task,
            user=self.user,
            role=models.TaskUser.ROLE_PERFORMER
        )
        data = {
            'ids': [obj1.id, obj2.id, obj3.id]
        }
        res = self.client.delete(f'{self.url}bulk/', data, json=True)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            models.TaskUser.objects.count(),
            0
        )

    def test_task_user_list(self):
        self.authenticate(self.superuser)
        models.TaskUser.objects.create(
            task=self.task,
            user=self.superuser,
            role=models.TaskUser.ROLE_MANAGER
        )
        models.TaskUser.objects.create(
            task=self.task,
            user=self.admin,
            role=models.TaskUser.ROLE_DEPUTY
        )
        models.TaskUser.objects.create(
            task=self.task,
            user=self.user,
            role=models.TaskUser.ROLE_PERFORMER
        )

        res = self.client.get(f'{self.url}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        results = res.json()['results']
        self.assertEqual(len(results), 3)


class TaskCoinTestCase(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.url = '/api/v1/watchlist/task/coin/'

        self.task = models.Task.objects.create(
            user=self.superuser,
            title="First Task",
            description="First Desc"
        )

        self.coin1 = signal_models.SignalCoin.objects.create(
            coin_id="@btc",
            symbol="BTC",
            name="Bitcoin"
        )
        self.coin2 = signal_models.SignalCoin.objects.create(
            coin_id="@eth",
            symbol="ETH",
            name="Etherium"
        )

    def test_task_coin_create_bulk__success_all_coins_new(self):
        self.authenticate(self.superuser)
        
        data = {
            "task": self.task.id,
            "coins_id": [self.coin1.id, self.coin2.id]
        }
        res = self.client.post(f'{self.url}bulk/', data, json=True)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        objs = models.TaskCoin.objects.all()

        self.assertEqual(objs.count(), 2)

        for obj in objs:
            self.assertTrue(obj.task)
            self.assertTrue(obj.coin)

    def test_task_coin_create_bulk__success_one_coin_new(self):
        self.authenticate(self.superuser)
        
        models.TaskCoin.objects.create(
            task=self.task,
            coin=self.coin1
        )

        data = {
            "task": self.task.id,
            "coins_id": [self.coin2.id]
        }
        res = self.client.post(f'{self.url}bulk/', data, json=True)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        objs = models.TaskCoin.objects.all()

        self.assertEqual(objs.count(), 2)

        for obj in objs:
            self.assertTrue(obj.task)
            self.assertTrue(obj.coin)
    
    def test_task_coin_create_bulk__error_send_already_added_coins(self):
        self.authenticate(self.superuser)
            
        models.TaskCoin.objects.create(
            task=self.task,
            coin=self.coin1
        )
        models.TaskCoin.objects.create(
            task=self.task,
            coin=self.coin2
        )

        data = {
            "task": self.task.id,
            "coins_id": [self.coin1.id, self.coin2.id]
        }
        res = self.client.post(f'{self.url}bulk/', data, json=True)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        objs = models.TaskCoin.objects.all()
        self.assertEqual(objs.count(), 2)

    def test_task_coin_create_bulk__error_not_valid_task_id(self):
        self.authenticate(self.superuser)

        data = {
            "task": 1000,
            "coins_id": [self.coin1.id, self.coin2.id]
        }
        res = self.client.post(f'{self.url}bulk/', data, json=True)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        objs = models.TaskCoin.objects.all()
        self.assertEqual(objs.count(), 0)

    def test_task_coin_delete(self):
        self.authenticate(self.superuser)
        obj = models.TaskCoin.objects.create(
            task=self.task,
            coin=self.coin1
        )
        res = self.client.delete(f'{self.url}{obj.id}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            models.TaskCoin.objects.count(),
            0
        )

    def test_task_coin_bulk_delete(self):
        self.authenticate(self.superuser)
        obj1 = models.TaskCoin.objects.create(
            task=self.task,
            coin=self.coin1
        )
        obj2 = models.TaskCoin.objects.create(
            task=self.task,
            coin=self.coin2
        )
        data = {
            'ids': [obj1.id, obj2.id]
        }
        res = self.client.delete(f'{self.url}bulk/', data, json=True)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            models.TaskCoin.objects.count(),
            0
        )

    def test_task_coin_list(self):
        self.authenticate(self.superuser)
        models.TaskCoin.objects.create(
            task=self.task,
            coin=self.coin1
        )
        models.TaskCoin.objects.create(
            task=self.task,
            coin=self.coin2
        )

        res = self.client.get(f'{self.url}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        results = res.json()['results']
        self.assertEqual(len(results), 2)


class TaskChecklistTestCase(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.url = '/api/v1/watchlist/task/checklist/'

        self.task = models.Task.objects.create(
            user=self.superuser,
            title="First Task",
            description="First Desc"
        )

    def test_task_checklist_create(self):
        self.authenticate(self.superuser)
        
        data = {
            "task": self.task.id,
            "text": "First checklist"
        }
        res = self.client.post(f'{self.url}', data, json=True)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        obj = models.TaskChecklist.objects.first()
        self.assertTrue(obj)
        self.assertTrue(obj.task)
        self.assertTrue(obj.text)
        self.assertEqual(obj.order, 0)

        # Now we create another one, it should set the order to 1
        data = {
            "task": self.task.id,
            "text": "Second checklist"
        }
        res = self.client.post(f'{self.url}', data, json=True)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        obj = models.TaskChecklist.objects.last()
        self.assertTrue(obj)
        self.assertTrue(obj.task)
        self.assertTrue(obj.text)
        self.assertEqual(obj.order, 1)

    def test_task_checklist_list(self):
        self.authenticate(self.superuser)
        models.TaskChecklist.objects.create(
            task=self.task,
            text="First checklist"
        )
        models.TaskChecklist.objects.create(
            task=self.task,
            text="Second checklist"
        )

        res = self.client.get(f'{self.url}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        results = res.json()['results']
        self.assertEqual(len(results), 2)

    def test_task_checklist_delete(self):
        self.authenticate(self.superuser)
        obj = models.TaskChecklist.objects.create(
            task=self.task,
            text="First checklist"
        )
        res = self.client.delete(f'{self.url}{obj.id}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            models.TaskChecklist.objects.count(),
            0
        )

    def test_task_checklist_update(self):
        self.authenticate(self.superuser)
        obj = models.TaskChecklist.objects.create(
            task=self.task,
            text="First checklist"
        )
        data = {
            'task': self.task.id,
            'text': 'First checklist edited'
        }
        res = self.client.put(f'{self.url}{obj.id}/', data, json=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        updated_obj = models.TaskChecklist.objects.get(pk=obj.pk)
        self.assertNotEqual(obj.text, updated_obj.text)

    def test_task_checklist_change_checked(self):
        self.authenticate(self.user)
        obj = models.TaskChecklist.objects.create(
            task=self.task,
            text="First checklist"
        )
        data = {
            'checked': True
        }
        res = self.client.put(f'{self.url}{obj.id}/checked/', data, json=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        updated_obj = models.TaskChecklist.objects.first()
        self.assertNotEqual(obj.checked, updated_obj.checked)