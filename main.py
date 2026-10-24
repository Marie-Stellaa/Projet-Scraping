
import sys
sys.path.append('.')  


def main():
    from app.controllers.scraping_controller import ScrapingController

    controleur = ScrapingController()

    if "--console" in sys.argv:
        # python main.py --console  -> mode texte
        controleur.lancer_application()
    else:
        # python main.py  -> interface graphique
        from app.views.interface_view import InterfaceView
        InterfaceView(controleur).mainloop()


if __name__ == "__main__":
    main()