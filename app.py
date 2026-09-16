import streamlit as st
import random

st.set_page_config(page_title="Chronicles of Eldoria RPG", page_icon="⚔️", layout="wide")

# Compatibilidad de recarga para cualquier versión de Streamlit
def recargar():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

# Estilos CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .npc-card { background-color: #1a1c23; border: 1px solid #343b4f; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
    .combat-log { background-color: #1e222d; padding: 8px 12px; border-radius: 6px; border-left: 4px solid #f39c12; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# DATOS
CLASES = {
    "Guerrero 🛡️": {"hp_max": 160, "mana_max": 30, "atq": 18, "def": 10, "habilidad": "Golpe de Escudo (20 MP)"},
    "Mago 🔮": {"hp_max": 95, "mana_max": 110, "atq": 26, "def": 4, "habilidad": "Bola de Fuego (30 MP)"},
    "Pícaro 🗡️": {"hp_max": 115, "mana_max": 50, "atq": 22, "def": 6, "habilidad": "Ataque Furtivo (25 MP)"}
}

ENEMIGOS = {
    "Bosque": [
        {"nombre": "Goblin Silvestre", "hp_max": 55, "hp": 55, "atq": 12, "xp": 45, "oro": 30, "icon": "👺"},
        {"nombre": "Lobo de Sombras", "hp_max": 70, "hp": 70, "atq": 16, "xp": 60, "oro": 35, "icon": "🐺"}
    ],
    "Mazmorra": [
        {"nombre": "Esqueleto Guerrero", "hp_max": 110, "hp": 110, "atq": 22, "xp": 95, "oro": 65, "icon": "💀"},
        {"nombre": "Orco Devastador", "hp_max": 150, "hp": 150, "atq": 28, "xp": 140, "oro": 100, "icon": "👹"}
    ],
    "Jefe": [
        {"nombre": "Rey Demonio Malakor", "hp_max": 350, "hp": 350, "atq": 40, "xp": 600, "oro": 600, "icon": "🐲"}
    ]
}

# ESTADO INICIAL
if "jugador" not in st.session_state:
    st.session_state.jugador = None
if "escena" not in st.session_state:
    st.session_state.escena = "creacion"
if "enemigo" not in st.session_state:
    st.session_state.enemigo = None
if "log_combate" not in st.session_state:
    st.session_state.log_combate = []

def subir_nivel_check():
    j = st.session_state.jugador
    if j["xp"] >= j["xp_siguiente"]:
        j["nivel"] += 1
        j["xp"] -= j["xp_siguiente"]
        j["xp_siguiente"] = int(j["xp_siguiente"] * 1.5)
        j["hp_max"] += 25
        j["hp"] = j["hp_max"]
        j["mana_max"] += 15
        j["mana"] = j["mana_max"]
        j["atq"] += 6
        j["def"] += 3
        st.success(f"⭐ ¡NIVEL {j['nivel']} ALCANZADO!")

def iniciar_combate(zona):
    enemigo_base = random.choice(ENEMIGOS[zona])
    st.session_state.enemigo = enemigo_base.copy()
    st.session_state.log_combate = [f"⚔️ ¡Un {enemigo_base['nombre']} te ataca!"]
    st.session_state.escena = "combate"

# === CREACIÓN DE PERSONAJE ===
if st.session_state.escena == "creacion":
    st.title("⚔️ CHRONICLES OF ELDORIA RPG")
    st.subheader("Crea a tu Héroe")
    
    nombre = st.text_input("Nombre del Héroe:", value="Aventurero")
    clase_sel = st.selectbox("Clase:", list(CLASES.keys()))
    datos = CLASES[clase_sel]
    
    st.write(f"❤️ **Vida:** {datos['hp_max']} | 🔷 **Maná:** {datos['mana_max']}")
    st.write(f"⚔️ **Ataque:** {datos['atq']} | 🛡️ **Defensa:** {datos['def']}")
    st.write(f"✨ **Habilidad:** {datos['habilidad']}")
    
    if st.button("🚀 Comenzar la Aventura", key="btn_inicio"):
        st.session_state.jugador = {
            "nombre": nombre, "clase": clase_sel, "nivel": 1, "xp": 0, "xp_siguiente": 100,
            "hp_max": datos["hp_max"], "hp": datos["hp_max"],
            "mana_max": datos["mana_max"], "mana": datos["mana_max"],
            "atq": datos["atq"], "def": datos["def"], "oro": 60,
            "pociones_hp": 2, "pociones_mana": 1, "equipo": "Ropas Simples",
            "mision_activa": False, "mision_completada": False
        }
        st.session_state.escena = "hub"
        recargar()

# === JUEGO PRINCIPAL ===
else:
    j = st.session_state.jugador
    
    with st.sidebar:
        st.header(f"👤 {j['nombre']}")
        st.caption(f"{j['clase']} | Nivel {j['nivel']}")
        
        hp_perc = max(0.0, min(1.0, j["hp"] / j["hp_max"]))
        mp_perc = max(0.0, min(1.0, j["mana"] / j["mana_max"]))
        xp_perc = max(0.0, min(1.0, j["xp"] / j["xp_siguiente"]))
        
        st.progress(hp_perc, text=f"❤️ HP: {j['hp']}/{j['hp_max']}")
        st.progress(mp_perc, text=f"🔷 MP: {j['mana']}/{j['mana_max']}")
        st.progress(xp_perc, text=f"⭐ XP: {j['xp']}/{j['xp_siguiente']}")
        
        st.divider()
        c1, c2 = st.columns(2)
        c1.metric("⚔️ ATQ", j["atq"])
        c2.metric("🛡️ DEF", j["def"])
        
        st.write(f"💰 **Oro:** {j['oro']}")
        st.write(f"🧪 **Pociones HP:** {j['pociones_hp']} | 🔷 **MP:** {j['pociones_mana']}")
        st.caption(f"🛡️ **Equipo:** {j['equipo']}")

    # HUB
    if st.session_state.escena == "hub":
        st.title("🏰 Ciudad Antigua de Oakhaven")
        st.write("Selecciona un lugar para explorar:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div class='npc-card'><h3>🍺 La Taberna</h3><p>Habla con Brak para misiones y descansos.</p></div>", unsafe_allow_html=True)
            if st.button("Entrar a la Taberna", key="btn_taberna"):
                st.session_state.escena = "taberna"
                recargar()

        with col2:
            st.markdown("<div class='npc-card'><h3>🛒 El Mercado</h3><p>Compra armas y pociones con Gideon.</p></div>", unsafe_allow_html=True)
            if st.button("Entrar al Mercado", key="btn_tienda"):
                st.session_state.escena = "tienda"
                recargar()

        with col3:
            st.markdown("<div class='npc-card'><h3>🔮 El Sabio</h3><p>Recibe bendiciones mágicas de Eldrin.</p></div>", unsafe_allow_html=True)
            if st.button("Visitar al Sabio", key="btn_sabio"):
                st.session_state.escena = "sabio"
                recargar()

        st.divider()
        st.subheader("🗺️ Combates disponibles")
        cz1, cz2, cz3 = st.columns(3)
        if cz1.button("🌲 Bosque Silvestre", key="btn_bosque"):
            iniciar_combate("Bosque")
            recargar()
        if cz2.button("🏛️ Mazmorra Maldita", key="btn_mazmorra"):
            iniciar_combate("Mazmorra")
            recargar()
        if cz3.button("🐲 Rey Demonio (JEFE)", key="btn_jefe", type="primary"):
            iniciar_combate("Jefe")
            recargar()

    # TABERNA
    elif st.session_state.escena == "taberna":
        st.title("🍺 La Taberna de Brak")
        st.markdown("<div class='npc-card'><b>Brak el Tabernero:</b> <i>'¡Bienvenido! ¿Buscas un trago o trabajo?'</i></div>", unsafe_allow_html=True)
        
        if st.button("🛌 Descansar (15 💰)", key="btn_descanso"):
            if j["oro"] >= 15:
                j["oro"] -= 15
                j["hp"], j["mana"] = j["hp_max"], j["mana_max"]
                st.success("¡Salud y Maná restaurados!")
                recargar()
            else:
                st.error("Oro insuficiente.")

        if not j["mision_activa"] and not j["mision_completada"]:
            if st.button("📜 Aceptar Misión de Caza", key="btn_mision_acc"):
                j["mision_activa"] = True
                st.info("Misión aceptada: Gana 1 combate y regresa.")
                recargar()
        elif j["mision_activa"] and not j["mision_completada"]:
            if st.button("🎁 Cobrar Recompensa de Misión", key="btn_mision_cob"):
                j["oro"] += 80
                j["xp"] += 50
                j["mision_activa"] = False
                j["mision_completada"] = True
                subir_nivel_check()
                recargar()
                
        if st.button("⬅️ Volver a la Ciudad", key="btn_back_taberna"):
            st.session_state.escena = "hub"
            recargar()

    # TIENDA
    elif st.session_state.escena == "tienda":
        st.title("🛒 El Mercado de Gideon")
        st.markdown("<div class='npc-card'><b>Gideon:</b> <i>'Tengo lo necesario para mantenerte vivo.'</i></div>", unsafe_allow_html=True)
        
        if st.button("🧪 Poción HP (+50 HP) - 25 💰", key="btn_buy_hp"):
            if j["oro"] >= 25:
                j["oro"] -= 25
                j["pociones_hp"] += 1
                recargar()
        if st.button("🔷 Poción MP (+40 MP) - 20 💰", key="btn_buy_mp"):
            if j["oro"] >= 20:
                j["oro"] -= 20
                j["pociones_mana"] += 1
                recargar()
        if st.button("⚔️ Espada Rúnica (+10 ATQ) - 90 💰", key="btn_buy_sword"):
            if j["oro"] >= 90 and "Espada" not in j["equipo"]:
                j["oro"] -= 90
                j["atq"] += 10
                j["equipo"] = "Espada Rúnica"
                recargar()

        if st.button("⬅️ Volver a la Ciudad", key="btn_back_tienda"):
            st.session_state.escena = "hub"
            recargar()

    # SABIO
    elif st.session_state.escena == "sabio":
        st.title("🔮 Eldrin el Sabio")
        st.markdown("<div class='npc-card'><b>Eldrin:</b> <i>'Aumentaré tu poder a cambio de oro.'</i></div>", unsafe_allow_html=True)
        
        if st.button("✨ Ritual de Fuerza (+4 ATQ) - 75 💰", key="btn_buff_atq"):
            if j["oro"] >= 75:
                j["oro"] -= 75
                j["atq"] += 4
                recargar()
        if st.button("🛡️ Bendición Arcana (+4 DEF) - 75 💰", key="btn_buff_def"):
            if j["oro"] >= 75:
                j["oro"] -= 75
                j["def"] += 4
                recargar()

        if st.button("⬅️ Volver a la Ciudad", key="btn_back_sabio"):
            st.session_state.escena = "hub"
            recargar()

    # COMBATE
    elif st.session_state.escena == "combate":
        ene = st.session_state.enemigo
        st.title(f"⚔️ BATALLA: {j['nombre']} vs {ene['icon']} {ene['nombre']}")
        
        ene_hp_perc = max(0.0, min(1.0, ene["hp"] / ene["hp_max"]))
        st.progress(ene_hp_perc, text=f"Salud de {ene['nombre']}: {ene['hp']}/{ene['hp_max']} HP")
        
        b1, b2, b3, b4 = st.columns(4)
        
        if b1.button("⚔️ Atacar", key="btn_bat_atq"):
            crit = random.random() < 0.2
            dano = (j["atq"] * 2 if crit else j["atq"]) + random.randint(-2, 3)
            dano = max(1, dano)
            ene["hp"] -= dano
            txt = " 💥 ¡CRÍTICO!" if crit else ""
            st.session_state.log_combate.append(f"🗡️ Infligiste **{dano}** de daño.{txt}")
            
            if ene["hp"] > 0:
                dano_e = max(1, ene["atq"] - j["def"] + random.randint(-2, 2))
                j["hp"] -= dano_e
                st.session_state.log_combate.append(f"🩸 {ene['nombre']} atacó con **{dano_e}** de daño.")
            recargar()

        if b2.button("✨ Habilidad", key="btn_bat_hab"):
            costo = 20 if "Guerrero" in j["clase"] else (30 if "Mago" in j["clase"] else 25)
            if j["mana"] >= costo:
                j["mana"] -= costo
                dano_m = int(j["atq"] * 1.8) + random.randint(3, 8)
                ene["hp"] -= dano_m
                st.session_state.log_combate.append(f"✨ ¡Habilidad usada! **{dano_m}** de daño.")
                if ene["hp"] > 0:
                    dano_e = max(1, ene["atq"] - j["def"])
                    j["hp"] -= dano_e
                    st.session_state.log_combate.append(f"🩸 {ene['nombre']} atacó con **{dano_e}** de daño.")
            recargar()

        if b3.button("🧪 Poción HP", key="btn_bat_poc"):
            if j["pociones_hp"] > 0:
                j["pociones_hp"] -= 1
                j["hp"] = min(j["hp_max"], j["hp"] + 50)
                st.session_state.log_combate.append("🧪 Curaste **50 HP**.")
            recargar()

        if b4.button("🏃 Huir", key="btn_bat_huir"):
            st.session_state.escena = "hub"
            recargar()

        st.divider()
        for log in reversed(st.session_state.log_combate[-4:]):
            st.markdown(f"<div class='combat-log'>{log}</div>", unsafe_allow_html=True)

        if ene["hp"] <= 0:
            st.success(f"🏆 ¡HAS DERROTADO A {ene['nombre'].upper()}!")
            j["xp"] += ene["xp"]
            j["oro"] += ene["oro"]
            subir_nivel_check()
            if st.button("Regresar a la Ciudad", key="btn_vic_back"):
                st.session_state.escena = "hub"
                recargar()
                
        elif j["hp"] <= 0:
            st.error("💀 HAS SIDO DERROTADO...")
            if st.button("🔄 Reiniciar Aventura", key="btn_der_back"):
                st.session_state.clear()
                recargar()
