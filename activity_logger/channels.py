from .handlers import action_handler, action_bulk_handler


async def set_log(bulk: bool = False, **kwargs):
    # TODO: Test this
    if bulk:
        await action_bulk_handler(signal=None, **kwargs)
        return
    await action_handler(signal=None, **kwargs)