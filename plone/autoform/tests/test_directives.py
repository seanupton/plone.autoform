import unittest

from zope.interface import Interface

import zope.component
import zope.app.component
import zope.component.testing
from zope.configuration import xmlconfig
import Products.Five

from plone.supermodel import model
from plone import autoform

from plone.supermodel.interfaces import FILENAME_KEY, SCHEMA_NAME_KEY
from plone.autoform.interfaces import OMITTED_KEY, WIDGETS_KEY, MODES_KEY, ORDER_KEY
from plone.autoform.interfaces import READ_PERMISSIONS_KEY, WRITE_PERMISSIONS_KEY

class DummyWidget(object):
    pass

class TestAutoformDirectives(unittest.TestCase):

    def setUp(self):
        xmlconfig.XMLConfig('meta.zcml', zope.component)()
        xmlconfig.XMLConfig('meta.zcml', zope.app.component)()
        xmlconfig.XMLConfig('configure.zcml', Products.Five)()
        xmlconfig.XMLConfig('configure.zcml', autoform)()

    def tearDown(self):
        zope.component.testing.tearDown()
    
    def test_schema_directives_store_tagged_values(self):
        
        class IDummy(model.Schema):
            
            autoform.omit('foo', 'bar')
            autoform.omit(model.Schema, 'qux')
            autoform.no_omit(model.Schema, 'bar')
            autoform.widget(foo='some.dummy.Widget', baz='other.Widget')
            autoform.mode(bar='hidden')
            autoform.mode(model.Schema, bar='input')
            autoform.order_before(baz='title')
            autoform.order_after(qux='title')
            autoform.read_permission(foo='zope2.View')
            autoform.write_permission(foo='cmf.ModifyPortalContent')
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            qux = zope.schema.TextLine(title=u"Qux")
        
        self.assertEquals({'foo': 'some.dummy.Widget',
                           'baz': 'other.Widget'},
                          IDummy.queryTaggedValue(WIDGETS_KEY))
        self.assertEquals([(Interface, 'foo', 'true'),
                           (Interface, 'bar', 'true'),
                           (model.Schema, 'qux', 'true'),
                           (model.Schema, 'bar', 'false')],
                          IDummy.queryTaggedValue(OMITTED_KEY))
        self.assertEquals([(Interface, 'bar', 'hidden'),
                           (model.Schema, 'bar', 'input')],
                          IDummy.queryTaggedValue(MODES_KEY))
        self.assertEquals([('baz', 'before', 'title',),
                           ('qux', 'after', 'title')],
                          IDummy.queryTaggedValue(ORDER_KEY))
        self.assertEquals({'foo': 'zope2.View'},
                          IDummy.queryTaggedValue(READ_PERMISSIONS_KEY))
        self.assertEquals({'foo': 'cmf.ModifyPortalContent'},
                          IDummy.queryTaggedValue(WRITE_PERMISSIONS_KEY))
                                  
    def test_widget_supports_instances_and_strings(self):
        
        class IDummy(model.Schema):
            
            autoform.widget(foo=DummyWidget)
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            
        self.assertEquals({'foo': 'plone.autoform.tests.test_directives.DummyWidget'},
                  IDummy.queryTaggedValue(WIDGETS_KEY))
        
    def test_multiple_invocations(self):
        
        class IDummy(model.Schema):
            
            autoform.omit('foo')
            autoform.omit('bar')
            autoform.widget(foo='some.dummy.Widget')
            autoform.widget(baz='other.Widget')
            autoform.mode(bar='hidden')
            autoform.mode(foo='display')
            autoform.order_before(baz='title')
            autoform.order_after(baz='qux')
            autoform.order_after(qux='bar')
            autoform.order_before(foo='body')
            autoform.read_permission(foo='zope2.View', bar='zope2.View')
            autoform.read_permission(baz='random.Permission')
            autoform.write_permission(foo='cmf.ModifyPortalContent')
            autoform.write_permission(baz='another.Permission')
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            qux = zope.schema.TextLine(title=u"Qux")
        
        self.assertEquals({'foo': 'some.dummy.Widget',
                           'baz': 'other.Widget'},
                          IDummy.queryTaggedValue(WIDGETS_KEY))
        self.assertEquals([(Interface, 'foo', 'true'),
                           (Interface, 'bar', 'true')],
                          IDummy.queryTaggedValue(OMITTED_KEY))
        self.assertEquals([(Interface, 'bar', 'hidden'),
                           (Interface, 'foo', 'display')],
                          IDummy.queryTaggedValue(MODES_KEY))
        self.assertEquals([('baz', 'before', 'title'),
                           ('baz', 'after', 'qux'),
                           ('qux', 'after', 'bar'),
                           ('foo', 'before', 'body'),],
                          IDummy.queryTaggedValue(ORDER_KEY))
        self.assertEquals({'foo': 'zope2.View', 'bar': 'zope2.View', 'baz': 'random.Permission'},
                          IDummy.queryTaggedValue(READ_PERMISSIONS_KEY))
        self.assertEquals({'foo': 'cmf.ModifyPortalContent', 'baz': 'another.Permission'},
                          IDummy.queryTaggedValue(WRITE_PERMISSIONS_KEY))
    
    def test_misspelled_field(self):
        
        def bar():
            class IBar(model.Schema):
                autoform.order_before(ber='*')
                bar = zope.schema.TextLine()
        
        def baz():
            class IBaz(model.Schema):
                autoform.omit('buz')
                baz = zope.schema.TextLine()
            
        self.assertRaises(ValueError, bar)
        self.assertRaises(ValueError, baz)

    def test_derived_class_fields(self):
        
        class IFoo(model.Schema):
            foo = zope.schema.TextLine()
        
        class IBar(IFoo):
            autoform.order_after(foo='bar')
            bar = zope.schema.TextLine()
                
        self.assertEquals([('foo', 'after', 'bar'),], IBar.queryTaggedValue(ORDER_KEY))

                
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestAutoformDirectives),
        ))
