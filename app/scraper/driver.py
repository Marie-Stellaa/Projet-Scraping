import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config


class CaptchaDetecte(Exception):
    pass


class Driver:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--lang=fr")
        self.pilote = webdriver.Chrome(options=options)

    def charger(self, url):
        self.pilote.get(url)
        if "captcha" in self.pilote.page_source.lower():
            raise CaptchaDetecte("Amazon demande un captcha : arrêt du scraping.")
        WebDriverWait(self.pilote, config.TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTEUR_PRODUIT))
        )
        html = self.pilote.page_source
        time.sleep(config.DELAI)
        return html

    def fermer(self):
        self.pilote.quit()