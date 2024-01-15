"""
Aplicación de registro de gastos con Streamlit.
main.py
Este script implementa una aplicación de registro de gastos utilizando Streamlit y SQLite.
"""
# Importar librerías
import sqlite3
from hashlib import sha256
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# Función para verificar el inicio de sesión
def verificar_inicio_sesion(usuario, contrasena):
    """
    Obtiene las credenciales de inicio
    de sesión del usuaRIO.
    """
    hashed_contrasena = sha256(contrasena.encode()).hexdigest()
    cursor.execute('SELECT * FROM usuarios WHERE usuario=? AND contrasena=?',
                (usuario, hashed_contrasena)
    )
    return cursor.fetchone()
# Función para agregar un nuevo usuario
def agregar_usuario(usuario, contrasena):
    """
    Crea un usuario nuevo en la base de datos.
    """
    hashed_contrasena = sha256(contrasena.encode()).hexdigest()
    cursor.execute('INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)',
                (usuario, hashed_contrasena)
    )
    conn.commit()
# Función para agregar un nuevo gasto
def agregar_gasto(usuario_id, nombre, categoria, monto, fecha):
    """
    Crea un gasto nuevo en la base de datos.
    """
    cursor.execute(
        'INSERT INTO gastos (usuario_id, nombre, categoria, monto, fecha) VALUES (?, ?, ?, ?, ?)',
        (usuario_id, nombre, categoria, monto, fecha)
    )
    conn.commit()
# Función para obtener los gastos de un usuario
def obtener_gastos(usuario_id):
    """
    Obtiene los gastos de un usuario.
    """
    cursor.execute('SELECT * FROM gastos WHERE usuario_id=?',
                (usuario_id,)
    )
    return cursor.fetchall()
# Ajusta la función para obtener los gastos mensuales
def obtener_gastos_mensuales(usuario_id):
    """
    Obtiene los gastos mensuales de un usuario.
    """
    cursor.execute(
        'SELECT strftime("%Y,%m", fecha) as mes,SUM(monto) as total'
        'FROM gastos WHERE usuario_id=? GROUP BY mes',
        (usuario_id,)
    )
    return cursor.fetchall()
# Función para eliminar toda la fila de un gasto
def eliminar_gasto_completo(gasto_id):
    """
    Elimina un gasto de la base de datos.
    """
    cursor.execute('DELETE FROM gastos WHERE id=?', (gasto_id,))
    conn.commit()
# Conexión a la base de datos y crea una nueva si no existe
conn = sqlite3.connect('gastos_app.db')
cursor = conn.cursor()
# Crear una tabla de usuarios si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        contrasena TEXT
    )
''')
conn.commit()
# Crear una tabla de gastos si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        nombre TEXT,
        categoria TEXT,
        monto REAL,
        fecha DATE,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )
''')
conn.commit()
# Interfaz de inicio de sesión y registro
st.title('Registro de Gastos')
# Si el usuario no ha iniciado sesión
if 'usuario_id' not in st.session_state:
    with st.form(key='inicio_sesion_form'):
        st.subheader('Iniciar Sesión')
        usuario_input = st.text_input('Usuario:')
        contrasena_input = st.text_input('Contraseña:', type='password')
        submit_button_inicio_sesion = st.form_submit_button('Iniciar Sesión')
        if submit_button_inicio_sesion:
            usuario_encontrado = verificar_inicio_sesion(usuario_input, contrasena_input)
            if usuario_encontrado:
                st.success(f'Inicio de sesión exitoso, ¡bienvenido {usuario_encontrado[1]}!')
                st.session_state.usuario_id = usuario_encontrado[0]
            else:
                st.error('Usuario o contraseña incorrectos. '
                    'Por favor, inténtalo de nuevo o regístrate.')
# Si el usuario no ha iniciado sesión
if 'usuario_id' not in st.session_state:
    with st.form(key='registro_form'):
        st.subheader('Registrarse')
        nuevo_usuario = st.text_input('Nuevo Usuario:')
        nueva_contrasena = st.text_input('Nueva Contraseña:', type='password')
        confirmar_contrasena = st.text_input('Confirmar Contraseña:', type='password')
        # Usar el mismo form_submit_button para manejar el registro
        submit_button_registro = st.form_submit_button('Registrarse en la Aplicación')
        if submit_button_registro:
            if nuevo_usuario and nueva_contrasena and nueva_contrasena == confirmar_contrasena:
                agregar_usuario(nuevo_usuario, nueva_contrasena)
                st.success('Usuario registrado exitosamente. Ahora puedes iniciar sesión.')
            else:
                st.error('Contraseña no coincide. Por favor, inténtalo de nuevo.')
# Si el usuario ha iniciado sesión
if 'usuario_id' in st.session_state:
    st.sidebar.subheader('Menú')
    with st.form(key='gasto_form'):
        st.subheader('Registrar Nuevo Gasto')
        nombre = st.text_input('Nombre del Gasto:')
        # Cambia esta línea para utilizar un selectbox con las categorías específicas
        categorias_disponibles = [
            'Alimentos',
            'Transporte',
            'Entretenimiento',
            'Salud',
            'Servicios públicos',
            'Otros'
        ]
        categoria = st.selectbox('Categoría:', categorias_disponibles)
        monto = st.number_input('Monto:')
        fecha = st.date_input('Fecha:')
        submit_button_gasto = st.form_submit_button('Agregar Gasto')
        if submit_button_gasto:
            agregar_gasto(st.session_state.usuario_id,
                        nombre, categoria, monto, fecha)
            st.success('Gasto registrado exitosamente.')
# Sección para mostrar los gastos registrados y graficarlos
    if st.sidebar.button('Gastos Registrados'):
        st.subheader('Gastos Registrados')
        gastos_usuario = obtener_gastos(st.session_state.usuario_id)
        if not gastos_usuario:
            st.warning('No hay gastos registrados.')
        else:
            # Crear un DataFrame de Pandas para mostrar los datos en una tabla
            df_gastos = pd.DataFrame(gastos_usuario, columns=[
                'ID', 'Usuario ID', 'Nombre', 'Categoría', 'Monto', 'Fecha']
            )
            df_gastos = df_gastos.sort_values(by='ID', ascending=False)
            st.dataframe(df_gastos)
            try:
                import plotly.express as px
                fig = px.bar(
                    df_gastos,
                    x='Fecha',
                    y='Monto',
                    color='Categoría',
                    title='Gráfica de gastos Registrados'
                )
                st.plotly_chart(fig)
            except ImportError:
                st.warning('Error al graficar, verifique la grafica .')

# Sección para mostrar los gastos mensuales
if 'usuario_id' in st.session_state:
    if st.sidebar.button('Gastos Mensuales'):
        st.subheader('Gastos Mensuales')
        # Obtén los gastos mensuales
        df_gastos_mensuales = obtener_gastos_mensuales(st.session_state.usuario_id)
        # Convierte los resultados en un DataFrame de Pandas
        df_gastos_mensuales = pd.DataFrame(df_gastos_mensuales, columns=['Mes', 'Total'])
        # Muestra el DataFrame
        st.dataframe(df_gastos_mensuales.reset_index(drop=True))
        # Gráfico con Seaborn
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Mes', y='Total', data=df_gastos_mensuales)
        plt.xlabel('Mes')
        plt.ylabel('Total Gastossssss')
        plt.title('Gastos Mensuales')
        plt.xticks(rotation=45)
        st.pyplot(plt)
    # Sección para cerrar sesión
    if st.sidebar.button('Cerrar Sesión'):
        # Cerrar la conexión a la base de datos al finalizar
        conn.close()
        st.session_state.pop('usuario_id')
        st.success('Sesión cerrada exitosamente.')
        