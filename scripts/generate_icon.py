#!/usr/bin/env python3
"""Génère les fichiers icône robot pour Windows (.ico) et macOS (.icns)."""

import os
import sys
from PIL import Image, ImageDraw, ImageFont


def draw_robot(size: int) -> Image.Image:
    """Dessine une icône robot sur un fond violet."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    s = size / 64  # facteur d'échelle

    # Fond rond
    draw.ellipse([int(2*s), int(2*s), int(62*s), int(62*s)], fill="#6c63ff")

    # Tête du robot
    draw.rounded_rectangle(
        [int(16*s), int(14*s), int(48*s), int(40*s)],
        radius=int(4*s), fill="#e0e0e0"
    )

    # Yeux
    draw.ellipse([int(22*s), int(20*s), int(30*s), int(28*s)], fill="#6c63ff")
    draw.ellipse([int(34*s), int(20*s), int(42*s), int(28*s)], fill="#6c63ff")

    # Pupilles
    draw.ellipse([int(24*s), int(22*s), int(28*s), int(26*s)], fill="#1a1a2e")
    draw.ellipse([int(36*s), int(22*s), int(40*s), int(26*s)], fill="#1a1a2e")

    # Bouche
    draw.arc(
        [int(24*s), int(28*s), int(40*s), int(38*s)],
        start=0, end=180, fill="#1a1a2e", width=max(1, int(2*s))
    )

    # Antenne
    draw.line(
        [int(32*s), int(14*s), int(32*s), int(8*s)],
        fill="#e0e0e0", width=max(1, int(2*s))
    )
    draw.ellipse([int(29*s), int(5*s), int(35*s), int(11*s)], fill="#ff6b6b")

    # Corps
    draw.rounded_rectangle(
        [int(20*s), int(42*s), int(44*s), int(54*s)],
        radius=int(3*s), fill="#e0e0e0"
    )

    return img


def generate_ico(output_path: str):
    """Génère un fichier .ico avec plusieurs tailles."""
    sizes = [16, 32, 48, 64, 128, 256]
    images = [draw_robot(s) for s in sizes]
    images[-1].save(output_path, format="ICO", sizes=[(s, s) for s in sizes], append_images=images[:-1])
    print(f"ICO généré : {output_path}")


def generate_png(output_path: str, size: int = 256):
    """Génère un fichier .png."""
    img = draw_robot(size)
    img.save(output_path, format="PNG")
    print(f"PNG généré : {output_path}")


def generate_icns(output_path: str):
    """Génère un fichier .icns (macOS) via un PNG intermédiaire."""
    # Sur macOS, on utilise iconutil. Sinon, on sauvegarde juste un PNG.
    png_path = output_path.replace(".icns", ".png")
    generate_png(png_path, 512)

    if sys.platform == "darwin":
        import subprocess
        import tempfile
        iconset_dir = tempfile.mkdtemp(suffix=".iconset")
        for size in [16, 32, 64, 128, 256, 512]:
            img = draw_robot(size)
            img.save(os.path.join(iconset_dir, f"icon_{size}x{size}.png"))
            # Retina (@2x)
            if size <= 256:
                img2x = draw_robot(size * 2)
                img2x.save(os.path.join(iconset_dir, f"icon_{size}x{size}@2x.png"))
        subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", output_path], check=True)
        print(f"ICNS généré : {output_path}")
    else:
        print(f"ICNS non généré (nécessite macOS). PNG disponible : {png_path}")


def main():
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "ui", "assets")
    os.makedirs(assets_dir, exist_ok=True)

    generate_ico(os.path.join(assets_dir, "icon.ico"))
    generate_png(os.path.join(assets_dir, "icon.png"))
    generate_icns(os.path.join(assets_dir, "icon.icns"))


if __name__ == "__main__":
    main()
