import re
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class Scraper(object):
    """Able to start up a browser, to authenticate to Instagram and get
    followers and people following a specific user."""


    def __init__(self, target):
        self.target = target
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1200, 800)


    def close(self):
        """Close the browser."""

        self.driver.close()


    def authenticate(self, username, password):
        """Log in to Instagram with the provided credentials."""

        print('\nLogging in…')
        self.driver.get('https://www.instagram.com')
        time.sleep(5)
        # Go to log in
        # login_link = WebDriverWait(self.driver, 10).until(
        #     EC.presence_of_element_located((By.LINK_TEXT, 'Log in'))
        # )
        # login_link= self.driver.find_element_by_link_text('Log in')
        login_link=  self.driver.find_element(By.TAG_NAME,'button' )
        time.sleep(5)

        # Authenticate
        # username_input = self.driver.find_element(By.XPATH,
        #     '//input[@placeholder="Username"]'
        # )
        username_input = self.driver.find_element(By.TAG_NAME,
            'input'
        )
        # password_input = self.driver.find_element(By.XPATH,
        #     '//input[@placeholder="Password"]'
        # )
        password_input = self.driver.find_element(By.XPATH,
                                                  '//input[@aria-label="Password"]'
                                                  )

        username_input.send_keys(username)
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)


    def get_users(self, group, verbose = False):
        """Return a list of links to the users profiles found."""

        self._open_dialog(self._get_link(group))

        print('\nGetting {} users…{}'.format(
            self.expected_number,
            '\n' if verbose else ''
        ))

        links = []
        last_user_index = 0
        updated_list = self._get_updated_user_list()
        initial_scrolling_speed = 5
        retry = 2

        # While there are more users scroll and save the results
        # while updated_list[last_user_index] is not updated_list[-1] and retry > 0:
        self._scroll(self.users_list_container, initial_scrolling_speed)


        for index, user in enumerate(updated_list):
            if index < last_user_index:
                continue

            try:
                link_to_user = user
                if(self._filter_user(link_to_user)):
                        link_to_user = link_to_user.get_attribute('href')
                else:
                    continue
                last_user_index = index
                if link_to_user not in links:
                    links.append(link_to_user)
                    if verbose:
                        print(
                            '{0:.2f}% {1:s}'.format(
                            round(index / self.expected_number * 100, 2),
                            link_to_user
                            )
                        )
            except:
                if (initial_scrolling_speed > 1):
                    initial_scrolling_speed -= 1
                pass
            self._scroll(self.users_list_container, initial_scrolling_speed)
            updated_list = self._get_updated_user_list()
            if updated_list[last_user_index] is updated_list[-1]:
                retry -= 1

        print('100% Complete')
        return links

    def get_follower_details(self, link, verbose = False):
        self.driver.get(link)
        time.sleep(3)
        details = {}
        header =self.driver.find_element(By.XPATH,
                                 '//header'
                                 ).text

        #print(header)
        email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', header)
        if email_match:
            details['email']= email_match.group(0)
        else:
            details = None
        return details

    def _open_dialog(self, link):
        """Open a specific dialog and identify the div containing the users
        list."""

        link.click()
        print(link.text)
        self.expected_number = int(
            re.search('(\d+)', link.text).group(1)
        )
        time.sleep(1)
        self.users_list_container = self.driver.find_element(By.XPATH,
                         '//div[@role="dialog"]'
                         )

    def _get_link(self, group):
        """Return the element linking to the users list dialog."""

        print('\nNavigating to %s profile…' % self.target)
        self.driver.get('https://www.instagram.com/%s/' % self.target)
        time.sleep(5)
        try:
            # elment = self.driver.find_element(By.PARTIAL_LINK_TEXT, group)
            filter =  "//div[contains(text(), '{}')]".format(group)
            return self.driver.find_element(By.XPATH, filter)
            time.sleep(3)
        except:
            if group == 'followers':
                group = 'follower'
            self._get_link(group)


    def _filter_user(self, x):

         return x.get_attribute("href").replace("https://www.instagram.com/", "") not in ['','reels/videos/', 'explore/'] and x.text == x.get_attribute("href").split("/")[
             -1] and "/p/" not in x.get_attribute("href")

    def _get_updated_user_list(self):
        """Return all the list items included in the users list."""
        user_list = self.users_list_container.find_elements(By.XPATH, '//a[@role="link"]')
        return user_list


    def _scroll(self, element, times = 1):
        """Scroll a specific element one or more times with small delay between
        them."""

        while times > 0:
            self.driver.execute_script(
                'arguments[0].scrollTop = arguments[0].scrollHeight',
                element
            )
            time.sleep(.2)
            times -= 1
