import streamlit as st
import random

st.set_page_config(page_title="Chronicles of Eldoria RPG", page_icon="⚔️", layout="wide")

# Estilo visual personalizado Dark Fantasy
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .combat-log { background-color: #1e222d; padding: 12px; border-radius: 8px; border-left: 4px solid #f39c12; }
    </style>
""", unsafe_allow_html=True)

# === INICIALIZACIÓN DEL ESTADO ===
if "jugador" not in st.session_state:
    st.session_state.jugador = None
if "escena" not in st.session_state:
    st.session_state.escena = "creacion"
if "enemigo" not in st.session_state:
    st.session_state.enemigo = None
if "log_combate" not in st.session_state:
    st.session_state.log_combate = []

# === DATOS DE CLASES Y ENEMIGOS ===
CLASES = {
    "Guerrero 🛡️": {"hp_max": 150, "mana_max": 30, "atq": 18, "def": 8, "habilidad": "Golpe de Escudo (20 Mana)"},
    "Mago 🔮": {"hp_max": 90, "mana_max": 100, "atq": 25, "def": 3, "habilidad": "Bola de Fuego (30 Mana)"},
    "Pícaro 🗡️": {"hp_max": 110, "mana_max": 50, "atq": 22, "def": 5, "habilidad": "Ataque Furtivo (25 Mana)"}
}

ENEMIGOS = {
    "Bosque": [
        {"nombre": "Goblin Silvestre", "hp_max": 50, "hp": 50, "atq": 10, "xp": 40, "oro": 25, "img": "👺"},
        {"nombre": "Lobo Hambriento", "hp_max": 65, "hp": 65, "atq": 14, "xp": 55, "oro": 30, "img": "🐺"}
    ],
    "Mazmorra": [
        {"nombre": "Esqueleto Guerrero", "hp_max": 100, "hp": 100, "atq": 20, "xp": 90, "oro": 60, "img": "💀"},
        {"nombre": "Orco Brutal", "hp_max": 140, "hp": 140, "atq": 26, "xp": 130, "oro": 90, "img": "👹"}
    ],
    "Jefe": [
        {"nombre": "Rey Demonio Malakor", "hp_max": 320, "hp": 320, "atq": 38, "xp": 500, "oro": 500, "img": "🐲"}
    ]
}

# === FUNCIONES DE LÓGICA ===
def subir_nivel_check():
    j = st.session_state.jugador
    if j["xp"] >= j["xp_siguiente"]:
        j["nivel"] += 1
        j["xp"] -= j["xp_siguiente"]
        j["xp_siguiente"] = int(j["xp_siguiente"] * 1.5)
        j["hp_max"] += 20
        j["hp"] = j["hp_max"]
        j["mana_max"] += 15
        j["mana"] = j["mana_max"]
        j["atq"] += 5
        j["def"] += 2
        st.toast(f"🎉 ¡HAS SUBIDO AL NIVEL {j['nivel']}! Tus atributos han aumentado.", icon="⭐")

def Iniciar_Combate(zona):
    opciones = ENEMIGOS[zona]
    enemigo_base = random.choice(opciones)
    st.session_state.enemigo = enemigo_base.copy()
    st.session_state.log_combate = [f"⚔️ ¡Un {enemigo_base['nombre']} ha aparecido!"]
    st.session_state.escena = "combate"

# === INTERFAZ: CREACIÓN DE PERSONAJE ===
if st.session_state.escena == "creacion":
    st.title("⚔️ CHRONICLES OF ELDORIA")
    st.subheader("Crea a tu Héroe para comenzar la aventura")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        nombre = st.text_input("Nombre de tu héroe:", value="Aventurero")
        clase_sel = st.selectbox("Elige tu clase:", list(CLASES.keys()))
        
        datos = CLASES[clase_sel]
        st.write(f"❤️ **Vida:** {datos['hp_max']} | 🔷 **Maná:** {datos['mana_max']}")
        st.write(f"⚔️ **Ataque:** {datos['atq']} | 🛡️ **Defensa:** {datos['def']}")
        st.write(f"✨ **Habilidad Especial:** {datos['habilidad']}")
        
        if st.button("🚀 Comenzar Aventura"):
            st.session_state.jugador = {
                "nombre": nombre, "clase": clase_sel, "nivel": 1, "xp": 0, "xp_siguiente": 100,
                "hp_max": datos["hp_max"], "hp": datos["hp_max"],
                "mana_max": datos["mana_max"], "mana": datos["mana_max"],
                "atq": datos["atq"], "def": datos["def"], "oro": 50,
                "pociones_hp": 2, "pociones_mana": 1, "equipo": "Ropas de Viajero"
            }
            st.session_state.escena = "hub"
            st.rerun()

# === PANEL LATERAL Y NAVEGACIÓN ===
else:
    j = st.session_state.jugador
    
    with st.sidebar:
        st.header(f"👤 {j['nombre']}")
        st.caption(f"Clase: {j['clase']} | Nivel {j['nivel']}")
        
        st.write("**Estadísticas:**")
        st.progress(max(0.0, min(1.0, j["hp"] / j["hp_max"])), text=f"❤️ HP: {j['hp']}/{j['hp_max']}")
        st.progress(max(0.0, min(1.0, j["mana"] / j["mana_max"])), text=f"🔷 Maná: {j['mana']}/{j['mana_max']}")
        st.progress(max(0.0, min(1.0, j["xp"] / j["xp_siguiente"])), text=f"⭐ XP: {j['xp']}/{j['xp_siguiente']}")
        
        st.divider()
        col_s1, col_s2 = st.columns(2)
        col_s1.metric("⚔️ ATQ", j["atq"])
        col_s2.metric("🛡️ DEF", j["def"])
        
        st.write(f"💰 **Oro:** {j['oro']} monedas")
        st.write(f"🎒 **Pociones HP:** {j['pociones_hp']} | **Pociones Maná:** {j['pociones_mana']}")
        st.caption(f"🛡️ **Equipo:** {j['equipo']}")

    # === ESCENA: CIUDAD CENTRAL (HUB) ===
    if st.session_state.escena == "hub":
        st.title("🏰 Ciudad Antigua de Oakhaven")
        st.write("Desde aquí puedes recuperarte, comprar mejor equipo o adentrarte en zonas peligrosas.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🏡 La Posada")
            st.write("Descansa para restaurar toda tu salud y maná.")
            if st.button("🛌 Descansar (15 💰)"):
                if j["oro"] >= 15:
                    j["oro"] -= 15
                    j["hp"] = j["hp_max"]
                    j["mana"] = j["mana_max"]
                    st.success("¡Te has recuperado por completo!")
                    st.rerun()
                else:
                    st.error("No tienes suficiente oro.")
                    
        with col2:
            st.subheader("🛒 El Mercado")
            st.write("Compra consumibles y equipo para tus combates.")
            if st.button("Entrar a la Tienda"):
                st.session_state.escena = "tienda"
                st.rerun()
                
        with col3:
            st.subheader("🗺️ Mapa de Zonas")
            st.write("Selecciona tu destino de combate:")
            if st.button("🌲 Bosque de los Lamentos (Fácil)"):
                Iniciar_Combate("Bosque")
                st.rerun()
            if st.button("🏛️ Mazmorras Olvidadas (Medio)"):
                Iniciar_Combate("Mazmorra")
                st.rerun()
            if st.button("🔥 Trono del Rey Demonio (JEFE)", type="primary"):
                Iniciar_Combate("Jefe")
                st.rerun()

    # === ESCENA: TIENDA ===
    elif st.session_state.escena == "tienda":
        st.title("🛒 Mercado de Armas y Alquimia")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🧪 Consumibles")
            if st.button("Comprar Poción HP (+50 HP) - 20 💰"):
                if j["oro"] >= 20:
                    j["oro"] -= 20
                    j["pociones_hp"] += 1
                    st.success("Poción de Salud comprada.")
                    st.rerun()
            if st.button("Comprar Poción Maná (+40 MP) - 20 💰"):
                if j["oro"] >= 20:
                    j["oro"] -= 20
                    j["pociones_mana"] += 1
                    st.success("Poción de Maná comprada.")
                    st.rerun()
                    
        with col2:
            st.subheader("⚔️ Equipamiento")
            if st.button("Espada de Hierro (+8 ATQ) - 80 💰"):
                if j["oro"] >= 80 and j["equipo"] != "Espada de Hierro":
                    j["oro"] -= 80
                    j["atq"] += 8
                    j["equipo"] = "Espada de Hierro"
                    st.success("¡Espada de Hierro equipada!")
                    st.rerun()
            if st.button("Armadura de Placas (+6 DEF) - 100 💰"):
                if j["oro"] >= 100 and "Placas" not in j["equipo"]:
                    j["oro"] -= 100
                    j["def"] += 6
                    j["equipo"] += " + Placas"
                    st.success("¡Armadura equipada!")
                    st.rerun()
                    
        if st.button("⬅️ Volver a la Ciudad"):
            st.session_state.escena = "hub"
            st.rerun()

    # === ESCENA: SISTEMA DE COMBATE ===
    elif st.session_state.escena == "combate":
        ene = st.session_state.enemigo
        st.title(f"⚔️ COMBATE: {j['nombre']} VS {ene['nombre']}")
        
        # Estado del enemigo
        st.subheader(f"{ene['img']} {ene['nombre']}")
        st.progress(max(0.0, min(1.0, ene["hp"] / ene["hp_max"])), text=f"Salud Enemiga: {ene['hp']}/{ene['hp_max']} HP")
        
        st.divider()
        
        # Opciones de Acción
        col1, col2, col3, col4 = st.columns(4)
        
        # Acción 1: Ataque Básico
        if col1.button("⚔️ Ataque Básico"):
            dano_jugador = max(1, j["atq"] + random.randint(-3, 5))
            ene["hp"] -= dano_jugador
            st.session_state.log_combate.append(f"🗡️ Infligiste **{dano_jugador}** de daño a {ene['nombre']}.")
            
            # Turno Enemigo si sigue vivo
            if ene["hp"] > 0:
                dano_ene = max(1, ene["atq"] - j["def"] + random.randint(-2, 3))
                j["hp"] -= dano_ene
                st.session_state.log_combate.append(f"💥 {ene['nombre']} te atacó e infligió **{dano_ene}** de daño.")
            st.rerun()

        # Acción 2: Habilidad Especial
        if col2.button("✨ Usar Habilidad"):
            costo_mana = 20 if "Guerrero" in j["clase"] else (30 if "Mago" in j["clase"] else 25)
            if j["mana"] >= costo_mana:
                j["mana"] -= costo_mana
                dano_magico = max(1, int(j["atq"] * 1.8) + random.randint(2, 8))
                ene["hp"] -= dano_magico
                st.session_state.log_combate.append(f"✨ ¡Usaste tu Habilidad Especial e infligiste **{dano_magico}** de daño!")
                
                if ene["hp"] > 0:
                    dano_ene = max(1, ene["atq"] - j["def"] + random.randint(-2, 3))
                    j["hp"] -= dano_ene
                    st.session_state.log_combate.append(f"💥 {ene['nombre']} respondió atacando con **{dano_ene}** de daño.")
            else:
                st.toast("❌ ¡No tienes suficiente Maná!", icon="⚠️")
            st.rerun()

        # Acción 3: Usar Poción HP
        if col3.button("🧪 Usar Poción HP"):
            if j["pociones_hp"] > 0:
                j["pociones_hp"] -= 1
                j["hp"] = min(j["hp_max"], j["hp"] + 50)
                st.session_state.log_combate.append("🧪 Usaste una Poción y recuperaste **50 HP**.")
                
                if ene["hp"] > 0:
                    dano_ene = max(1, ene["atq"] - j["def"] + random.randint(-2, 3))
                    j["hp"] -= dano_ene
                    st.session_state.log_combate.append(f"💥 {ene['nombre']} aprovechó tu guardia baja e infligió **{dano_ene}** de daño.")
            else:
                st.toast("❌ No te quedan pociones de salud.", icon="⚠️")
            st.rerun()

        # Acción 4: Huir
        if col4.button("🏃 Huir"):
            st.session_state.escena = "hub"
            st.toast("Has huido del combate.", icon="🏃")
            st.rerun()

        # Registro del combate
        st.divider()
        st.write("**Historial de Batalla:**")
        for log in reversed(st.session_state.log_combate[-5:]):
            st.markdown(f"<div class='combat-log'>{log}</div><br>", unsafe_allow_html=True)

        # Verificación de Resultados
        if ene["hp"] <= 0:
            st.balloons()
            st.success(f"🏆 ¡HAS DERROTADO A {ene['nombre'].upper()}!")
            j["xp"] += ene["xp"]
            j["oro"] += ene["oro"]
            st.write(f"Recompensas: **+{ene['xp']} XP** | **+{ene['oro']} Monedas de Oro**")
            subir_nivel_check()
            if st.button("Volver a la Ciudad"):
                st.session_state.escena = "hub"
                st.rerun()

        elif j["hp"] <= 0:
            st.error("💀 HAS SIDO DERROTADO EN COMBATE...")
            if st.button("🔄 Reiniciar Aventura"):
                st.session_state.clear()
                st.rerun()
