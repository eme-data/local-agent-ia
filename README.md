# Agent IA Local

Agent conversationnel local connecté à l'API Anthropic (Claude) pour t'aider dans ton quotidien.

## Fonctionnalités

- Conversation en langage naturel avec Claude
- Exécution de commandes système
- Lecture et écriture de fichiers
- Navigation dans les répertoires
- Informations système
- Boucle agentic (l'agent peut enchaîner plusieurs outils automatiquement)

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
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env et ajouter ta clé API Anthropic
# ANTHROPIC_API_KEY=sk-ant-xxxxx
```

## Utilisation

```bash
python main.py
```

### Commandes

| Commande | Description |
|----------|-------------|
| `/quit`  | Quitter l'agent |
| `/reset` | Réinitialiser la conversation |

## Structure

```
├── main.py           # Point d'entrée
├── src/
│   ├── agent.py      # Agent principal (boucle agentic)
│   ├── config.py     # Configuration
│   └── tools.py      # Outils disponibles pour l'agent
├── .env.example      # Template de configuration
└── requirements.txt  # Dépendances Python
```
