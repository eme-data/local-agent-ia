# 🤖 Autobot

Assistant IA desktop connecté à l'API Anthropic (Claude) avec interface graphique et icône system tray. Cross-platform Windows / macOS.

## Installation en un clic

### Option 1 : Télécharger l'exécutable (recommandé)

Rendez-vous sur la page [Releases](https://github.com/eme-data/local-agent-ia/releases) et téléchargez :
- **Windows** : `Autobot.exe`
- **macOS** : `Autobot.dmg`

Lancez le fichier, c'est prêt !

> **Note** : Au premier lancement, Autobot vous demandera votre clé API Anthropic.
> Obtenez-la sur [console.anthropic.com](https://console.anthropic.com/).

### Option 2 : Installation depuis les sources

**Windows** : Double-cliquez sur `scripts\install-windows.bat`

**macOS / Linux** :
```bash
chmod +x scripts/install-mac.sh
./scripts/install-mac.sh
```

Puis lancez avec `lancer.bat` (Windows) ou `./lancer.sh` (Mac).

## Fonctionnalités

- **Interface desktop** : fenêtre chat avec dark theme, rendu Markdown, coloration syntaxique
- **Icône system tray** : petit robot dans la barre des tâches, fonctionne en arrière-plan
- **Streaming** : réponses en temps réel, token par token
- **Boucle agentic** : Autobot enchaîne plusieurs outils automatiquement
- **Mémoire persistante** : conversations, notes et rappels sauvegardés en SQLite
- **9 outils intégrés** :

| Outil | Description |
|-------|-------------|
| `run_command` | Exécuter des commandes système |
| `read_file` | Lire un fichier |
| `write_file` | Écrire un fichier |
| `list_directory` | Lister un répertoire |
| `get_system_info` | Informations système |
| `clipboard` | Lire/écrire le presse-papier |
| `web_search` | Recherche web (DuckDuckGo) |
| `manage_notes` | Créer, lister, modifier, supprimer des notes |
| `manage_reminders` | Créer et gérer des rappels |

## Configuration

La clé API Anthropic peut être définie de deux manières :

1. **Fichier `.env`** à la racine du projet :
   ```
   ANTHROPIC_API_KEY=sk-ant-xxxxx
   ```

2. **Variable d'environnement** système `ANTHROPIC_API_KEY`

## Utilisation

### Application desktop (recommandé)

```bash
python app.py
```

### Mode CLI

```bash
python main.py
```

Commandes CLI : `/quit` pour quitter, `/reset` pour nouvelle conversation.

## Build depuis les sources

Pour créer un exécutable standalone :

```bash
pip install pyinstaller
python build.py
```

L'exécutable sera dans `dist/`.

## Structure

```
├── app.py                # Point d'entrée desktop (pywebview + tray)
├── main.py               # Point d'entrée CLI
├── build.py              # Script de build PyInstaller
├── src/
│   ├── agent.py          # Agent (boucle agentic + streaming)
│   ├── config.py         # Configuration
│   ├── database.py       # Persistance SQLite
│   ├── tray.py           # Icône system tray (robot)
│   └── tools/
│       ├── filesystem.py # Commandes, fichiers
│       ├── system.py     # Infos système, presse-papier
│       ├── web.py        # Recherche web
│       └── productivity.py # Notes et rappels
├── ui/
│   ├── index.html        # Interface chat
│   ├── style.css         # Dark theme
│   └── app.js            # Frontend (streaming)
├── scripts/
│   ├── install-windows.bat
│   └── install-mac.sh
└── .github/workflows/
    └── build.yml         # CI/CD : build auto + release GitHub
```

## Stack technique

- **Backend** : Python + Anthropic SDK
- **Frontend** : HTML/CSS/JS dans pywebview (WebView2 Windows / WebKit macOS)
- **Tray** : pystray + Pillow
- **Base de données** : SQLite
- **Recherche web** : DuckDuckGo (gratuit, sans clé API)
- **CI/CD** : GitHub Actions + PyInstaller
