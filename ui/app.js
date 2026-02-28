// --- État de l'application ---
let isStreaming = false;
let currentAssistantBubble = null;
let currentAssistantText = '';

// --- Initialisation ---
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('message-input');

    // Auto-resize du textarea
    input.addEventListener('input', () => {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    });

    // Enter pour envoyer, Shift+Enter pour retour à la ligne
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Charger l'historique quand pywebview est prêt
    if (window.pywebview) {
        loadHistory();
    } else {
        window.addEventListener('pywebviewready', loadHistory);
    }
});

// --- Configuration de marked.js ---
marked.setOptions({
    highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value;
        }
        return hljs.highlightAuto(code).value;
    },
    breaks: true,
});

// --- Envoi de message ---
function sendMessage() {
    if (isStreaming) return;

    const input = document.getElementById('message-input');
    const text = input.value.trim();
    if (!text) return;

    // Retirer le message de bienvenue
    const welcome = document.getElementById('welcome-message');
    if (welcome) welcome.remove();

    // Afficher la bulle utilisateur
    addUserBubble(text);

    // Vider le champ
    input.value = '';
    input.style.height = 'auto';

    // Désactiver l'envoi
    setStreaming(true);

    // Afficher l'indicateur de frappe
    showTypingIndicator();

    // Envoyer au backend Python
    if (window.pywebview) {
        window.pywebview.api.send_message(text);
    }
}

// --- Rendu des bulles ---
function addUserBubble(text) {
    const messages = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = 'message user';
    div.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
    messages.appendChild(div);
    scrollToBottom();
}

function createAssistantBubble() {
    removeTypingIndicator();

    const messages = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.innerHTML = '<div class="bubble"></div>';
    messages.appendChild(div);

    currentAssistantBubble = div.querySelector('.bubble');
    currentAssistantText = '';
    scrollToBottom();
}

// --- Fonctions appelées par Python via evaluate_js ---
function receiveToken(text) {
    if (!currentAssistantBubble) {
        createAssistantBubble();
    }
    currentAssistantText += text;
    currentAssistantBubble.innerHTML = marked.parse(currentAssistantText);
    scrollToBottom();
}

function toolStart(info) {
    removeTypingIndicator();

    const messages = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = 'tool-indicator';
    div.id = `tool-${Date.now()}`;
    div.innerHTML = `<div class="spinner"></div><span>🔧 ${escapeHtml(info.name)}...</span>`;
    messages.appendChild(div);
    scrollToBottom();

    // Stocker la référence pour la marquer comme terminée
    div.dataset.toolName = info.name;
}

function toolResult(info) {
    // Marquer le dernier indicateur d'outil correspondant comme terminé
    const indicators = document.querySelectorAll('.tool-indicator:not(.done)');
    for (const ind of indicators) {
        if (ind.dataset.toolName === info.name) {
            ind.classList.add('done');
            ind.querySelector('span').textContent = `🔧 ${info.name} — terminé`;
            break;
        }
    }
    scrollToBottom();
}

function responseComplete() {
    // Finaliser le rendu Markdown avec highlight.js
    if (currentAssistantBubble) {
        currentAssistantBubble.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }

    currentAssistantBubble = null;
    currentAssistantText = '';
    removeTypingIndicator();
    setStreaming(false);
}

function streamError(errorMsg) {
    removeTypingIndicator();

    if (!currentAssistantBubble) {
        createAssistantBubble();
    }
    currentAssistantBubble.innerHTML = `<span style="color: #ff6b6b;">Erreur : ${escapeHtml(errorMsg)}</span>`;
    currentAssistantBubble = null;
    currentAssistantText = '';
    setStreaming(false);
}

// --- Historique ---
async function loadHistory() {
    if (!window.pywebview) return;
    try {
        const conversations = await window.pywebview.api.get_history();
        renderHistory(conversations);
    } catch (e) {
        console.error('Erreur chargement historique:', e);
    }
}

function renderHistory(conversations) {
    const list = document.getElementById('history-list');
    if (!conversations || conversations.length === 0) {
        list.innerHTML = '<p style="padding: 16px; color: var(--text-secondary); text-align: center;">Aucune conversation</p>';
        return;
    }
    list.innerHTML = conversations.map(c => `
        <div class="history-item" onclick="loadConversation(${c.id})">
            <div class="title">${escapeHtml(c.title || 'Sans titre')}</div>
            <div class="date">${c.updated_at || ''}</div>
        </div>
    `).join('');
}

async function loadConversation(conversationId) {
    if (!window.pywebview) return;
    try {
        const messages = await window.pywebview.api.load_conversation(conversationId);
        renderConversation(messages);
        toggleHistory();
    } catch (e) {
        console.error('Erreur chargement conversation:', e);
    }
}

function renderConversation(messages) {
    const container = document.getElementById('messages');
    container.innerHTML = '';

    for (const msg of messages) {
        if (msg.role === 'user') {
            const content = typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content);
            addUserBubble(content);
        } else if (msg.role === 'assistant') {
            const content = typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content);
            const div = document.createElement('div');
            div.className = 'message assistant';
            div.innerHTML = `<div class="bubble">${marked.parse(content)}</div>`;
            container.appendChild(div);
        }
    }
    scrollToBottom();
}

function toggleHistory() {
    const panel = document.getElementById('history-panel');
    panel.classList.toggle('hidden');
    if (!panel.classList.contains('hidden')) {
        loadHistory();
    }
}

async function newConversation() {
    if (window.pywebview) {
        await window.pywebview.api.new_conversation();
    }
    const messages = document.getElementById('messages');
    messages.innerHTML = `
        <div id="welcome-message">
            <div class="welcome-icon">🤖</div>
            <h2>Bonjour !</h2>
            <p>Je suis Autobot, ton assistant IA local. Comment puis-je t'aider ?</p>
        </div>
    `;
    setStreaming(false);
}

// --- Utilitaires ---
function setStreaming(value) {
    isStreaming = value;
    document.getElementById('btn-send').disabled = value;
    document.getElementById('message-input').disabled = value;
    if (!value) {
        document.getElementById('message-input').focus();
    }
}

function showTypingIndicator() {
    removeTypingIndicator();
    const messages = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = 'typing-indicator';
    div.id = 'typing-indicator';
    div.innerHTML = '<span></span><span></span><span></span>';
    messages.appendChild(div);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

function scrollToBottom() {
    const messages = document.getElementById('messages');
    messages.scrollTop = messages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
