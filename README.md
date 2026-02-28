# Agent IA Local

Agent conversationnel desktop connecté à l'API Anthropic (Claude) avec interface graphique et icône system tray. Cross-platform Windows / macOS.

## Fonctionnalités

- **Interface desktop** : fenêtre chat avec dark theme, rendu Markdown, coloration syntaxique
- **Icône system tray** : accès rapide, fonctionne en arrière-plan
- **Streaming** : réponses en temps réel, token par token
- **Boucle agentic** : l'agent enchaîne plusieurs outils automatiquement
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

## Installation

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows :
venv\Scripts\activate
# Mac/Linux :
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## Configuration

```bash
cp .env.example .env
# Éditer .env et ajouter ta clé API Anthropic :
# ANTHROPIC_API_KEY=sk-ant-xxxxx
```

## Utilisation

### Application desktop (recommandé)

```bash
python app.py
```

Lance la fenêtre de chat + icône system tray.

### Mode CLI

```bash
python main.py
```

Interface terminal avec Rich. Commandes : `/quit`, `/reset`.

## Structure

```
├── app.py                # Point d'entrée desktop (pywebview + tray)
├── main.py               # Point d'entrée CLI
├── src/
│   ├── agent.py          # Agent principal (boucle agentic + streaming)
│   ├── config.py         # Configuration (API, chemins, prompt système)
│   ├── database.py       # Persistance SQLite
│   ├── tray.py           # Icône system tray
│   └── tools/
│       ├── __init__.py   # Agrégation des outils
│       ├── filesystem.py # Commandes, lecture/écriture fichiers
│       ├── system.py     # Infos système, presse-papier
│       ├── web.py        # Recherche web DuckDuckGo
│       └── productivity.py # Notes et rappels
├── ui/
│   ├── index.html        # Interface chat HTML
│   ├── style.css         # Styles dark theme
│   └── app.js            # Logique frontend (streaming)
├── .env.example
└── requirements.txt
```

## Stack technique

- **Backend** : Python + Anthropic SDK
- **Frontend** : HTML/CSS/JS dans pywebview (WebView2 Windows / WebKit macOS)
- **Tray** : pystray + Pillow
- **Base de données** : SQLite (conversations, notes, rappels)
- **Recherche web** : DuckDuckGo (gratuit, sans clé API)
