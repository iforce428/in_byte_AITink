import re
# from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PIL import Image
from io import BytesIO

import numpy as np
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time

load_dotenv()

linkedin_id = os.environ['LINKEDIN_ID']
linkedin_pw = os.environ['LINKEDIN_PW']

linkedin_xpath_dict = {'username': {"xpath": '//input[@id="username"]',
                                    'value': linkedin_id},
                       'password': {'xpath': '//input[@id="password"]',
                                    'value': linkedin_pw},
                       'signin_btn': {'xpath': '//button[@data-litms-control-urn="login-submit"]'},
                       'see_more_link': {'xpath': "//button[contains(@class, 'inline-show-more-text__button')]"},
                       'view_experiences': {'xpath': '//a[@id="navigation-index-see-all-experiences"]'},
                       'view_educations': {'xpath': '//a[@id="navigation-index-see-all-education"]'},
                       'sticky_bar': {'xpath': "//section[contains(@class, 'scaffold-layout-toolbar') and contains(@class, 'scaffold-layout-toolbar--is-fixed') and contains(@class, 'scaffold-layout-toolbar--is-fixed-visible')]"}
}

linkedin_urls = [
    "https://www.linkedin.com/in/addis-olujohungbe/",
    "https://www.linkedin.com/in/sharanjm"
]

priority_sections = ['About', 'Activity', 'Experience', 'Education']    # , 'Licenses & certifications', 'Projects', 'Skills', 'Recommendations', '']

os.mkdir('merged_images')

url = 'https://www.linkedin.com/feed/'

chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')

driver = webdriver.Chrome(service = Service(), options=chrome_options)
driver.get(url)
driver.maximize_window()
wait = WebDriverWait(driver, 20)

driver.find_element(By.XPATH, linkedin_xpath_dict['username']['xpath']).send_keys(linkedin_xpath_dict['username']['value'])
time.sleep(1)

driver.find_element(By.XPATH, linkedin_xpath_dict['password']['xpath']).send_keys(linkedin_xpath_dict['password']['value'])
time.sleep(1)

# Click sign in
driver.find_element(By.XPATH, linkedin_xpath_dict['signin_btn']['xpath']).click()
time.sleep(2)

def stitch_img(folderpath):
    list_images = os.listdir(folderpath)

    images = []

    for item in list_images:
        img = Image.open(os.path.join(folderpath, item))
        images.append(img)

    # Determine the maximum width
    max_width = max(img.width for img in images)
    total_height = sum(img.height for img in images)

    # Create a new image with white background and combined height
    merged_img = Image.new('RGB', (max_width, total_height), color='white')

    # Paste images, padding with white if needed
    y_offset = 0
    for img in images:
        padded_img = Image.new('RGB', (max_width, img.height), color='white')
        padded_img.paste(img, (0, 0))  # paste left-aligned
        merged_img.paste(padded_img, (0, y_offset))
        y_offset += img.height

    # Save the final merged image
    merged_img.save(os.path.join('merged_images', f"{folderpath}_merged_screenshots_cropped_padded.png"))



# Iterate through provided LinkedIn URLs
for url in linkedin_urls:
    # Pattern search with regex
    content = re.search(r'https://www.linkedin.com/in/(.*)', url)
    
    # Get user LinkedIn account name
    acc_name = content.group(1)
    
    if not os.path.exists(acc_name):
        # Make dedicated folder for user
        os.mkdir(acc_name)

        # Navigate to respective LinkedIn user page
        driver.get(url)
        time.sleep(3)

        # Click on all 'see more' links in separate sections
        section_elements = driver.find_elements(By.TAG_NAME, 'section')
        driver.execute_script("document.body.style.zoom='75%'")

        counter = 0
        for i, element in enumerate(section_elements[2:]):
            if counter >= 4:
                break
            else:

                # see_more = element.find_elements(By.XPATH, linkedin_xpath_dict['see_more_link']['xpath'])
                # if see_more:
                #     see_more[0].click()
                # else:
                #     pass

                keyword = [word for word in priority_sections if word in element.text]

                
                if len(keyword) == 1:
                    # Position on the page (relative to the top-left corner)
                    position = element.location  # returns {'x': value, 'y': value}

                    # Size of the element (width and height in pixels)
                    size = element.size  # returns {'height': value, 'width': value}

                    # device_pixel_ratio = driver.execute_script("return window.devicePixelRatio;")
                    device_pixel_ratio = 1.75

                    # Combine into a bounding box
                    bounding_box = {
                        'x': int(position['x']),
                        'y': int(position['y']),
                        'width': int(size['width'] * device_pixel_ratio),
                        'height': int(size['height'] * device_pixel_ratio)
                    }

                    print(bounding_box)

                    # Scroll to specific location
                    driver.execute_script(f"window.scrollTo({0}, {bounding_box['y']-100});")
                    time.sleep(3)
                    print(element)

                    content_bytes = driver.get_screenshot_as_png()
                    # content_bytes = element.screenshot_as_png

                    with open(os.path.join(acc_name,f"sample_img{i}.png"), 'wb') as f:
                        f.write(content_bytes)

                    image = Image.open(os.path.join(acc_name,f"sample_img{i}.png"))

                    # Define the bounding box: (left, upper, right, lower)
                    bbox = (bounding_box['x']*device_pixel_ratio, 200, bounding_box['width']+400, bounding_box['height'])

                    # Crop the image
                    cropped_image = image.crop(bbox)

                    # Save the cropped image
                    cropped_image.save(os.path.join(acc_name,f"sample_img{i}.png"))
                    counter += 1
                    # image = Image.open(f"sample_img{i}.png")  # Replace with your actual image filename

                    # # Define the bounding box: (left, upper, right, lower)
                    # bbox = (bounding_box['x'],
                    #         bounding_box['y'], 
                    #         bounding_box['x'] + bounding_box['width'], 
                    #         bounding_box['y'] + bounding_box['height'])

                    # # Crop the image
                    # cropped_image = image.crop(bbox)

                    # # Save the cropped image
                    # cropped_image.save(f"cropped_output{i}.png")

                    # Wait until sticky bar is present on scroll and hide with JS
                    # element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, linkedin_xpath_dict['sticky_bar']['xpath'])))
                    # driver.execute_script("arguments[0].style.display = 'none';", element)
                    # time.sleep(1)

        stitch_img(acc_name.replace('/',''))

    else:
        print('Screenshots already recorded.')

driver.quit()