from django.http import HttpRequest
from django.test import TestCase
from django.urls import resolve

from lists.models import Item, List
from lists.views import home_page


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')


class NewListTest(TestCase):
    def test_can_save_a_post_request(self):
        item_text = 'A new list item'
        response = self.client.post('/lists/new', data={'item_text': item_text})

        self.assertEqual(Item.objects.count(), 1)

        new_item = Item.objects.first()
        self.assertEqual(new_item.text, item_text)

    def test_redirects_after_post(self):
        response = self.client.post('/lists/new', data={'item_text': 'A new list item'})
        list_ = List.objects.first()
        self.assertRedirects(response, f'/lists/{list_.id}/')

    def test_can_save_a_post_request_to_an_existing_list(self):
        list_ = List.objects.create()
        another_list = List.objects.create()

        self.client.post(f'/lists/{list_.id}/add_item', data={'item_text': 'A new item for an existing list'})

        self.assertEqual(Item.objects.count(), 1)
        item = Item.objects.first()
        self.assertEqual(item.text, 'A new item for an existing list')
        self.assertEqual(item.list, list_)

    def test_redirects_to_list_view(self):
        list_ = List.objects.create()
        another_list = List.objects.create()

        response = self.client.post(f'/lists/{list_.id}/add_item',
                                    data={'item_text': 'A new item for an existing list'})

        self.assertRedirects(response, f'/lists/{list_.id}/')


class ListAndItemModelTest(TestCase):
    def test_save_and_retrieve_items(self):
        list_ = List()
        list_.save()

        first_item = Item()
        first_item.text = 'The first item'
        first_item.list = list_
        first_item.save()

        second_item = Item()
        second_item.text = 'Item the second'
        second_item.list = list_
        second_item.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        self.assertEqual(first_saved_item.text, 'The first item')
        self.assertEqual(first_saved_item.list, list_)
        second_saved_item = saved_items[1]
        self.assertEqual(second_saved_item.text, 'Item the second')
        self.assertEqual(second_saved_item.list, list_)


class ListViewTest(TestCase):
    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        list_ = List.objects.create()
        Item.objects.create(text='itemey 1', list=list_)
        Item.objects.create(text='itemey 2', list=list_)
        another_list = List.objects.create()
        Item.objects.create(text='other itemey 1', list=another_list)
        Item.objects.create(text='other itemey 2', list=another_list)
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other itemey 1')
        self.assertNotContains(response, 'other itemey 2')

    def test_passes_correct_list_to_template(self):
        list_ = List.objects.create()
        other_list = List.objects.create()

        response = self.client.get(f'/lists/{list_.id}/')
        self.assertEqual(response.context['list'], list_)
