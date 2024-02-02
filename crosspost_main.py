from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import Select

from datetime import datetime, timedelta
import sys, random, pdb, time
from dotenv import load_dotenv
import os
load_dotenv()

#This will be the backend of the bot. Let's just get it working first, then worry about the GUI later.

#STEPS:
#Figure out what user input is needed from Poshmark and Kidizen
#Get the input from the user
#Post to Kidizen, Post to Posh

#Sell links:
#Kidizen: https://www.kidizen.com/items/new
#Poshmark: https://poshmark.com/create-listing

#INPUTS:
#Kidizen: Title, Photos, Category, Subcategory, Gender (Male, Female, All), Size, Brand, Condition, Description, Shipping, Price (list and original MSRP)
#Poshmark: Photos, Title, Description, Category, Subcategory, Quantity, Size, New with tags?, Brand, Color, Style Tags, Shipping, Price (list and original MSRP)

#Let's make a dummy input, then go on to user input

#Make a listing class
class Listing:
    def __init__(self, title, photos, category, subcategory, gender, quantity, size, brand, condition, new_with_tags, description, shipping, list_price, original_msrp, color, style_tags):
        self.title = title
        self.photos = photos
        self.category = category
        self.subcategory = subcategory
        self.gender = gender
        self.quantity = quantity
        self.size = size
        self.brand = brand
        self.condition = condition
        self.new_with_tags = new_with_tags
        self.description = description
        self.shipping = shipping
        self.list_price = list_price
        self.original_msrp = original_msrp
        self.color = color
        self.style_tags = style_tags

class KidizenForm:
    def __init__(self, debug = False):
        self.username = os.getenv("KIDIZEN_USERNAME")
        self.password = os.getenv("KIDIZEN_PASSWORD")
        self.chrome_options = Options()
        #self.chrome_options.add_argument("--headless")
        #self.chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(options = self.chrome_options)
        self.loginUrl = "https://www.kidizen.com/login"
        self.loginID = "session_email"
        self.loginXPath = '//*[@id="session_email"]'
        self.passwordID = "session_password"
        self.passwordXPath = '//*[@id="session_password"]' 
        self.newPostUrl = "https://www.kidizen.com/items/new"
        self.titleXPath = '//*[@id="item_title"]'
        self.photosXPath = '//*[@id="new_item"]/div[2]/div[2]/label/div'
        self.categoryXPath = '//*[@id="new_item"]/div[3]/div[1]'
        self.categoryOptions = ['Kid Clothing', 'Kid Shoes', 'Kid Accessories', 'Children\'s Books & Toys', 
                                'Baby Essentials', 'Diaper Bags & Carriers', 'Children\'s Room and Nursery', 
                                'Maternity', 'Mama Clothing', 'Mama Accessories', 'Mama Essentials', 'Not For Sale']
        self.subcategoryXPath = '//*[@id="new_item"]/div[4]/div[2]/select'
        self.subcategoryOptions = ['Tops & Tees', 'Sweaters & Sweatshirts', 'Jeans', 'Pants', 
                                   'Leggings', 'Shorts', 'Dresses', 'Formal Dresses', 'Skirts', 
                                   'Outfits & Bundles', 'Rompers & Overalls', 'Onesies', 
                                   'Outerwear', 'Activewear', 'Dancewear & Gymnastics', 'Swim',
                                'Sleepwear', 'Suits', 'Undergarments', 'Costumes', 'Other']
        self.genderXPath = '//*[@id="new_item"]/div[5]/div[2]/select' 
        self.genderOptions = ['Male', 'Female', 'All genders']
        self.sizeXPath = '//*[@id="new_item"]/div[6]/div[1]/div[2]'
        self.sizeOptions = {
                            "Baby": ["preemie", "nb", "0-3 mo", "3-6 mo", "6-12 mo", "12-18 mo", "18-24 mo", "One Size"],
                            "Toddler": ["2", "2T", "3", "3T", "4", "4T", "One Size"],
                            "Little Kid": ["5", "5T", "6", "7", "XXS", "XS", "S", "One Size"],
                            "Big Kid": ["8", "9", "10", "11", "12", "13", "14", "16+", "M", "L", "XL", "XXL", "One Size"]
        }
        self.brandXPath = '//*[@id="new_item"]/div[7]/div[2]/input'
        self.conditionXPath = '//*[@id="new_item"]/div[8]/div[2]/select'
        self.conditionOptions = ['New with tag', 'New without tag', 'Excellent used condition', 
                                 'Very good used condition', 'Good used condition', 'Play condition']
        self.descriptionXPath = '//*[@id="item_description"]'
        self.shippingOptionsXPath = {
            'small' : '//*[@id="new_item"]/div[12]/div[1]/div',
            'medium' : '//*[@id="new_item"]/div[12]/div[2]/div',
            'large' : '//*[@id="new_item"]/div[12]/div[3]/div',
        }
        self.listPriceXPath = '//*[@id="item_list_price"]'
        self.originalMsrpXPath = '//*[@id="item_msrp"]'

        self.debug = debug
        self.timeOutSecs = 10
        self.scrollWaitTime = 5

    #Exits the driver
    def quit(self):   
        self.driver.quit()

    #Enters text slowly, to avoid being flagged as a bot
    def enterTxtSlowly(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.random())

    #Waits until an element is clickable, then returns it
    def waitTillClickable(self, findByIdOrPath, idOrPath, timeOutSecs = 10):
        clickableElement = False
        if findByIdOrPath == 'id':
            try:
                clickableElement = WebDriverWait(self.driver, timeOutSecs).until(EC.element_to_be_clickable((By.ID, idOrPath)))
            except TimeoutException as e:
                print("Timed out at locating element by " + findByIdOrPath + " at " + str(idOrPath) + ": " + str(e))
                return False
        else:
            try:
                clickableElement = WebDriverWait(self.driver, timeOutSecs).until(EC.element_to_be_clickable((By.XPATH, idOrPath)))
            except TimeoutException as e:
                print("Timed out at locating element by " + findByIdOrPath + " at " + str(idOrPath) + ": " + str(e))
                return False
        return clickableElement

    #Waits until an element is present, then returns it
    def waitForAnElementByXPath(self, xpath, elementName):
        try:
            element = WebDriverWait(self.driver, self.timeOutSecs).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException as e:
            print("Timed out while waiting for " + elementName + " to pop up..waiting again")
            print(e)
            return False
        return element
    
    def clickAButton(self, button):
      try:
         self.driver.execute_script("arguments[0].click();", button)
      except Exception as e:
         print("clicking button failed: " + str(e))

    #Scroll one page down
    def scrollDown(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(self.scrollWaitTime)
        print("Scrolling")
    
    #Looks for login field by ID, then xpath if not found
    def getLogInElement(self, elementID, elementXPath):
        element = self.waitTillClickable("id", elementID)
        if not element:
            print("Time out at locating ID: " + elementID)
            element = self.waitTillClickable("xpath", elementXPath)
            if not element:
                print("Timed out again with xpath")
                print("Please manually enter username/password, then type 'c' or 'continue'")
                pdb.set_trace()
        return element   

    def enterUserName(self):
        userNameElement = self.getLogInElement(self.loginID, self.loginXPath)
        if not userNameElement:
            print("Username element not obtained from page, exiting...")
            self.quit()
            sys.exit() 
        self.enterTxtSlowly(userNameElement, self.username)

    def enterAndSubmitPassword(self):
        passwordElement = self.getLogInElement(self.passwordID, self.passwordXPath)
        if not passwordElement:
            print("Password element not obtained from page, exiting...")
            self.quit()
            sys.exit()
        self.enterTxtSlowly(passwordElement, self.password)
        passwordElement.submit()
            
    def login(self): 
        self.driver.get(self.loginUrl)      
        self.enterUserName()
        self.enterAndSubmitPassword()
        if self.debug:  
            print(self.driver.title)
        print("Logged in successfully")
    
    def selectDropdownOption(self, dropdownElement, option):
        print("Selecting option: " + option)

    def post_listing(self, listing):
        #Go to new post page
        self.driver.get(self.newPostUrl)

        #Enter title
        titleElement = self.waitTillClickable("xpath", self.titleXPath)
        if not titleElement:
            print("Timed out at locating title element")
            self.quit()
            sys.exit()
        self.enterTxtSlowly(titleElement, listing.title)

        #Enter photos
        #NOTE: This button is looking for a filepath, so we can just send the filepath
        #rather than going through the file explorer
        photo_input = self.waitForAnElementByXPath('//input[@type="file"]', "file input")
        if not photo_input:
            print("Timed out at locating photos element")
            self.quit()
            sys.exit()
        for photo in listing.photos:
            file_path = photo
            photo_input.send_keys(file_path)
       

        print('Maybe it worked?') 
        time.sleep(5) 
        





        
   
#Start by defining variables
#In the future this will be taken from the GUI
def create_listing():
    title = "Test Title"
    photos = [r".\stock1.jpg", r".\stock2.jpeg"]
    category = "Kid Shoes"
    subcategory = "Casual"
    gender = "Female"
    brand = "Test Brand"
    condition =  "Like New"
    new_with_tags = "No"
    description = "Test Description"
    shipping = 'Option 1'
    list_price = "10"
    original_msrp = "20"
    color = "Blue"
    style_tags = "Casual"

    listing = Listing(title, photos, category, subcategory, gender, quantity, size, brand, condition, new_with_tags, description, shipping, list_price, original_msrp, color, style_tags)

    return listing



listing = create_listing()

#Post to Kidizen
kidizen_form = KidizenForm()
kidizen_form.login()
kidizen_form.post_listing(listing)
kidizen_form.quit()
