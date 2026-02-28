import threading
from PIL import Image, ImageDraw
import pystray


class TrayManager:
    """Gère l'icône dans la barre système (system tray)."""

    def __init__(self, window, on_quit=None):
        self.window = window
        self.on_quit = on_quit
        self.icon = None

    def _create_icon_image(self) -> Image.Image:
        """Crée une icône programmatique (cercle violet avec 'IA')."""
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Cercle de fond
        draw.ellipse([2, 2, size - 2, size - 2], fill="#6c63ff")
        # Texte 'IA'
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial", 24)
        except Exception:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), "IA", font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        draw.text(
            ((size - text_w) / 2, (size - text_h) / 2 - 2),
            "IA",
            fill="white",
            font=font,
        )
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
            name="AgentIA",
            icon=self._create_icon_image(),
            title="Agent IA",
            menu=menu,
        )
        self.icon.run()

    def stop(self):
        """Arrête le tray icon."""
        if self.icon:
            self.icon.stop()
