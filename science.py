import streamlit as st
import google.generativeai as genai


# --- STYLE CSS POUR LES FICHES ---
st.markdown("""
    <style>
    /* On force le texte des fiches en noir et on ajoute un fond léger */
    .stMarkdown p, .stMarkdown li {
        color: #1E1E1E !important;
    }
    
    /* Si tu utilises des containers pour tes fiches, on leur donne un style propre */
    .element-container {
        color: #1E1E1E;
    }

    /* Style spécifique pour le titre des fiches si besoin */
    h1, h2, h3 {
        color: #0F52BA !important; /* Un beau bleu scientifique */
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURATION DE L'IA ---
# Remplace par ta vraie clé API récupérée sur Google AI Studio
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("La clé API est manquante dans les Secrets de Streamlit.")
model = genai.GenerativeModel('models/gemini-2.5-flash')

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Apprendre avec l'IA", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; }
    .card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #4A90E2;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DU STOCKAGE (SESSION STATE) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "cards" not in st.session_state:
    st.session_state.cards = []
if "last_response" not in st.session_state:
    st.session_state.last_response = ""

# --- INTERFACE ---
st.title(" IA Learning Assistant")
st.caption("Pose des questions, apprends, et sauvegarde tes connaissances.")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Discussion")
    
    # Historique de la conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Zone de saisie
    if prompt := st.chat_input("Que veux-tu apprendre ?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Appel à l'IA
            response = model.generate_content(prompt)
            full_response = response.text
            st.markdown(full_response)
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.last_response = full_response

with col2:
    st.subheader("📂 Mémoire & Fiches")
    
    # Bouton pour sauvegarder
    if st.button(" Cette réponse est intéressante !"):
        if st.session_state.last_response:
            # On demande à l'IA de résumer la réponse en une fiche courte
            summary_prompt = f"Résume cette information en une fiche mémo très courte et structurée : {st.session_state.last_response}"
            summary = model.generate_content(summary_prompt).text
            st.session_state.cards.append(summary)
            st.success("Fiche ajoutée à ta bibliothèque !")
        else:
            st.warning("Pose une question d'abord !")

    st.divider()
    
    # Affichage des cartes sauvegardées
    if not st.session_state.cards:
        st.info("Tes fiches mémo apparaîtront ici.")
    else:
        for i, card in enumerate(reversed(st.session_state.cards)):
            st.markdown(f"""<div class="card"><strong>Fiche #{len(st.session_state.cards)-i}</strong><br>{card}</div>""", unsafe_allow_html=True)
