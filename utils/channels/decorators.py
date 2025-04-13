from typing import Callable, List, Set, Tuple, Union


def has_permissions(perm_list: Union[List[str], Tuple[str], Set[str]], has_all: bool = True):
    def wrapper(func):
        async def async_inner_wrapper(*args, **kwargs):
            """
            First we get the instance of the class
            then we get some fields from it
            NOTE: 
                Be carefull this fields should always be in the consumer class
                otherwise it will cause error and crash!
            we check if the user has permissions for this event we return the function
            otherwise we return a permission denied message event to client.
            """
            instance = args[0]
            user = instance.user
            if user.has_access_to_all():
                return await func(*args, **kwargs)
            user_permissions: List = instance.user_permissions
            send_data: Callable = instance.send_data
            has_perm = user.c_check_perms(user_permissions, perm_list, has_all)
            if has_perm:
                return await func(*args, **kwargs)
            await send_data('permission', {
                'message': "You don't have proper permission to complete this task!",
                'status': 403
            })
        return async_inner_wrapper
    return wrapper