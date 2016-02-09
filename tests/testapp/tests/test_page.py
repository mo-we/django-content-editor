from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import User
from django.test import TestCase
# from django.utils import timezone

try:
    from django.urls import reverse
except ImportError:  # pragma: no cover
    from django.core.urlresolvers import reverse

from content_editor.models import ContentProxy

from testapp.models import Article, RichText, Download


class ContentEditorTest(TestCase):
    def setUp(self):
        u = User(
            username='test',
            is_active=True,
            is_staff=True,
            is_superuser=True)
        u.set_password('test')
        u.save()

    def login(self):
        self.assertTrue(self.client.login(username='test', password='test'))

    def test_stuff(self):
        # Smoke test some stuff
        article = Article.objects.create(
            title='Test',
        )
        article.testapp_richtext_set.create(
            text='<p>bla</p>',
            region='main',
            ordering=10,
        )

        with self.assertNumQueries(2):  # Two content types.
            content = ContentProxy(article, plugins=[RichText, Download])

        self.assertEqual(len(content.main), 1)
        self.assertEqual(len(content.sidebar), 0)
        self.assertRaises(AttributeError, lambda: content.bla)

        response = self.client.get(article.get_absolute_url())
        self.assertContains(response, '<h1>Test</h1>')
        self.assertContains(response, '<p>bla</p>')

    def test_admin(self):
        self.login()
        response = self.client.get(reverse('admin:testapp_article_add'))

        self.assertContains(response, 'content-editor-script', 1)
        self.assertContains(response, 'class="richtext"', 1)
