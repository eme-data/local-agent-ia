#!/bin/bash
echo ""
echo "  ===================================="
echo "    Installation de Autobot"
echo "  ===================================="
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "[ERREUR] Python 3 n'est pas installé."
    echo "Installe-le avec : brew install python3"
    echo "Ou télécharge-le sur https://www.python.org/downloads/"
    exit 1
fi

echo "[1/4] Création de l'environnement virtuel..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[ERREUR] Impossible de créer l'environnement virtuel."
    exit 1
fi

echo "[2/4] Activation de l'environnement..."
source venv/bin/activate

echo "[3/4] Installation des dépendances..."
pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "[ERREUR] Impossible d'installer les dépendances."
    exit 1
fi

echo "[4/4] Configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "  ============================================"
    echo "    IMPORTANT : Configure ta clé API Anthropic"
    echo "  ============================================"
    echo ""
    echo "  Ouvre le fichier .env et remplace la valeur de"
    echo "  ANTHROPIC_API_KEY par ta clé API."
    echo ""
    echo "  Pour obtenir une clé : https://console.anthropic.com/"
    echo ""
fi

echo ""
echo "  ===================================="
echo "    Installation terminée !"
echo "  ===================================="
echo ""
echo "  Pour lancer l'application :"
echo "    ./lancer.sh"
echo "    ou : source venv/bin/activate && python app.py"
echo ""
