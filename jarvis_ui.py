import streamlit as st
import requests
import json

# ==============================================================================
# 1. CONFIGURACIÓN Y ESTILO (OPTIMIZADO PARA MÓVIL)
# ==============================================================================
st.set_page_config(
    page_title="Jarvis 2.0 | Automotive Expert",
    page_icon="🚗",
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# Custom CSS para estética industrial
st.markdown("""
    <style>
    .main { 
        background-color: #f5f5f5; 
        padding-top: 20px;
    }
    /* Estilo del botón profesional */
    .stButton>button { 
        width: 100%; 
        border-radius: 5px; 
        height: 3em; 
        background-color: #007BFF; 
        color: white; 
    }
    </style>
    """, unsafe_allow_html=True)

# Inicializar estado de sesión
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

# ==============================================================================
# 2. PÁGINA DE LOGIN (SIMULACIÓN DE ACCESO EMPRESARIAL)
# ==============================================================================
def show_login_page():
    st.title("🛡️ Jarvis 2.0: Access Portal")
    st.subheader("Senior Collision Adjuster Login")
    
    # Campo para API Key o credenciales de usuario
    username = st.text_input("Username (e.g., adjuster@axalta.com)")
    password = st.text_input("Password", type="password")
    
    if st.button("Secure Login", key="login_button"):
        # Validación simple de simulación
        if username and password == "2025":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Access Granted. Welcome, Senior Adjuster.")
            st.rerun() 
        else:
            st.error("Invalid credentials. Hint: Password is '2025'.")

# ==============================================================================
# 3. APLICACIÓN PRINCIPAL (VISIBLE DESPUÉS DEL LOGIN)
# ==============================================================================
def show_main_app():
    st.title("🚗 Jarvis 2.0: Automotive Expert")
    st.subheader("RAG-Enhanced Technical Estimation Engine")
    
    # User Input Section
    query = st.text_area(
        "Describe the vehicle damage or ask a technical question:",
        placeholder="e.g., Mezcla de barniz Excel-Pro y costo total en ARS...",
        height=150
    )

    # Divisas disponibles (incluyendo ARS para el mercado local)
    currency = st.selectbox("Currency:", ["USD", "ARS", "EUR", "MXN"])
    
    # Botón Único y Lógica de Ejecución
    if st.button("Generate Expert Dictamen", key="report_generation_button"):
        if not query:
            st.warning("Please enter a valid damage description.")
        else:
            # Enhanced instructions including the currency selector
            enhanced_query = f"{query}. IMPORTANT: Provide all financial costs strictly in {currency}."
            
            with st.spinner("Auditing technical docs and calculating costs..."):
                try:
                    # Backend call to local FastAPI server
                    response = requests.post(
                        "http://localhost:8000/estimate", 
                        json={"description": enhanced_query},
                        timeout= 120
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success("Auditoría del Ajustador Completada")
                        
                        # --- INICIO DEL RENDERIZADO ESTRUCTURADO Y HUMANO (CÓDIGO CORREGIDO) ---
                        
                        st.markdown("### 📄 Veredicto del Ajustador Senior")
                        
                        # 1. El veredicto inicial humano (Tono profesional)
                        st.markdown(data.get('final_technical_verdict', 'Error: No se encontró el resumen.')) 
                        
                        st.markdown("---")
                        
                        # 2. Desglose en tablas de Markdown (Materiales)
                        st.markdown("#### 💰 Desglose de Costos de Materiales")
                        material_data = [
                            [
                                item['description'], 
                                f"${item['usd_per_unit']:.2f} (x{item['quantity']:.1f})", 
                                f"{currency} {item.get('cost_ars', 0.0):,.2f}" # Usamos .get para seguridad
                            ] 
                            for item in data.get('material_costs', [])
                        ]
                        st.table([["Descripción", "Costo Base (USD)", f"Total ({currency})"]] + material_data)

                        # 3. Desglose en tablas de Markdown (Mano de Obra)
                        st.markdown("#### 👷 Costos de Mano de Obra y Operacionales")
                        labor_data = [
                            [
                                item['description'], 
                                f"${item['usd_per_unit']:.2f} (x{item['quantity']:.1f})", 
                                f"{currency} {item.get('cost_ars', 0.0):,.2f}" # Usamos .get para seguridad
                            ] 
                            for item in data.get('labor_and_oh_costs', [])
                        ]
                        st.table([["Descripción", "Tarifa Base (USD/Hora)", f"Total ({currency})"]] + labor_data)

                        # 4. Resumen y Citaciones
                        st.markdown("---")
                        # Formato del total general
                        st.markdown(f"**TOTAL GENERAL ESTIMADO:** **{currency} {data.get('total_ars', 0.0):,.2f}**")
                        
                        st.caption(f"**Evidencia Técnica:** {data.get('evidence_source', 'No citada')} | **Tasa Aplicada:** 1 USD = {data.get('exchange_rate', 'N/A')} {currency}")
                        
                        # --- FIN DEL RENDERIZADO ESTRUCTURADO Y HUMANO ---
                        
                    else:
                        st.error(f"Backend Error: HTTP {response.status_code}")
                        try:
                            # Intenta mostrar el detalle del error JSON
                            error_detail = response.json()
                            st.json(error_detail) # Usamos st.json para ver el detalle de forma clara
                        except:
                            # Si no es un JSON, muestra el texto crudo
                            st.text(response.text) 
                        
                except requests.exceptions.ConnectionError:
                    st.error("Connection Refused: Make sure the FastAPI server (uvicorn) is running on port 8000.")
                except requests.exceptions.ReadTimeout:
                    st.error("Timeout Error: The AI engine took too long to respond (120 seconds limit). Try reducing the complexity of the query.")


    # Opción de Logout
    if st.button("Logout", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

# ==============================================================================
# 4. CONTROL DE FLUJO
# ==============================================================================
if not st.session_state.logged_in:
    show_login_page()
else:
    show_main_app()