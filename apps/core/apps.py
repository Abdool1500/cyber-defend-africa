from django.apps import AppConfig


def _patch_base_context_copy():
    """Works around a Django 5.1 / Python 3.14 incompatibility.

    django.template.context.BaseContext.__copy__ does `copy(super())`,
    relying on `copy.copy()` handling a bound `super` proxy object as a
    stand-in for "a blank instance of the parent class". That trick no
    longer produces a usable object on Python 3.14 (AttributeError:
    'super' object has no attribute 'dicts'), which breaks *any* code path
    that copies a template Context — most notably Django's own test
    Client, which copies the rendered context after every template render
    for assertTemplateUsed()/response.context support. Every view that
    renders a template fails under `manage.py test` without this patch.

    This replaces it with a straightforward, equivalent shallow copy that
    doesn't rely on that idiom. Remove once upstream Django supports
    Python 3.14 properly.
    """
    from django.template.context import BaseContext

    if getattr(BaseContext.__copy__, "_cda_patched", False):
        return

    def __copy__(self):
        duplicate = self.__class__.__new__(self.__class__)
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    __copy__._cda_patched = True
    BaseContext.__copy__ = __copy__


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"
    verbose_name = "Core"

    def ready(self):
        _patch_base_context_copy()
