from zope.interface import Interface
from zope.interface.interfaces import IInterface

from plone.supermodel.directives import MetadataDictDirective
from plone.supermodel.directives import MetadataListDirective
from plone.supermodel.directives import DictCheckerPlugin
from plone.supermodel.directives import ListCheckerPlugin
from plone.supermodel.directives import ListPositionCheckerPlugin

from plone.autoform.interfaces import OMITTED_KEY, WIDGETS_KEY, MODES_KEY, ORDER_KEY
from plone.autoform.interfaces import READ_PERMISSIONS_KEY, WRITE_PERMISSIONS_KEY

class omit(MetadataListDirective):
    """Directive used to omit one or more fields
    """

    key = OMITTED_KEY
    value = 'true'

    def factory(self, *args):
        if not args:
            raise TypeError('The %s directive expects at least one argument.' % self.__class__.__name__)
        form_interface = Interface
        if IInterface.providedBy(args[0]):
            form_interface = args[0]
            args = args[1:]
        return [(form_interface, field, self.value) for field in args]


class no_omit(omit):
    """Directive used to prevent one or more fields from being omitted
    """
    value = 'false'


class OmittedPlugin(ListPositionCheckerPlugin):
    key = OMITTED_KEY
    position = 1


class mode(MetadataListDirective):
    """Directive used to set the mode of one or more fields
    """

    key = MODES_KEY

    def factory(self, *args, **kw):
        if len(args) > 1:
            raise TypeError('The mode directive expects 0 or 1 non-keyword arguments.')
        form_interface = Interface
        if args:
            form_interface = args[0]
        return [(form_interface, field, mode) for field, mode in kw.items()]


class ModesPlugin(ListPositionCheckerPlugin):
    key = MODES_KEY
    position = 1


class widget(MetadataDictDirective):
    """Directive used to set the widget for one or more fields
    """

    key = WIDGETS_KEY

    def factory(self, **kw):
        widgets = {}
        for field_name, widget in kw.items():
            if not isinstance(widget, basestring):
                widget = "%s.%s" % (widget.__module__, widget.__name__)
            widgets[field_name] = widget
        return widgets


class WidgetsPlugin(DictCheckerPlugin):
    key = WIDGETS_KEY


class order_before(MetadataListDirective):
    """Directive used to order one field before another
    """

    key = ORDER_KEY
    value = 'before'

    def factory(self, **kw):
        return [(field_name, self.value, relative_to) for field_name, relative_to in kw.items()]


class order_after(order_before):
    """Directive used to order one field after another
    """

    value = 'after'


class OrderPlugin(ListPositionCheckerPlugin):
    key = ORDER_KEY
    position = 0


class read_permission(MetadataDictDirective):
    """Directive used to set a field read permission
    """

    key = READ_PERMISSIONS_KEY

    def factory(self, **kw):
        return kw


class ReadPermissionsPlugin(DictCheckerPlugin):
    key = READ_PERMISSIONS_KEY


class write_permission(MetadataDictDirective):
    """Directive used to set a field write permission
    """

    key = WRITE_PERMISSIONS_KEY

    def factory(self, **kw):
        return kw


class WritePermissionsPlugin(DictCheckerPlugin):
    key = WRITE_PERMISSIONS_KEY
