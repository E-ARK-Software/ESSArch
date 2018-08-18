import importlib

from django.conf import settings

AVAILABLE_TRANSFORMERS = {}

extra_transformers = getattr(settings, 'ESSARCH_TRANSFORMERS', {})
AVAILABLE_TRANSFORMERS.update(extra_transformers)


def get_backend(name, *args, **kwargs):
    try:
        module_name, klass = AVAILABLE_TRANSFORMERS[name].rsplit('.', 1)
    except KeyError:
        raise ValueError('Transformer backend "%s" not found' % name)

    return getattr(importlib.import_module(module_name), klass)(*args, **kwargs)
