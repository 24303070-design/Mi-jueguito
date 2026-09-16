import json
import os
import random
import streamlit as st

st.set_page_config(page_title="GAME OF ATIZAPAN", page_icon="⚔️", layout="wide")

def recargar():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

# ==========================================
# 1. ARQUITECTURA DE CLASES (POO Y HERENCIA)
# ==========================================

class Entidad:
    """Clase Base para gestión de combate y estados."""
    def __init__(self, nombre, hp, atq, defensa):
        self.nombre = nombre
        self.hp = hp
        self.hp_max = hp
        self.atq = atq
        self.defensa = defensa

    def esta_vivo(self):
        return self.hp > 0

    def recibir_dano(self, cantidad):
        dano_real = max(1, cantidad - self.defensa)
        self.hp = max(0, self.hp - dano_real)
        return dano_real


class Jugador(Entidad):
    """Clase Jugador derivada de Entidad (Herencia + Estado Persistente)."""
    def __init__(self, nombre, clase):
        stats = {
            "Guerrero 🛡️": (170, 22, 10),
            "Mago 🔮": (100, 30, 4),
            "Pícaro 🗡️": (125, 26, 6)
        }.get(clase, (120, 20, 5))
        
        super().__init__(nombre, stats[0], stats[1], stats[2])
        self.clase = clase
        self.nivel = 1
        self.xp = 0
        self.xp_siguiente = 100
        self.oro = 60
        self.pos_x = 0
        self.pos_y = 0
        self.historial_dano = []

    def mover(self, dx, dy, limite=3):
        self.pos_x = max(0, min(limite - 1, self.pos_x + dx))
        self.pos_y = max(0, min(limite - 1, self.pos_y + dy))

    def ganar_xp(self, cantidad):
        self.xp += cantidad
        if self.xp >= self.xp_siguiente:
            self.nivel += 1
            self.xp -= self.xp_siguiente
            self.xp_siguiente = int(self.xp_siguiente * 1.5)
            self.hp_max += 25
            self.hp = self.hp_max
            self.atq += 5
            self.defensa += 2
            return True
        return False

    def a_dict(self):
        """Serialización a diccionario."""
        return {
            "nombre": self.nombre, "clase": self.clase, "nivel": self.nivel,
            "xp": self.xp, "xp_siguiente": self.xp_siguiente, "hp": self.hp,
            "hp_max": self.hp_max, "atq": self.atq, "defensa": self.defensa,
            "oro": self.oro, "pos_x": self.pos_x, "pos_y": self.pos_y,
            "historial_dano": self.historial_dano
        }

    @classmethod
    def desde_dict(cls, data):
        """Deserialización desde diccionario."""
        j = cls(data["nombre"], data["clase"])
        j.nivel = data["nivel"]
        j.xp = data["xp"]
        j.xp_siguiente = data["xp_siguiente"]
        j.hp = data["hp"]
        j.hp_max = data["hp_max"]
        j.atq = data["atq"]
        j.defensa = data["defensa"]
        j.oro = data["oro"]
        j.pos_x = data["pos_x"]
        j.pos_y = data["pos_y"]
        j.historial_dano = data.get("historial_dano", [])
        return j


class Enemigo(Entidad):
    """Clase Enemigo derivada de Entidad."""
    def __init__(self, nombre, hp, atq, defensa, xp, oro, icono):
        super().__init__(nombre, hp, atq, defensa)
        self.xp = xp
        self.oro = oro
        self.icono = icono


# ==========================================
# 2. SISTEMA DE PERSISTENCIA (FILE I/O JSON)
# ==========================================

class GestorPersistencia:
    ARCHIVO = "partida.json"

    @classmethod
    def guardar(cls, jugador):
        with open(cls.ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(jugador.a_dict(), f, indent=4)

    @classmethod
    def cargar(cls):
        if os.path.exists(cls.ARCHIVO):
            try:
                with open(cls.ARCHIVO, "r", encoding="utf-8") as f:
                    return Jugador.desde_dict(json.load(f))
            except Exception:
                return None
        return None

# ==========================================
# 3. MATRIZ DE NAVEGACIÓN 2D
# ==========================================

MATRIZ_MAPA = [
    [{"nombre": "🏰 Ciudad Oakhaven", "tipo": "seguro"}, {"nombre": "🌲 Bosque Norte", "tipo": "combate", "zona": "Bosque"}, {"nombre": "🕳️ Cueva Profunda", "tipo": "combate", "zona": "Mazmorra"}],
    [{"nombre": "🛒 Mercado Central", "tipo": "tienda"}, {"nombre": "🏛️ Ruinas Antiguas", "tipo": "combate", "zona": "Bosque"}, {"nombre": "💀 Cementerio", "tipo": "combate", "zona": "Mazmorra"}],
    [{"nombre": "🌾 Pradera Sur", "tipo": "combate", "zona": "Bosque"}, {"nombre": "🏰 Fortaleza Abandonada", "tipo": "combate", "zona": "Mazmorra"}, {"nombre": "🐲 Trono Demonio", "tipo": "jefe", "zona": "Jefe"}]
]

ENEMIGOS_DB = {
    "Bosque": [
        lambda: Enemigo("Goblin Explorador", 50, 12, 2, 40, 25, "👺"),
        lambda: Enemigo("Lobo Feroz", 65, 15, 3, 50, 30, "🐺")
    ],
    "Mazmorra": [
        lambda: Enemigo("Esqueleto Soldado", 100, 20, 5, 90, 60, "💀"),
        lambda: Enemigo("Orco Guerrero", 140, 25, 8, 130, 90, "👹")
    ],
    "Jefe": [
        lambda: Enemigo("Rey Demonio Malakor", 320, 38, 12, 500, 500, "🐲")
    ]
}

# ==========================================
# 4. CONTROLADOR DE SESIÓN Y UI
# ==========================================

if "jugador" not in st.session_state:
    st.session_state.jugador = None
if "enemigo" not in st.session_state:
    st.session_state.enemigo = None
if "log_combate" not in st.session_state:
    st.session_state.log_combate = []

# PANTALLA INICIAL: INICIALIZACIÓN / CARGA
if st.session_state.jugador is None:
    st.title("🛡️ Sistema RPG: Chronicles of Eldoria")
    st.caption("Backend en POO, Persistencia File I/O (JSON) y Control Matricial Vectorial.")
    
    tab1, tab2 = st.tabs(["✨ Crear Nueva Partida", "📂 Cargar Partida de Disco"])
    
    with tab1:
        nombre = st.text_input("Nombre del Jugador:", value="Héroe")
        clase = st.selectbox("Clase del Personaje:", ["Guerrero 🛡️", "Mago 🔮", "Pícaro 🗡️"])
        if st.button("Inicializar Instancia", key="btn_crear"):
            st.session_state.jugador = Jugador(nombre, clase)
            GestorPersistencia.guardar(st.session_state.jugador)
            recargar()

    with tab2:
        if st.button("Cargar desde 'partida.json'", key="btn_cargar"):
            j_cargado = GestorPersistencia.cargar()
            if j_cargado:
                st.session_state.jugador = j_cargado
                st.success("¡Instancia reconstruida exitosamente desde JSON!")
                recargar()
            else:
                st.error("No se encontró ningún archivo 'partida.json'.")

# PANTALLA PRINCIPAL
else:
    j = st.session_state.jugador
    
    with st.sidebar:
        st.header(f"👤 {j.nombre}")
        st.caption(f"Clase: {j.clase} | Nivel {j.nivel}")
        
        st.progress(max(0.0, min(1.0, j.hp / j.hp_max)), text=f"❤️ HP: {j.hp}/{j.hp_max}")
        st.progress(max(0.0, min(1.0, j.xp / j.xp_siguiente)), text=f"⭐ XP: {j.xp}/{j.xp_siguiente}")
        
        st.write(f"⚔️ **Ataque:** {j.atq} | 🛡️ **Defensa:** {j.defensa}")
        st.write(f"💰 **Oro:** {j.oro} | 📍 **Posición Vectorial:** ({j.pos_x}, {j.pos_y})")
        st.divider()
        
        c1, c2 = st.columns(2)
        if c1.button("💾 Guardar", key="sb_save"):
            GestorPersistencia.guardar(j)
            st.success("JSON actualizado.")
        if c2.button("🚪 Salir", key="sb_exit"):
            st.session_state.jugador = None
            recargar()

    # MÓDULO DE COMBATE
    if st.session_state.enemigo is not None:
        ene = st.session_state.enemigo
        st.title(f"⚔️ MÓDULO DE BATALLA: {j.nombre} vs {ene.icono} {ene.nombre}")
        
        st.progress(max(0.0, min(1.0, ene.hp / ene.hp_max)), text=f"Salud Enemigo: {ene.hp}/{ene.hp_max} HP")
        
        b1, b2, b3 = st.columns(3)
        if b1.button("⚔️ Ejecutar Ataque", key="cb_atq"):
            dano = max(1, j.atq + random.randint(-3, 4))
            dano_recibido = ene.recibir_dano(dano)
            j.historial_dano.append(dano_recibido)
            st.session_state.log_combate.append(f"🗡️ Infligiste **{dano_recibido}** de daño.")
            
            if ene.esta_vivo():
                d_ene = ene.atq + random.randint(-2, 2)
                d_rec = j.recibir_dano(d_ene)
                st.session_state.log_combate.append(f"💥 {ene.nombre} te infligió **{d_rec}** de daño.")
            recargar()

        if b2.button("🧪 Usar Poción (20 💰)", key="cb_poc"):
            if j.oro >= 20:
                j.oro -= 20
                j.hp = min(j.hp_max, j.hp + 40)
                st.session_state.log_combate.append("🧪 Curación aplicada (+40 HP).")
            recargar()

        if b3.button("🏃 Huir del Área", key="cb_huir"):
            st.session_state.enemigo = None
            st.session_state.log_combate = []
            recargar()

        st.divider()
        col_log, col_graf = st.columns([1, 1])
        with col_log:
            st.subheader("Historial de Combate")
            for log in reversed(st.session_state.log_combate[-4:]):
                st.markdown(f"• {log}")
                
        with col_graf:
            st.subheader("Telemetría de Daño (DPS)")
            if j.historial_dano:
                st.line_chart(j.historial_dano)
            else:
                st.caption("Ataca para visualizar la gráfica.")

        if not ene.esta_vivo():
            st.success(f"🏆 ¡Enemigo Eliminado! +{ene.xp} XP, +{ene.oro} Oro")
            j.oro += ene.oro
            j.ganar_xp(ene.xp)
            st.session_state.enemigo = None
            GestorPersistencia.guardar(j)
            if st.button("Continuar Nivel", key="btn_post_vic"):
                recargar()

        elif not j.esta_vivo():
            st.error("💀 La entidad Jugador ha sido destruida.")
            if st.button("Cargar Save de Disco", key="btn_post_der"):
                st.session_state.jugador = GestorPersistencia.cargar()
                st.session_state.enemigo = None
                recargar()

    # MÓDULO DE NAVEGACIÓN 2D
    else:
        st.title("🗺️ Matriz de Navegación 2D")
        
        celda_actual = MATRIZ_MAPA[j.pos_y][j.pos_x]
        st.info(f"📍 Posición Actual: **{celda_actual['nombre']}** | Coordenadas Cartesianas: `[{j.pos_x}, {j.pos_y}]`")

        # Renderizado de la matriz de botones visuales
        for y in range(3):
            cols = st.columns(3)
            for x in range(3):
                info_celda = MATRIZ_MAPA[y][x]
                with cols[x]:
                    if x == j.pos_x and y == j.pos_y:
                        st.write(f"👉 **[{info_celda['nombre']}]**")
                    else:
                        st.caption(f"{info_celda['nombre']}")
        st.divider()

        st.write("**Movimiento por Vectores:**")
        ctrl1, ctrl2, ctrl3, ctrl4 = st.columns(4)
        if ctrl1.button("⬆️ Norte (Y-1)", key="mov_n"):
            j.mover(0, -1); recargar()
        if ctrl2.button("⬇️ Sur (Y+1)", key="mov_s"):
            j.mover(0, 1); recargar()
        if ctrl3.button("⬅️ Oeste (X-1)", key="mov_o"):
            j.mover(-1, 0); recargar()
        if ctrl4.button("➡️ Este (X+1)", key="mov_e"):
            j.mover(1, 0); recargar()

        st.divider()

        # Acciones según tipo de casilla
        if celda_actual["tipo"] == "seguro":
            st.write("🏡 **Zona Segura:** Recupera salud por completo.")
            if st.button("🛌 Descansar (10 💰)", key="act_descansar"):
                if j.oro >= 10:
                    j.oro -= 10
                    j.hp = j.hp_max
                    GestorPersistencia.guardar(j)
                    st.success("Salud restaurada.")
                    recargar()

        elif celda_actual["tipo"] == "tienda":
            st.write("🛒 **Mercado Central:** Compra mejoras para tu entidad.")
            if st.button("⚔️ Aumentar Ataque (+5 ATQ) - 50 💰", key="act_tienda"):
                if j.oro >= 50:
                    j.oro -= 50
                    j.atq += 5
                    GestorPersistencia.guardar(j)
                    st.success("Atributo actualizado.")
                    recargar()

        elif celda_actual["tipo"] in ["combate", "jefe"]:
            st.warning("⚠️ **Zona de Peligro:** Enemigos detectados.")
            if st.button("⚔️ Iniciar Protocolo de Combate", key="act_combate"):
                gen_enemigo = random.choice(ENEMIGOS_DB[celda_actual["zona"]])
                st.session_state.enemigo = gen_enemigo()
                st.session_state.log_combate = [f"Combate iniciado contra {st.session_state.enemigo.nombre}"]
                recargar()

        if j.historial_dano:
            st.subheader("Telemetría de Daño Acumulada")
            st.line_chart(j.historial_dano)
