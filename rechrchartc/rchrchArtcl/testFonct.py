from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

service = Service(executavle_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

# Initialiser le WebDriver en utilisant ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())

#Test Fonctionnel Avec Selenuim :Recherche d'un article automatiquement  
def testSearch():
         # Accéder à la page de connexion
         driver.get("http://localhost:3000/login")
          #Login Utilisateur
         username_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "id_username"))
    )
       
         username_element.send_keys("Rahal")
         driver.find_element(By.ID,"id_password").send_keys("nour")
         driver.find_element(By.ID, "id_Ok").click()
         #search
         driver.get("http://localhost:3000/search")
         input_element = driver.find_element(By.ID,"id_search")
         input_element.send_keys("intelligence artificielle"+ Keys.ENTER)
         driver.implicitly_wait(100)



        

         
# Exécuter le test
testSearch()

# Fermer la fenêtre du navigateur
driver.quit()
