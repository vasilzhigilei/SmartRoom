'''
Unlocks dorm room door, so only a pin is required. In order to normally get into a room, you have to put your RFID
ID up against the lock, and then punch in your PIN #. Unfortunately, the mobile online "unlock my door" function only
skips the RFID part, the user then still has to punch in the PIN code. This is still useful, since now you don't need
your ID on you to get into your room, but a more convenient (and less secure) solution may involve using a stepper motor
on the inside of the door to pull the door handle. This solution may possibly be implemented in the future.
'''
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time # a better solution will be used in the future
import os
import pickle
import playsound

opts = Options()
opts.add_argument("user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/70.0.3538.102 Mobile Safari/537.36")
driver = webdriver.Chrome(chrome_options=opts)
driver.set_window_size(300,500)

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
    try: #Try to click Open Door button right away if browser is already up, and login is within 7 days of DUO
        driver.find_element_by_xpath("//*[@id='content']/div[2]/div/div/div/form[1]/ul/li/input[3]").click()
        print("Door opened via first try")
    except:
        url = "https://csg-web1.eservices.virginia.edu/login/index.php"
        driver.get(url)

        if os.path.isfile("cookies.pkl"):
            cookies = pickle.load(open("cookies.pkl", "rb"))
            for cookie in cookies:
                driver.add_cookie(cookie)

        #Click to login CS Gold WebCard Center
        driver.find_element_by_xpath("//*[@href='sso.php']").click()

        try: #Try to open door right away, but for the first time before a browser is already open
            driver.get("https://csg-web1.eservices.virginia.edu/student/openmydoor.php")
            driver.find_element_by_xpath("//*[@id='content']/div[2]/div/div/div/form[1]/ul/li/input[3]").click()
            print("Door opened via second try")
        except: #Login through netbadge and DUO 2-step
            try: #If not already logged in
                # Netbadge username/password
                driver.find_element_by_id("user").send_keys(username)
                driver.find_element_by_id("pass").send_keys(password)
                driver.find_element_by_xpath("//*[@id='loginBoxes']/fieldset[2]/span[2]/form/p[3]/input[1]").click()

                # Duo confirmation part
                time.sleep(3)
                iframe = driver.find_element_by_xpath("//*[@id='duo_iframe']")
                driver.switch_to_frame(iframe)
                duo_finished = False
                while not duo_finished:
                    try:
                        driver.find_element_by_xpath("//*[@id='messages-view']/div/div[2]/div/span")
                    except:
                        driver.find_element_by_xpath('//*[@id="login-form"]/div/div/label/input').click()
                        driver.find_element_by_xpath("//*[@id='login-form']/fieldset[2]/div[1]/button").click()
                        try:
                            driver.find_element_by_xpath('//*[@id="login-form"]/div/div/label/input')
                        except:
                            duo_finished = True
                driver.switch_to_default_content()
                print("Finished log in - try for netbadge and DUO")
            except:
                print("Error - try for netbadge and DUO")

            #Open door
            driver.get("https://csg-web1.eservices.virginia.edu/student/openmydoor.php")
            driver.find_element_by_xpath("//*[@id='content']/div[2]/div/div/div/form[1]/ul/li/input[3]").click()
            print("Door opened via second except")

    print("Door has been opened")
    playsound.playsound("beep.wav")
    pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
    return True