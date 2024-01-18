from django.test import LiveServerTestCase, TestCase, override_settings
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


from django.template.loader import render_to_string
from django.core import mail
import time
import json




@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
class Hosttest(LiveServerTestCase):
    def test_depublishPosts(self):
        html = render_to_string('emails/email_delisted.html')

        with open('logins.json', 'r') as f:
            logins = json.load(f)

        for login in logins:
            driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())

            driver.get('https://www.sbazar.cz/admin/moje-inzeraty/zverejnene')

            original_window = driver.current_window_handle

            driver.implicitly_wait(3) # waits for 5 seconds

            # Find the first button and click it
            button = driver.find_element_by_xpath('//button[text()="Přihlásit se"]')
            button.click()

            # Wait for the login page to load
            driver.implicitly_wait(5)

            # Switch to the popup window
            driver.switch_to.window(driver.window_handles[1])

            driver.implicitly_wait(3) # waits for 3 seconds

            # Find the username field and enter your username
            username_field = driver.find_element_by_id('login-username')
            username_field.send_keys(login['username'])

            # Find the Continue button and click it
            continue_button = driver.find_element_by_xpath('//button[@data-locale="login.submit"]')
            continue_button.click()

            # Wait for the password field to appear
            driver.implicitly_wait(1)

            # Find the password field and enter your password
            password_field = driver.find_element_by_id('login-password')
            password_field.send_keys(login['password'])

            # Find the Sign in button and click it
            sign_in_button = driver.find_element_by_xpath('//button[@data-locale="login.submit"]')
            sign_in_button.click()

            time.sleep(1)

            driver.switch_to.window(original_window)

            driver.refresh()
            time.sleep(1)

            # Check for the presence of a warning popup and close it if it appears
            try:
                warning_popup = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="c-fraud__popup c-popup c-popup--z-index-level-third c-popup-dialog c-popup-dialog--open c-popup-dialog--z-index-level-third"]'))
                )
                close_button = warning_popup.find_element_by_xpath('.//button[@class="c-popup__closer"]')
                close_button.click()
            except:
                pass

            #Redirect to the active page
            #Make the posts unlisted
            #Relist them again
            #Run this for 14 days
            

            # Initialize the counter for the number of iterations
            iteration_count = 0

            # Get the initial number of items
            initial_item_count = len(driver.find_elements_by_xpath('//li[@class="c-item c-item--ca"]'))
            print(f'Initial item count: {initial_item_count}')

            # Iterate over each page in the grid
            while initial_item_count > 0:
                # Refresh the page after 30 iterations
                if iteration_count >= 30:
                    print('Refreshing the page...')
                    driver.refresh()
                    iteration_count = 0

                    driver.implicitly_wait(5)
                    # Re-fetch the number of items after the refresh
                    initial_item_count = len(driver.find_elements_by_xpath('//li[@class="c-item c-item--ca"]'))
                    print(f'Updated item count after refresh: {initial_item_count}')

                # Wait for the page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//li[@class="c-item c-item--ca"]'))
                )

                # Refresh the list of items
                items = driver.find_elements_by_xpath('//li[@class="c-item c-item--ca"]')

                # Get the current item
                item = items[0]
                print(f'Processing item {iteration_count + 1} of {initial_item_count}')

                dots_button = item.find_element_by_xpath('.//button[@class="c-item__actions"]')

                # Check if the button is visible
                if dots_button.is_displayed():
                    print("The button is visible")
                else:
                    print("The button is not visible")

                dots_button.click()

                time.sleep(2)

                print('Button with dots found')

                # Wait for the menu to appear
                WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, './/div[@class="c-popup__box c-popup-dialog__box"]'))
                )
                print('Menu appeared')

                # Find the desired button in the menu and click it
                menu_button = item.find_element_by_xpath('//button[.//img[@src="/static/img/deactivate.svg"]]')
                menu_button.click()
                
                time.sleep(1)

                reason_button = item.find_element_by_xpath('//button[.//img[@src="/static/img/envelope-no-report.svg"]]')
                reason_button.click()

                print('Simulated a click on an item')

                # Decrement the initial_item_count
                initial_item_count -= 1
                print(f'Remaining items: {initial_item_count}')

                # Increment the iteration_count
                iteration_count += 1
                print(f'Iteration count: {iteration_count}')

                time.sleep(1)
            driver.close()

        print("Since this print shows, it means that the code below should run and is in the correct block")
        
        
        # SUBJECT, MESSAGE, SENDER_EMAIL, RECIPIENT, HTML
        #mail.send_mail('VW Audi Inzeráty', 'This is the message', 'vwaudi.cz@gmail.com', ['petrmalecek@systexo.com'], html_message=html) # SUBJECT, MESSAGE, SENDER_EMAIL, RECIPIENT, HTML
        
        email = mail.EmailMessage(
            '[DEAKTIVACE] VW Audi Inzeráty', 
            html, 
            'vwaudi.cz@gmail.com', 
            ['hermanx@email.cz'], 
            cc=['petrmalecek@systexo.com'],
        )
        email.content_subtype = "html"  # You need this line to send HTML content
        email.send()

        time.sleep(2)


