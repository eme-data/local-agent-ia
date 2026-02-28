from PIL import Image, ImageDraw
import pystray


class TrayManager:
    """Gère l'icône dans la barre système (system tray)."""

    def __init__(self, window, on_quit=None):
        self.window = window
        self.on_quit = on_quit
        self.icon = None

    def _create_icon_image(self) -> Image.Image:
        """Crée une icône robot pour le tray."""
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Fond rond
        draw.ellipse([2, 2, size - 2, size - 2], fill="#6c63ff")

        # Tête du robot (rectangle arrondi)
        draw.rounded_rectangle([16, 14, 48, 40], radius=4, fill="#e0e0e0")

        # Yeux
        draw.ellipse([22, 20, 30, 28], fill="#6c63ff")
        draw.ellipse([34, 20, 42, 28], fill="#6c63ff")

        # Pupilles
        draw.ellipse([24, 22, 28, 26], fill="#1a1a2e")
        draw.ellipse([36, 22, 40, 26], fill="#1a1a2e")

        # Bouche (sourire)
        draw.arc([24, 28, 40, 38], start=0, end=180, fill="#1a1a2e", width=2)

        # Antenne
        draw.line([32, 14, 32, 8], fill="#e0e0e0", width=2)
        draw.ellipse([29, 5, 35, 11], fill="#ff6b6b")

        # Corps (petit rectangle)
        draw.rounded_rectangle([20, 42, 44, 54], radius=3, fill="#e0e0e0")

        return img

    def _on_show(self, icon, item):
        """Affiche la fenêtre."""
        self.window.show()

    def _on_new(self, icon, item):
        """Nouvelle conversation."""
        self.window.evaluate_js("newConversation()")
        self.window.show()

    def _on_quit(self, icon, item):
        """Quitte l'application."""
        icon.stop()
        if self.on_quit:
            self.on_quit()

    def run(self):
        """Lance le tray icon (à appeler dans un thread séparé)."""
        menu = pystray.Menu(
            pystray.MenuItem("Ouvrir", self._on_show, default=True),
            pystray.MenuItem("Nouvelle conversation", self._on_new),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quitter", self._on_quit),
        )

        self.icon = pystray.Icon(
            name="Autobot",
            icon=self._create_icon_image(),
            title="Autobot",
            menu=menu,
        )
        self.icon.run()

    def stop(self):
        """Arrête le tray icon."""
        if self.icon:
            self.icon.stop()
