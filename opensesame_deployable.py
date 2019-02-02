'''
Deployable version of opensesame. Intended to be compiled into an executable, and manually triggered via other programs
or macros. An example use is if somebody knocks on your door, and you don't want to get up to open it, they can simply
enter your pin after you run this program (connecting it to a keyboard macro, for example, would work great for this
application). This is of course intended to be used with people that you trust and who frequently visit your dorm room.

Original description:
Unlocks dorm room door, so only a pin is required. In order to normally get into a room, you have to put your RFID
ID up against the lock, and then punch in your PIN #. Unfortunately, the mobile online "unlock my door" function only
skips the RFID part, the user then still has to punch in the PIN code. This is still useful, since now you don't need
your ID on you to get into your room, but a more convenient (and less secure) solution may involve using a stepper motor
on the inside of the door to pull the door handle. This solution may possibly be implemented in the future.
'''
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import os
import pickle
import playsound

opts = Options()
opts.add_argument("user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/70.0.3538.102 Mobile Safari/537.36")

def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

sound = True

assure_path_exists(os.path.expanduser('~')+"/Documents/opensesame")

with open(os.path.expanduser('~')+"/Documents/opensesame/userinfo.txt", "r") as file:
    data = file.readline()
dataList = data.split(',')
try:
    if(dataList[2] == 'False' or dataList[2] == 'false'):
        sound = False
    if(dataList[3] == 'False' or dataList[3] == 'false'):
        opts.add_argument("--headless")
except:
    print('Extra options may not have been included in the file userinfo.txt')

driver = webdriver.Chrome(executable_path=os.path.expanduser('~')+"/Documents/opensesame/resources/chromedriver.exe", chrome_options=opts)
driver.set_window_size(300,500)

def instantLogin():
    """
    Attempts to instantly login if one of the following is true:
    (1) - driver window is already open and logged into the "open my door" page
    (2) - updated cookies (within 7 days) exist and can be used
    :return: True if either method works
    """
    try:
        try: # in case method fbiOpenUp is called again while still open
            driver.find_element_by_xpath("//*[@id='content']/div[2]/div/div/div/form[1]/ul/li/input[3]").click()
            print("Door opened via instantLogin - click")
            return True
        except: # in case method fbiOpenUp first time called, but cookies up to date
            driver.get("https://csg-web1.eservices.virginia.edu/login/")
            if os.path.isfile(os.path.expanduser('~')+"/Documents/opensesame/resources/cookies.pkl"):
                cookies = pickle.load(open(os.path.expanduser('~')+"/Documents/opensesame/resources/cookies.pkl", "rb"))
                for cookie in cookies:
                    driver.add_cookie(cookie)
            driver.find_element_by_xpath('//*[@id="content"]/div[2]/a').click()
            driver.find_element_by_xpath('//*[@id="mmenu"]/div[2]/table/tbody/tr[1]/td[2]/a').click()
            driver.find_element_by_xpath("//*[@id='content']/div[2]/div/div/div/form[1]/ul/li/input[3]").click()
            print("Door opened via instantLogin - cookies")
            return True
    except:
        return False


def initialLogin(username, password):
    """
    The first step in the process of logging in. Send the username and password to the UVa Netbadge system.
    :param username: username of the user
    :param password: password of the user
    :return: True once done
    """
    driver.get("https://csg-web1.eservices.virginia.edu/login/")
    driver.find_element_by_xpath('//*[@id="content"]/div[2]/a').click()
    driver.find_element_by_xpath('//*[@id="user"]').send_keys(username)
    driver.find_element_by_xpath('//*[@id="pass"]').send_keys(password)
    driver.find_element_by_xpath('/html/body/main/div[2]/fieldset/form/input').click()
    return True

def duoConfirm():
    """
    Attempts to send a DUO push confirmation to the user's phone. Netbadge times this process out after three
    minutes, after which the whole automation must rerun to get to this point again.
    :return: True if DUO confirmed, False if not
    """
    minutes = 0
    while minutes <= 2: # Netbadge times out DUO confirmation after three minutes
        try:
            driver.switch_to_frame(driver.find_element_by_xpath('//*[@id="duo_iframe"]'))
            driver.find_element_by_xpath('//*[@id="login-form"]/div/div/label/input').click()
            driver.find_element_by_xpath('//*[@id="login-form"]/fieldset[2]/div[1]/button').click()
            driver.switch_to_default_content()
            myElem = WebDriverWait(driver, 60).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="mmenu"]/div[2]/table/tbody/tr[1]/td[2]/a')))
            return True
        except:
            print("Error! DUO Push not confirmed! Attempting to retry!")
            minutes += 1
    return False

def fbiOpenUp(username, password):
    '''
    Automated script that runs through Chrome to access the "unlock my door" page for UVa dorms.
    Due to the fact that the page only opens on mobile devices, the user-agent of an Android is used.
    This function returns True if the door was unlocked (in other words, only the PIN is now needed to enter).
    Due to 2-step verification through an app called DUO, every 7 days the user must manually confirm the login of
    the program. A possible solution may be to emulate an Android OS on desktop with a script that will always
    accept the 2-step verification push.
    :param username: username used for Netbadge login
    :param password: password used for Netbadge login
    :return: True if door unlocked
    '''

    if(sound):
        playsound.playsound(os.path.expanduser('~')+"/Documents/opensesame/resources/beepLow.wav") # initial beep for recognition in, for example, the facial recognition thing.

    while True:
        if instantLogin() == True:
            doorOpened()
            return True

        initialLogin(username, password)

        driver.switch_to_frame(driver.find_element_by_xpath('//*[@id="duo_iframe"]'))
        try:
            WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="login-form"]/fieldset[2]/div[1]/button')))
        except:
            print("Timeout! Netbadge login took too long to show DUO frame!")
            return False
        driver.switch_to_default_content()

        if duoConfirm() == True: # only finish the automation if DUO confirmed, otherwise, restart whole process
            driver.get('https://csg-web1.eservices.virginia.edu/student/openmydoor.php')
            driver.find_element_by_xpath('//*[@id="content"]/div[2]/div/div/div/form[1]/ul/li/input[3]').click()

            doorOpened()
            return True

def doorOpened():
    """
    Prints a debugging door opened confirmation and plays a beep so the person attempting to enter the room knows when
    to input their pin number.
    Saves cookies for next time.
    :return: True if function finishes successfully.
    """
    print("Door has been opened!")
    if(sound):
        playsound.playsound(os.path.expanduser('~')+"/Documents/opensesame/resources/beep.wav") # final beep of door open
    pickle.dump(driver.get_cookies(), open(os.path.expanduser('~')+"/Documents/opensesame/resources/cookies.pkl", "wb"))
    return True

fbiOpenUp(dataList[0],dataList[1])
file.close()