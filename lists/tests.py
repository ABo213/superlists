from django.http import HttpRequest
from django.test import TestCase
from django.urls import resolve

from lists.models import Item
from lists.views import home_page


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_can_save_a_post_request(self):
        item_text = 'A new list item'
        response = self.client.post('/', data={'item_text': item_text})
        self.assertIn(item_text, response.content.decode())
        self.assertTemplateUsed(response, 'home.html')


class ItemModelTest(TestCase):
    def test_save_and_retrieve_items(self):
        first_item = Item()
        first_item.text = 'The first item'
        first_item.save()

        second_item = Item()
        second_item.text = 'Item the second'
        second_item.save()

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        self.assertEqual(first_saved_item.text, 'The first item')
        second_saved_item = saved_items[1]
        self.assertEqual(second_saved_item.text, 'Item the second')
