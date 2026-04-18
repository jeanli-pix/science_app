import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION DE LA PAGE (TOUJOURS EN PREMIER) ---
st.set_page_config(page_title="Apprendre avec l'IA", layout="wide")

# --- 2. STYLE CSS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; }
    /* Style des fiches pour qu'elles soient lisibles (Noir sur blanc) */
    .card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #4A90E2;
        color: #1E1E1E !important;
    }
    .card strong { color: #0F52BA; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONFIGURATION DE L'IA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash')
except Exception as e:
    st.error("Erreur de configuration API. Vérifie tes Secrets.")

# --- 4. INITIALISATION DU STOCKAGE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "cards" not in st.session_state:
    st.session_state.cards = []
if "last_response" not in st.session_state:
    st.session_state.last_response = ""

# --- 5. NAVIGATION (SIDEBAR) ---
st.sidebar.title("📌 Menu")
page = st.sidebar.radio("Aller vers :", [" Assistant Chat", " Ma Bibliothèque"])

# --- PAGE 1 : CHAT ---
if page == " Assistant Chat":
    st.title("IA Learning Assistant")
    st.caption("Pose des questions et sauvegarde les points clés.")

    # Zone de discussion
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Que veux-tu apprendre ?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = model.generate_content(prompt)
            full_response = response.text
            st.markdown(full_response)
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.last_response = full_response

    # Bouton de sauvegarde (fixé en bas de la barre latérale ou sous le chat)
    st.sidebar.divider()
    if st.sidebar.button("✨ Sauvegarder la dernière réponse"):
        if st.session_state.last_response:
            with st.spinner("Création de la fiche..."):
                summary_prompt = f"Résume cette information en une fiche mémo courte (max 3 points clés) : {st.session_state.last_response}"
                summary = model.generate_content(summary_prompt).text
                st.session_state.cards.append({"sujet": st.session_state.messages[-2]["content"], "contenu": summary})
                st.sidebar.success("Fiche ajoutée !")
        else:
            st.sidebar.warning("Rien à sauvegarder !")

# --- PAGE 2 : BIBLIOTHÈQUE ---
else:
    st.title(" Ma Bibliothèque de Fiches")
    st.write("Retrouve ici tout ce que tu as appris.")

    if not st.session_state.cards:
        st.info("Ta bibliothèque est vide. Utilise l'assistant pour créer des fiches !")
    else:
        # Affichage propre
        for i, card in enumerate(reversed(st.session_state.cards)):
            with st.container():
                # AJOUT DU 'f' devant les guillemets pour activer les variables {}
                st.markdown(f"""
                <div class="card">
                    <strong>Fiche : {card['sujet']}</strong><br>
                    {card['contenu']}
                </div>
                """, unsafe_allow_html=True)
