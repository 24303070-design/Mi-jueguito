import streamlit as st

st.set_page_config(page_title="El Castillo del Dragón", page_icon="⚔️")

if "hp" not in st.session_state:
    st.session_state.hp = 100
    st.session_state.oro = 60
    st.session_state.inventario = []
    st.session_state.escena = "inicio"

st.title("⚔️ La Leyenda del Dragón")
col_hp, col_oro = st.columns(2)
col_hp.metric("❤️ Vida", f"{st.session_state.hp}/100")
col_oro.metric("💰 Oro", f"{st.session_state.oro}")
st.write(f"📦 **Inventario:** {', '.join(st.session_state.inventario) if st.session_state.inventario else 'Vacío'}")
st.divider()

if st.session_state.escena == "inicio":
    st.image("https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=600")
    st.subheader("📜 Capítulo 1: La Taberna")
    col1, col2 = st.columns(2)
    if col1.button("🛒 Visitar Mercader"):
        st.session_state.escena = "tienda"
        st.rerun()
    if col2.button("🚶 Salir al Camino"):
        st.session_state.escena = "encrucijada"
        st.rerun()

elif st.session_state.escena == "tienda":
    st.image("https://images.unsplash.com/photo-1555680202-c86f0e12f086?w=600")
    st.subheader("🛒 El Mercado")
    if st.button("⚔️ Comprar Espada - 40💰"):
        if st.session_state.oro >= 40 and "Espada" not in st.session_state.inventario:
            st.session_state.oro -= 40
            st.session_state.inventario.append("Espada")
            st.rerun()
    if st.button("🚪 Salir al Camino"):
        st.session_state.escena = "encrucijada"
        st.rerun()

elif st.session_state.escena == "encrucijada":
    st.image("https://images.unsplash.com/photo-1448375240586-882707db888b?w=600")
    st.subheader("🗺️ La Encrucijada")
    if st.button("🐉 Enfrentar al Dragón"):
        if "Espada" in st.session_state.inventario:
            st.session_state.escena = "victoria"
        else:
            st.session_state.escena = "derrota"
        st.rerun()

elif st.session_state.escena == "victoria":
    st.image("https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=600")
    st.balloons()
    st.success("🏆 ¡Derrotaste al Dragón!")
    if st.button("🔄 Jugar de nuevo"):
        st.session_state.clear()
        st.rerun()

elif st.session_state.escena == "derrota":
    st.image("https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=600")
    st.error("💀 Sin espada, el Dragón te venció.")
    if st.button("🔄 Reintentar"):
        st.session_state.clear()
        st.rerun()
