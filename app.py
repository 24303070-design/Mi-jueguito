import json
import os
import random
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="GAME OF ATIZAPAN", page_icon="⚔️", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 6px; font-weight: bold; }
    .status-card { background-color: #1e222d; padding: 12px; border-radius: 8px; border-left: 4px solid #3498db; }
    .map-cell { background-color: #1a1c23; border: 1px solid #343b4f; padding: 10px; text-align: center; border-radius: 5px; }
    .map-cell-player { background-color: #2c3e50; border: 2px solid #f39c12; padding: 10px; text-align: center; border-radius: 5px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def recargar():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

# ==========================================
# 1. ARQUITECTURA DE CLASES (POO Y HERENCIA)
# ==========================================

class Entidad:
    """Clase Base que define la lógica global de combate."""
    def __init__(self, nombre: str, hp: int, atq: int, defensa: int):
        self.nombre = nombre
        self.hp = hp
        self.hp_max = hp
        self.atq = atq
        self.defensa = defensa

    def esta_vivo(self) -> bool:
        return self.hp > 0

    def recibir_dano(self, cantidad: int) -> int:
        dano_real = max(1, cantidad - self.defensa)
        self.hp = max(0, self.hp - dano_real)
        return dano_real


class Jugador(Entidad):
    """Clase Jugador con estado dinámico, posición 2D e historial para telemetría."""
    def __init__(self, nombre: str, clase: str):
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

    def mover(self, dx: int, dy: int, limite: int = 3):
        self.pos_x = max(0, min(limite - 1, self.pos_x + dx))
        self.pos_y = max(0, min(limite - 1, self.pos_y + dy))

    def ganar_xp(self, cantidad: int) -> bool:
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

    def a_dict(self) -> dict:
        """Serialización del objeto a diccionario."""
        return {
            "nombre": self.nombre, "clase": self.clase, "nivel": self.nivel,
            "xp": self.xp, "xp_siguiente": self.xp_siguiente, "hp": self.hp,
            "hp_max": self.hp_max, "atq": self.atq, "defensa": self.defensa,
            "oro": self.oro, "pos_x": self.pos_x, "pos_y": self.pos_y,
            "historial_dano": self.historial_dano
        }

    @classmethod
    def desde_dict(cls, data: dict):
        """Deserialización e instanciación de clase."""
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
    """Clase de Enemigos derivada de Entidad."""
    def __init__(self, nombre: str, hp: int, atq: int, defensa: int, xp: int, oro: int, icono: str):
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
    def guardar(cls, jugador: Jugador):
        with open(cls.ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(jugador.a_dict(), f, indent=4)

    @classmethod
    def cargar(cls) -> Jugador | None:
        if os.path.exists(cls.ARCHIVO):
            try:
                with open(cls.ARCHIVO, "r", encoding="utf-8") as f:
                    return Jugador.desde_dict(json.load(f))
            except Exception:
                return None
        return None

# ==========================================
# 3. TELEMETRÍA Y GRÁFICOS (MATPLOTLIB)
# ==========================================

def renderizar_grafica_rendimiento(historial):
    fig, ax = plt.subplots(figsize=(6, 2.2))
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#1e222d')
    
    if historial:
        ax.plot(historial, color='#f39c12', marker='o', linewidth=2, label="Daño por Turno")
    else:
        ax.plot([0], [0], color='#f39c12')
        
    ax.set_title("Análisis Estadístico de Combate (DPS)", color="white", fontsize=10)
    ax.set_xlabel("Turnos", color="white", fontsize=8)
    ax.set_ylabel("Daño Infligido", color="white", fontsize=8)
    ax.tick_params(colors='white', labelsize=8)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend(facecolor='#1e222d', edgecolor='white', labelcolor='white', fontsize=8)
    
    st.pyplot(fig)

# ==========================================
# 4. CONFIGURACIÓN DEL MAPA 2D
# ==========================================

MATRIZ_MAPA = [
    [{"nombre": "🏰 Ciudad Oakhaven", "tipo": "seguro"}, {"nombre": "🌲 Bosque Norte", "tipo": "combate", "zona": "Bosque"}, {"nombre": "🕳️ Cueva Profunda", "tipo": "combate", "zona": "Mazmorra"}],
    [{"nombre": "🛒 Mercado Central", "tipo": "tienda"}, {"nombre": "🏛️ Ruinas Antiguas", "tipo": "combate", "zona": "Bosque"}, {"nombre": "💀 Cementerio", "tipo": "combate", "zona": "Mazmorra"}],
    [{"nombre": "🌾 Pradera Sur", "tipo": "combate", "zona": "Bosque"}, {"nombre": "🏰 Fortaleza Abandonada", "tipo": "combate", "zona": "Mazmorra"}, {"nombre": "🐲 Trono Demonio", "tipo": "jefe", "zona": "Jefe"}]
]

ENEMIGOS_DB = {
    "Bosque": [
        lambda: Enemigo("Goblin Explorador", 50, 12, 2, 40, 25, "👺"),
        lambda: Enemigo("Lobo Ferotaz", 65, 15, 3, 50, 30, "🐺")
    ],
    "Mazmorra": [
        lambda: Enemigo("Esqueleto Soldado", 100, 20, 5, 90, 60, "💀"),
        lambda: Enemigo("Orco Guerreador", 140, 25, 8, 130, 90, "👹")
    ],
    "Jefe": [
        lambda: Enemigo("Rey Demonio Malakor", 320, 38, 12, 500, 500, "🐲")
    ]
}

# ==========================================
# 5. CONTROLADOR PRINCIPAL Y SESIÓN
# ==========================================

if "jugador" not in st.session_state:
    st.session_state.jugador = None
if "enemigo" not in st.session_state:
    st.session_state.enemigo = None
if "log_combate" not in st.session_state:
    st.session_state.log_combate = []

# PANTALLA: CREACIÓN O CARGA DE USUARIO
if st.session_state.jugador is None:
    st.title("🛡️ Sistema de Gestión RPG: Chronicles of Eldoria")
    st.caption("Motor de Juego basado en POO, Persistencia en JSON y Análisis Estadístico.")
    
    tab1, tab2 = st.tabs(["✨ Crear Nueva Partida", "📂 Cargar Partida de Disco"])
    
    with tab1:
        nombre = st.text_input("Nombre de la Entidad Jugador:", value="Héroe")
        clase = st.selectbox("Seleccionar Clase de Personaje:", ["Guerrero 🛡️", "Mago 🔮", "Pícaro 🗡️"])
        if st.button("Inicializar Instancia del Jugador", key="btn_crear"):
            st.session_state.jugador = Jugador(nombre, clase)
            GestorPersistencia.guardar(st.session_state.jugador)
            recargar()

    with tab2:
        if st.button("Cargar 'partida.json' desde Almacenamiento Local", key="btn_cargar"):
            j_cargado = GestorPersistencia.cargar()
            if j_cargado:
                st.session_state.jugador = j_cargado
                st.success("¡Objeto instanciado correctamente desde el JSON!")
                recargar()
            else:
                st.error("No se encontró un archivo 'partida.json' válido.")

# PANTALLA PRINCIPAL DEL JUEGO
else:
    j = st.session_state.jugador
    
    # Barra Lateral
    with st.sidebar:
        st.header(f"👤 {j.nombre}")
        st.caption(f"Clase: {j.clase} | Nivel {j.nivel}")
        
        st.progress(max(0.0, min(1.0, j.hp / j.hp_max)), text=f"❤️ HP: {j.hp}/{j.hp_max}")
        st.progress(max(0.0, min(1.0, j.xp / j.xp_siguiente)), text=f"⭐ XP: {j.xp}/{j.xp_siguiente}")
        
        st.write(f"⚔️ **Ataque:** {j.atq} | 🛡️ **Defensa:** {j.defensa}")
        st.write(f"💰 **Oro:** {j.oro} | 📍 **Posición 2D:** ({j.pos_x}, {j.pos_y})")
        st.divider()
        
        c1, c2 = st.columns(2)
        if c1.button("💾 Guardar JSON", key="sb_save"):
            GestorPersistencia.guardar(j)
            st.toast("Progreso guardado en partida.json", icon="💾")
        if c2.button("🚪 Salir", key="sb_exit"):
            st.session_state.jugador = None
            recargar()

    # Si estamos en estado de combate
    if st.session_state.enemigo is not None:
        ene = st.session_state.enemigo
        st.title(f"⚔️ Módulo de Combate: {j.nombre} vs {ene.icono} {ene.nombre}")
        
        st.progress(max(0.0, min(1.0, ene.hp / ene.hp_max)), text=f"Salud Enemigo: {ene.hp}/{ene.hp_max} HP")
        
        b1, b2, b3 = st.columns(3)
        if b1.button("⚔️ Ejecutar Ataque Básico", key="cb_atq"):
            dano = max(1, j.atq + random.randint(-3, 4))
            dano_recibido = ene.recibir_dano(dano)
            j.historial_dano.append(dano_recibido)
            st.session_state.log_combate.append(f"🗡️ Infligiste **{dano_recibido}** de daño a {ene.nombre}.")
            
            if ene.esta_vivo():
                d_ene = ene.atq + random.randint(-2, 2)
                d_rec = j.recibir_dano(d_ene)
                st.session_state.log_combate.append(f"💥 {ene.nombre} te infligió **{d_rec}** de daño.")
            recargar()

        if b2.button("🧪 Consumir Poción (30 HP - 20 💰)", key="cb_poc"):
            if j.oro >= 20:
                j.oro -= 20
                j.hp = min(j.hp_max, j.hp + 40)
                st.session_state.log_combate.append("🧪 Te has curado 40 HP.")
            recargar()

        if b3.button("🏃 Retirada Táctica", key="cb_huir"):
            st.session_state.enemigo = None
            st.session_state.log_combate = []
            recargar()

        st.divider()
        col_log, col_graf = st.columns([1, 1])
        with col_log:
            st.subheader("Registro de Batalla")
            for log in reversed(st.session_state.log_combate[-4:]):
                st.markdown(f"<div class='status-card'>{log}</div><br>", unsafe_allow_html=True)
                
        with col_graf:
            renderizar_grafica_rendimiento(j.historial_dano)

        if not ene.esta_vivo():
            st.balloons()
            st.success(f"🏆 ¡Enemigo Neutralizado! Recompensas: +{ene.xp} XP, +{ene.oro} Oro")
            j.oro += ene.oro
            subio = j.ganar_xp(ene.xp)
            if subio:
                st.toast("¡Nivel Aumentado!", icon="⭐")
            st.session_state.enemigo = None
            GestorPersistencia.guardar(j)
            if st.button("Continuar Exploración", key="btn_post_vic"):
                recargar()

        elif not j.esta_vivo():
            st.error("💀 La entidad Jugador ha sido destruida.")
            if st.button("Cargar Último Save", key="btn_post_der"):
                st.session_state.jugador = GestorPersistencia.cargar()
                st.session_state.enemigo = None
                recargar()

    # Modo Exploración en Matriz 2D
    else:
        st.title("🗺️ Matriz de Navegación Espacial 2D")
        
        celda_actual = MATRIZ_MAPA[j.pos_y][j.pos_x]
        st.markdown(f"<div class='status-card'>Ubicación actual: <b>{celda_actual['nombre']}</b> | Coordenadas: [{j.pos_x}, {j.pos_y}]</div><br>", unsafe_allow_html=True)

        # Renderizado Visual de la Matriz 3x3
        for y in range(3):
            cols = st.columns(3)
            for x in range(3):
                info_celda = MATRIZ_MAPA[y][x]
                with cols[x]:
                    if x == j.pos_x and y == j.pos_y:
                        st.markdown(f"<div class='map-cell-player'>📍 {info_celda['nombre']}<br>(TÚ)</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='map-cell'>{info_celda['nombre']}</div>", unsafe_allow_html=True)
        st.divider()

        # Controles de Movimiento Vectorial
        st.subheader("Control Vectorial de Posición")
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

        # Lógica por Tipo de Celda
        if celda_actual["tipo"] == "seguro":
            st.info("🏡 Zona Segura: Puedes descansar para regenerar tus atributos.")
            if st.button("🛌 Descansar en la Ciudad (10 💰)", key="act_descansar"):
                if j.oro >= 10:
                    j.oro -= 10
                    j.hp = j.hp_max
                    GestorPersistencia.guardar(j)
                    st.success("Salud completamente restaurada.")
                    recargar()

        elif celda_actual["tipo"] == "tienda":
            st.info("🛒 Tienda Local: Mejora tu equipo base.")
            if st.button("⚔️ Comprar Mejora de Arma (+5 ATQ) - 50 💰", key="act_tienda"):
                if j.oro >= 50:
                    j.oro -= 50
                    j.atq += 5
                    GestorPersistencia.guardar(j)
                    st.success("¡Atributo de Ataque incrementado!")
                    recargar()

        elif celda_actual["tipo"] in ["combate", "jefe"]:
            st.warning("⚠️ Zona Hostil Detectada.")
            if st.button("⚔️ Iniciar Protocolo de Combate", key="act_combate"):
                gen_enemigo = random.choice(ENEMIGOS_DB[celda_actual["zona"]])
                st.session_state.enemigo = gen_enemigo()
                st.session_state.log_combate = [f"Combate iniciado contra {st.session_state.enemigo.nombre}"]
                recargar()

        st.subheader("Telemetría Acumulada del Jugador")
        renderizar_grafica_rendimiento(j.historial_dano)
