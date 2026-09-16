import streamlit as st
import random

st.set_page_config(page_title="Chronicles of Eldoria RPG", page_icon="⚔️", layout="wide")

# Estilos visuales Dark Fantasy
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .npc-box { background-color: #1a1c23; border: 1px solid #343b4f; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
    .combat-log { background-color: #1e222d; padding: 10px; border-radius: 6px; border-left: 4px solid #f39c12; }
    </style>
""", unsafe_allow_html=True)

# DATOS DE CLASES CON IMÁGENES
CLASES = {
    "Guerrero 🛡️": {
        "hp_max": 160, "mana_max": 30, "atq": 18, "def": 10, 
        "habilidad": "Golpe de Escudo (20 MP)",
        "img": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=500"
    },
    "Mago 🔮": {
        "hp_max": 95, "mana_max": 110, "atq": 26, "def": 4, 
        "habilidad": "Bola de Fuego (30 MP)",
        "img": "https://images.unsplash.com/photo-1514539079130-25950c84af65?w=500"
    },
    "Pícaro 🗡️": {
        "hp_max": 115, "mana_max": 50, "atq": 22, "def": 6, 
        "habilidad": "Ataque Furtivo (25 MP)",
        "img": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500"
    }
}

# DATOS DE ENEMIGOS CON IMÁGENES
ENEMIGOS = {
    "Bosque": [
        {"nombre": "Goblin Silvestre", "hp_max": 55, "hp": 55, "atq": 12, "xp": 45, "oro": 30, "img": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=500"},
        {"nombre": "Lobo de Sombras", "hp_max": 70, "hp": 70, "atq": 16, "xp": 60, "oro": 35, "img": "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?w=500"}
    ],
    "Mazmorra": [
        {"nombre": "Esqueleto Guerrero", "hp_max": 110, "hp": 110, "atq": 22, "xp": 95, "oro": 65, "img": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500"},
        {"nombre": "Orco Devastador", "hp_max": 150, "hp": 150, "atq": 28, "xp": 140, "oro": 100, "img": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=500"}
    ],
    "Jefe": [
        {"nombre": "Rey Demonio Malakor", "hp_max": 350, "hp": 350, "atq": 40, "xp": 600, "oro": 600, "img": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=500"}
    ]
}

# INICIALIZACIÓN
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
        st.toast(f"⭐ ¡NIVEL {j['nivel']} ALCANZADO!", icon="🎉")

def iniciar_combate(zona):
    enemigo_base = random.choice(ENEMIGOS[zona])
    st.session_state.enemigo = enemigo_base.copy()
    st.session_state.log_combate = [f"⚔️ ¡Un {enemigo_base['nombre']} te bloquea el paso!"]
    st.session_state.escena = "combate"

# === CREACIÓN DE PERSONAJE ===
if st.session_state.escena == "creacion":
    st.title("⚔️ CHRONICLES OF ELDORIA RPG")
    st.write("### Crea a tu Leyenda")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        nombre = st.text_input("Nombre del Héroe:", value="Aventurero")
        clase_sel = st.selectbox("Clase:", list(CLASES.keys()))
        datos = CLASES[clase_sel]
        
        st.write(f"❤️ **Vida:** {datos['hp_max']} | 🔷 **Maná:** {datos['mana_max']}")
        st.write(f"⚔️ **Ataque:** {datos['atq']} | 🛡️ **Defensa:** {datos['def']}")
        st.write(f"✨ **Habilidad:** {datos['habilidad']}")
        
        if st.button("🚀 Comenzar la Aventura"):
            st.session_state.jugador = {
                "nombre": nombre, "clase": clase_sel, "nivel": 1, "xp": 0, "xp_siguiente": 100,
                "hp_max": datos["hp_max"], "hp": datos["hp_max"],
                "mana_max": datos["mana_max"], "mana": datos["mana_max"],
                "atq": datos["atq"], "def": datos["def"], "oro": 60,
                "pociones_hp": 2, "pociones_mana": 1, "equipo": "Ropas Simples",
                "img": datos["img"], "mision_activa": False, "mision_completada": False
            }
            st.session_state.escena = "hub"
            st.rerun()

    with col2:
        st.image(datos["img"], caption=f"Retrato de {clase_sel}", use_container_width=True)

# === INTERFAZ PRINCIPAL Y BARRA LATERAL ===
else:
    j = st.session_state.jugador
    
    with st.sidebar:
        st.image(j["img"], use_container_width=True)
        st.header(f"👤 {j['nombre']}")
        st.caption(f"{j['clase']} | Nivel {j['nivel']}")
        
        st.progress(max(0.0, min(1.0, j["hp"] / j["hp_max"])), text=f"❤️ HP: {j['hp']}/{j['hp_max']}")
        st.progress(max(0.0, min(1.0, j["mana"] / j["mana_max"])), text=f"🔷 MP: {j['mana']}/{j['mana_max']}")
        st.progress(max(0.0, min(1.0, j["xp"] / j["xp_siguiente"])), text=f"⭐ XP: {j['xp']}/{j['xp_siguiente']}")
        
        st.divider()
        c1, c2 = st.columns(2)
        c1.metric("⚔️ ATQ", j["atq"])
        c2.metric("🛡️ DEF", j["def"])
        
        st.write(f"💰 **Oro:** {j['oro']}")
        st.write(f"🧪 **Pociones HP:** {j['pociones_hp']} | 🔷 **MP:** {j['pociones_mana']}")
        st.caption(f"🛡️ **Equipo:** {j['equipo']}")

    # === CIUDAD PRINCIPAL (HUB) ===
    if st.session_state.escena == "hub":
        st.title("🏰 Ciudad Antigua de Oakhaven")
        st.image("https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1000", height=250, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🍺 La Taberna de Brak")
            st.write("Habla con el tabernero para descansar o pedir misiones.")
            if st.button("Entrar a la Taberna"):
                st.session_state.escena = "taberna"
                st.rerun()

        with col2:
            st.subheader("🛒 El Mercado de Gideon")
            st.write("Compra armas, armaduras y elixires mágicos.")
            if st.button("Entrar al Mercado"):
                st.session_state.escena = "tienda"
                st.rerun()

        with col3:
            st.subheader("🔮 La Torre del Sabio")
            st.write("Obtén bendiciones de magia ancestral.")
            if st.button("Visitar al Sabio"):
                st.session_state.escena = "sabio"
                st.rerun()

        st.divider()
        st.subheader("🗺️ Seleccionar Zona de Batalla")
        cz1, cz2, cz3 = st.columns(3)
        if cz1.button("🌲 Bosque Silvestre (Fácil)"):
            iniciar_combate("Bosque")
            st.rerun()
        if cz2.button("🏛️ Mazmorra Maldita (Medio)"):
            iniciar_combate("Mazmorra")
            st.rerun()
        if cz3.button("🐉 Guarida del Rey Demonio (JEFE)", type="primary"):
            iniciar_combate("Jefe")
            st.rerun()

    # === NPC 1: LA TABERNA (MISIONES Y SALUD) ===
    elif st.session_state.escena == "taberna":
        st.title("🍺 La Taberna del Jabalí Dorado")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image("https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=400", caption="Brak, el Tabernero")
        with c2:
            st.markdown("<div class='npc-box'><b>Brak:</b> <i>'¡Salud, aventurero! Un buen trago cura cualquier herida, pero si buscas oro, tengo trabajo para ti.'</i></div>", unsafe_allow_html=True)
            
            if st.button("🛌 Descansar y Recuperar Salud (15 💰)"):
                if j["oro"] >= 15:
                    j["oro"] -= 15
                    j["hp"], j["mana"] = j["hp_max"], j["mana_max"]
                    st.success("¡Te has curado por completo!")
                    st.rerun()
                else:
                    st.error("No tienes suficiente oro.")

            if not j["mision_activa"] and not j["mision_completada"]:
                if st.button("📜 Aceptar Misión: Cacería de Monstruos"):
                    j["mision_activa"] = True
                    st.success("¡Misión Aceptada! Derrota a cualquier enemigo para cobrar tu recompensa.")
                    st.rerun()
            elif j["mision_activa"] and not j["mision_completada"]:
                st.info("📜 **Misión Activa:** Derrota a un enemigo en batalla.")
                if st.button("🎁 Entregar Misión (Requiere 1 Victoria)"):
                    j["oro"] += 80
                    j["xp"] += 50
                    j["mision_activa"] = False
                    j["mision_completada"] = True
                    subir_nivel_check()
                    st.balloons()
                    st.success("¡Misión Completada! Recompensa: +80 Oro, +50 XP")
                    st.rerun()
            else:
                st.write("✅ *Has completado todas las misiones de la taberna por hoy.*")
                
        if st.button("⬅️ Volver a la Ciudad"):
            st.session_state.escena = "hub"
            st.rerun()

    # === NPC 2: LA TIENDA ===
    elif st.session_state.escena == "tienda":
        st.title("🛒 El Mercado de Gideon")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image("https://images.unsplash.com/photo-1555680202-c86f0e12f086?w=400", caption="Gideon el Mercader")
        with c2:
            st.markdown("<div class='npc-box'><b>Gideon:</b> <i>'Solo el mejor acero para los verdaderos héroes. ¿Qué te interesa?'</i></div>", unsafe_allow_html=True)
            
            t1, t2 = st.columns(2)
            if t1.button("🧪 Poción HP (+50 HP) - 25 💰"):
                if j["oro"] >= 25:
                    j["oro"] -= 25
                    j["pociones_hp"] += 1
                    st.success("Poción comprada.")
                    st.rerun()
            if t2.button("🔷 Poción MP (+40 MP) - 20 💰"):
                if j["oro"] >= 20:
                    j["oro"] -= 20
                    j["pociones_mana"] += 1
                    st.success("Poción comprada.")
                    st.rerun()
                    
            if st.button("⚔️ Espada Runica (+10 ATQ) - 90 💰"):
                if j["oro"] >= 90 and "Espada" not in j["equipo"]:
                    j["oro"] -= 90
                    j["atq"] += 10
                    j["equipo"] = "Espada Rúnica"
                    st.success("¡Arma equipada!")
                    st.rerun()
                    
            if st.button("🛡️ Coraza Mitril (+8 DEF) - 110 💰"):
                if j["oro"] >= 110 and "Mitril" not in j["equipo"]:
                    j["oro"] -= 110
                    j["def"] += 8
                    j["equipo"] += " + Coraza Mitril"
                    st.success("¡Armadura equipada!")
                    st.rerun()

        if st.button("⬅️ Volver a la Ciudad"):
            st.session_state.escena = "hub"
            st.rerun()

    # === NPC 3: EL SABIO (POTENCIADORES) ===
    elif st.session_state.escena == "sabio":
        st.title("🔮 La Santuario del Sabio Eldrin")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image("https://images.unsplash.com/photo-1563089145-599997674d42?w=400", caption="Eldrin el Sabio")
        with c2:
            st.markdown("<div class='npc-box'><b>Eldrin:</b> <i>'La magia antigua puede moldear tu destino... por un precio justo.'</i></div>", unsafe_allow_html=True)
            
            if st.button("✨ Ritual de Fuerza (+4 ATQ permanente) - 75 💰"):
                if j["oro"] >= 75:
                    j["oro"] -= 75
                    j["atq"] += 4
                    st.success("¡Ataque aumentado permanentemente!")
                    st.rerun()
            if st.button("🛡️ Bendición Arcana (+4 DEF permanente) - 75 💰"):
                if j["oro"] >= 75:
                    j["oro"] -= 75
                    j["def"] += 4
                    st.success("¡Defensa aumentada permanentemente!")
                    st.rerun()

        if st.button("⬅️ Volver a la Ciudad"):
            st.session_state.escena = "hub"
            st.rerun()

    # === COMBATE VISUAL E INTERACTIVO ===
    elif st.session_state.escena == "combate":
        ene = st.session_state.enemigo
        st.title(f"⚔️ BATALLA: {j['nombre']} vs {ene['nombre']}")
        
        col_img, col_stats = st.columns([1, 2])
        with col_img:
            st.image(ene["img"], caption=ene["nombre"], use_container_width=True)
        with col_stats:
            st.subheader(f"👾 {ene['nombre']}")
            st.progress(max(0.0, min(1.0, ene["hp"] / ene["hp_max"])), text=f"Salud Enemiga: {ene['hp']}/{ene['hp_max']} HP")
            
            st.divider()
            b1, b2, b3, b4 = st.columns(4)
            
            # ATAQUE BÁSICO
            if b1.button("⚔️ Atacar"):
                critico = random.random() < 0.2
                dano = (j["atq"] * 2 if critico else j["atq"]) + random.randint(-2, 4)
                dano = max(1, dano)
                ene["hp"] -= dano
                txt_crit = " 💥 ¡GOLPE CRÍTICO!" if critico else ""
                st.session_state.log_combate.append(f"🗡️ Infligiste **{dano}** de daño.{txt_crit}")
                
                if ene["hp"] > 0:
                    dano_e = max(1, ene["atq"] - j["def"] + random.randint(-2, 2))
                    j["hp"] -= dano_e
                    st.session_state.log_combate.append(f"🩸 {ene['nombre']} contraatacó con **{dano_e}** de daño.")
                st.rerun()

            # HABILIDAD
            if b2.button("✨ Habilidad"):
                costo = 20 if "Guerrero" in j["clase"] else (30 if "Mago" in j["clase"] else 25)
                if j["mana"] >= costo:
                    j["mana"] -= costo
                    dano_mag = int(j["atq"] * 1.9) + random.randint(4, 10)
                    ene["hp"] -= dano_mag
                    st.session_state.log_combate.append(f"✨ ¡Usaste tu habilidad e infligiste **{dano_mag}** de daño mágico!")
                    
                    if ene["hp"] > 0:
                        dano_e = max(1, ene["atq"] - j["def"] + random.randint(-2, 2))
                        j["hp"] -= dano_e
                        st.session_state.log_combate.append(f"🩸 {ene['nombre']} atacó con **{dano_e}** de daño.")
                else:
                    st.toast("❌ ¡Sin suficiente Maná!", icon="⚠️")
                st.rerun()

            # POCIÓN
            if b3.button("🧪 Poción HP"):
                if j["pociones_hp"] > 0:
                    j["pociones_hp"] -= 1
                    j["hp"] = min(j["hp_max"], j["hp"] + 50)
                    st.session_state.log_combate.append("🧪 Curaste **50 HP**.")
                    if ene["hp"] > 0:
                        dano_e = max(1, ene["atq"] - j["def"])
                        j["hp"] -= dano_e
                        st.session_state.log_combate.append(f"🩸 {ene['nombre']} atacó con **{dano_e}** de daño.")
                else:
                    st.toast("❌ Sin pociones.", icon="⚠️")
                st.rerun()

            # HUIR
            if b4.button("🏃 Huir"):
                st.session_state.escena = "hub"
                st.rerun()

        # Registro de combate
        st.divider()
        st.write("**Historial del Combate:**")
        for log in reversed(st.session_state.log_combate[-4:]):
            st.markdown(f"<div class='combat-log'>{log}</div><br>", unsafe_allow_html=True)

        # Victoria / Derrota
        if ene["hp"] <= 0:
            st.balloons()
            st.success(f"🏆 ¡HAS DERROTADO A {ene['nombre'].upper()}!")
            j["xp"] += ene["xp"]
            j["oro"] += ene["oro"]
            subir_nivel_check()
            if st.button("Regresar a la Ciudad"):
                st.session_state.escena = "hub"
                st.rerun()
                
        elif j["hp"] <= 0:
            st.error("💀 HAS SIDO DERROTADO EN BATALLA...")
            if st.button("🔄 Reiniciar Aventura"):
                st.session_state.clear()
                st.rerun()
