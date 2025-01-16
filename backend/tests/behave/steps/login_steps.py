from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

@given("I am on the post creation page")
def step_go_to_post_creation(context):
    context.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    context.driver.get("http://localhost:3000")  # Deine App-URL

@when('I select "{post_type}" as the post type')
def step_select_post_type(context, post_type):
    dropdown = context.driver.find_element(By.ID, "postType")  # Verwendet die ID "postType"
    dropdown.send_keys(post_type)

@when('I enter "{caption}" as the caption')
def step_enter_caption(context, caption):
    caption_input = context.driver.find_element(By.ID, "caption")  # Verwendet die ID "caption"
    caption_input.send_keys(caption)

@when('I enter "{hashtags}" as the hashtags')
def step_enter_hashtags(context, hashtags):
    hashtags_input = context.driver.find_element(By.ID, "hashtags")  # Verwendet die ID "hashtags"
    hashtags_input.send_keys(hashtags)

@when('I upload a file "{file_path}"')
def step_upload_file(context, file_path):
    file_input = context.driver.find_element(By.ID, "media")  # Verwendet die ID "media"
    file_input.send_keys(file_path)

@when("I click the upload button")
def step_click_upload_button(context):
    upload_button = context.driver.find_element(By.ID, "uploadButton")  # Verwendet die ID "uploadButton"
    upload_button.click()

@then("I should see a success message")
def step_verify_success_message(context):
    success_message = context.driver.find_element(By.XPATH, "//p")  # Prüft eine Nachricht
    assert "Post uploaded successfully" in success_message.text
    context.driver.quit()  # Schließt den Browser nach dem Test
