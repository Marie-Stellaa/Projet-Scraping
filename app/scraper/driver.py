import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import config


class CaptchaDetecte(Exception):
    pass


class Driver:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--lang=fr")
        
        # --- AMÉLIORATION : Masquer Selenium ---
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        # Un User-Agent classique pour ressembler à un vrai visiteur
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.8078.47 Safari/537.36")
        
        self.pilote = webdriver.Chrome(options=options)
        
     
        self.pilote.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

    def _page_erreur_amazon(self):
        """Détecte la page 'Toutes nos excuses' d'Amazon."""
        source = self.pilote.page_source.lower()
        titre = self.pilote.title.lower()
        return "toutes nos excuses" in titre or "toutes nos excuses" in source

    def charger(self, url, tentatives=3):
        for essai in range(1, tentatives + 1):
            self.pilote.get(url)
            
            # --- Détection du Captcha Amazon ---
            if "validatecaptcha" in self.pilote.page_source.lower() or "automatique" in self.pilote.title.lower():
                raise CaptchaDetecte("Amazon demande un captcha : arrêt du scraping pour sécurité.")
            
            # --- Détection de la page d'erreur Amazon : on patiente puis on réessaie ---
            if self._page_erreur_amazon():
                pause = random.uniform(8, 15) * essai
                print(f" Page d'erreur Amazon (essai {essai}/{tentatives}). Nouvelle tentative dans {pause:.0f}s...")
                time.sleep(pause)
                continue
            
            try:
                # Attente de l'élément configuré
                WebDriverWait(self.pilote, config.TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTEUR_PRODUIT))
                )
            except TimeoutException:
                print(f" Temps d'attente dépassé : Le sélecteur '{config.SELECTEUR_PRODUIT}' n'est pas apparu.")
                return None
            
            html = self.pilote.page_source
            # Délai légèrement aléatoire pour paraître moins robotique
            time.sleep(config.DELAI + random.uniform(1, 3))
            return html
        
        print(" Amazon bloque cette page après plusieurs tentatives.")
        return None

    def fermer(self):
        self.pilote.quit()