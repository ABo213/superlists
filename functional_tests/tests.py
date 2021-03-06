from selenium import webdriver
from selenium.webdriver.common import keys

from functional_tests.base import FunctionalTest


class NewVisitorTest(FunctionalTest):
    def test_one_user_can_start_a_list_and_retrieve_it_later(self):
        self.browser.get(self.live_server_url)
        self.assertIn('To-Do', self.browser.title)

        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        input_box = self.browser.find_element_by_id('id_text')
        self.assertEqual(input_box.get_attribute('placeholder'), 'Enter a to-do item')

        input_box.send_keys('Buy peacock feathers')
        input_box.send_keys(keys.Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy peacock feathers')

        input_box = self.browser.find_element_by_id('id_text')
        input_box.send_keys('Use peacock feathers to make a fly')
        input_box.send_keys(keys.Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy peacock feathers')
        self.wait_for_row_in_list_table('2: Use peacock feathers to make a fly')

    def test_multiple_user_can_start_lists_at_different_urls(self):
        self.browser.get(self.live_server_url)
        input_box = self.browser.find_element_by_id('id_text')
        input_box.send_keys('Buy peacock feathers')
        input_box.send_keys(keys.Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy peacock feathers')

        ones_list_url = self.browser.current_url
        self.assertRegex(ones_list_url, '/lists/.+')

        self.browser.quit()
        self.browser = webdriver.Chrome()

        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)

        input_box = self.browser.find_element_by_id('id_text')
        input_box.send_keys('Buy milk')
        input_box.send_keys(keys.Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')

        others_list_url = self.browser.current_url
        self.assertRegex(others_list_url, '/lists/.+')
        self.assertNotEqual(others_list_url, ones_list_url)

        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertIn('Buy milk', page_text)


class LayoutAndStylingTest(FunctionalTest):
    def test_layout_and_styling(self):
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(480, 360)
        input_box = self.browser.find_element_by_id('id_text')
        self.assertAlmostEqual(input_box.location['x'] + input_box.size['width'] / 2, 240, delta=10)

        input_box.send_keys('testing')
        input_box.send_keys(keys.Keys.ENTER)
        self.wait_for_row_in_list_table('1: testing')
        input_box = self.browser.find_element_by_id('id_text')
        self.assertAlmostEqual(
            input_box.location['x'] + input_box.size['width'] / 2,
            240,
            delta=10
        )


class ItemValidationTest(FunctionalTest):
    def test_cannot_add_emtpy_items(self):
        self.browser.get(self.live_server_url)
        self.get_item_input_box().send_keys(keys.Keys.ENTER)

        self.wait_for(lambda: self.browser.find_element_by_css_selector('#id_text:invalid'))

        self.get_item_input_box().send_keys('Buy milk')
        self.wait_for(lambda: self.browser.find_element_by_css_selector('#id_text:valid'))
        self.get_item_input_box().send_keys(keys.Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')

        self.get_item_input_box().send_keys(keys.Keys.ENTER)
        self.wait_for(lambda: self.browser.find_element_by_css_selector('#id_text:invalid'))

        self.get_item_input_box().send_keys('Make tea')
        self.wait_for(lambda: self.browser.find_element_by_css_selector('#id_text:valid'))
        self.get_item_input_box().send_keys(keys.Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')
        self.wait_for_row_in_list_table('2: Make tea')

    def test_cannot_add_duplicate_items(self):
        self.browser.get(self.live_server_url)
        self.get_item_input_box().send_keys('Buy wellies')
        self.get_item_input_box().send_keys(keys.Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy wellies')

        self.get_item_input_box().send_keys('Buy wellies')
        self.get_item_input_box().send_keys(keys.Keys.ENTER)
        self.wait_for(lambda: self.assertEqual(
            self.get_error_element().text, "You've already got this in your list"
        ))

    def test_error_messages_are_cleared_on_input(self):
        self.browser.get(self.live_server_url)
        self.get_item_input_box().send_keys('Banter too thick')
        self.get_item_input_box().send_keys(keys.Keys.ENTER)
        self.wait_for_row_in_list_table('1: Banter too thick')

        self.get_item_input_box().send_keys('Banter too thick')
        self.get_item_input_box().send_keys(keys.Keys.ENTER)
        self.wait_for(lambda: self.assertTrue(self.get_error_element().is_displayed()))

        self.get_item_input_box().send_keys('a')
        self.wait_for(lambda: self.assertFalse(self.get_error_element().is_displayed()))

    def get_error_element(self):
        return self.browser.find_element_by_class_name('errorlist')
