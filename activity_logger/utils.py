from django.contrib.contenttypes.models import ContentType


def get_target(**kwargs):
    if 'target' in kwargs:
        target = kwargs.pop('target')
        if target:
            c_type = ContentType.objects.get_for_model(target)
            object_id = target.id
            kwargs.update({'content_type': c_type, 'object_id': object_id})
    return kwargs


def get_details(**kwargs):
    details = None
    if 'details' in kwargs:
        details = kwargs.pop('details')
    return details, kwargs