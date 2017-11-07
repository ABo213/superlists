import time
import unittest

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common import keys

MAX_WAIT_SECOND = 10


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):
        self.browser.get(self.live_server_url)
        self.assertIn('To-Do', self.browser.title)

        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        input_box = self.browser.find_element_by_id('new_item')
        self.assertEqual(input_box.get_attribute('placeholder'), 'Enter a to-do item')

        input_box.send_keys('Buy peacock feathers')
        input_box.send_keys(keys.Keys.ENTER)
        self._wait_and_check_for_row_in_list_table('1: Buy peacock feathers')

        input_box = self.browser.find_element_by_id('new_item')
        input_box.send_keys('Use peacock feathers to make a fly')
        input_box.send_keys(keys.Keys.ENTER)
        self._wait_and_check_for_row_in_list_table('1: Buy peacock feathers')
        self._wait_and_check_for_row_in_list_table('2: Use peacock feathers to make a fly')

        self.fail('Finish the test!')

    def _wait_and_check_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id('list_table')
                rows = table.find_elements_by_tag_name('tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() > start_time + MAX_WAIT_SECOND:
                    raise e
                time.sleep(0.5)