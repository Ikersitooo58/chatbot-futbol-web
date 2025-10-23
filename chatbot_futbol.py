import streamlit as st
     import pandas as pd

     # Cargar el archivo Excel
     df = pd.read_excel('datos_futbol.xlsx', sheet_name='Full 1')

     # Convertir la columna de probabilidad base a numérico (quitando el %)
     df['% "Base" per arribar a Laliga'] = df['% "Base" per arribar a Laliga'].astype(str).str.replace('%', '', regex=False).astype(float)

     # Filtrar las filas de clubes (donde Categoria y base prob no son NaN)
     club_df = df[df['Categoria'].notna() & df['% "Base" per arribar a Laliga'].notna()]

     # Multiplicadores hardcoded
     positions = {
         'Porter': 0.9,
         'Defensa': 0.95,
         'Migcampista': 1.02,
         'Devanter': 1.08
     }

     legs = {
         'Dreta': 1.0,
         'Esquerra': 1.05
     }

     height_multis = {
         (1.65, 1.70): {'Infantil': 0.99, 'Cadet': 0.97, 'Juvenil': 0.95},
         (1.71, 1.75): {'Infantil': 1.0, 'Cadet': 1.0, 'Juvenil': 0.98},
         (1.76, 1.80): {'Infantil': 1.03, 'Cadet': 1.02, 'Juvenil': 1.01},
         (1.81, 1.85): {'Infantil': 1.08, 'Cadet': 1.05, 'Juvenil': 1.03},
         (1.86, 1.90): {'Infantil': 1.12, 'Cadet': 1.08, 'Juvenil': 1.05},
         (1.91, 1.95): {'Infantil': 1.15, 'Cadet': 1.10, 'Juvenil': 1.06},
         (1.96, 2.00): {'Infantil': 1.18, 'Cadet': 1.12, 'Juvenil': 1.07}
     }

     def get_unique_options(df, col, filters=None):
         if filters:
             mask = pd.Series(True, index=df.index)
             for key, value in filters.items():
                 mask &= (df[key] == value)
             return sorted(df.loc[mask, col].dropna().unique())
         else:
             return sorted(df[col].dropna().unique())

     def get_age_group(category):
         if 'Infantil' in category:
             return 'Infantil'
         elif 'Cadet' in category:
             return 'Cadet'
         elif 'Juvenil' in category:
             return 'Juvenil'
         else:
             return None

     # Interfaz de Streamlit
     st.title('⚽ Chatbot de Probabilidades de Fútbol Juvenil')

     # Barra lateral para filtros
     st.sidebar.header('Filtros')

     # Seleccionar categoría
     categories = get_unique_options(club_df, 'Categoria')
     category = st.sidebar.selectbox('Selecciona la categoría:', categories)
     filters = {'Categoria': category}

     # Seleccionar división
     divisions = get_unique_options(club_df, 'Divisió', filters)
     division = st.sidebar.selectbox('Selecciona la división:', divisions)
     filters['Divisió'] = division

     # Seleccionar zona geográfica
     zones = get_unique_options(club_df, 'Zona geogràfica', filters)
     zone = st.sidebar.selectbox('Selecciona la zona geográfica:', zones)
     filters['Zona geogràfica'] = zone

     # Seleccionar club
     clubs = get_unique_options(club_df, 'Club', filters)
     club = st.sidebar.selectbox('Selecciona el club:', clubs)
     filters['Club'] = club

     # Obtener probabilidad base
     row = club_df[(club_df['Categoria'] == category) &
                   (club_df['Divisió'] == division) &
                   (club_df['Zona geogràfica'] == zone) &
                   (club_df['Club'] == club)]
     if not row.empty:
         base_prob = row['% "Base" per arribar a Laliga'].values[0] / 100  # Convertir a decimal
     else:
         base_prob = 0.0
         st.warning('No se encontró la combinación seleccionada.')

     # Seleccionar posición
     pos_options = list(positions.keys())
     position = st.sidebar.selectbox('Selecciona la posición:', pos_options)
     multi_pos = positions[position]

     # Seleccionar pierna dominante
     leg_options = list(legs.keys())
     leg = st.sidebar.selectbox('Selecciona la pierna dominante:', leg_options)
     multi_leg = legs[leg]

     # Seleccionar altura
     height = st.sidebar.number_input('Introduce la altura en metros (ej: 1.75):', min_value=1.65, max_value=2.00, value=1.75, step=0.01)

     # Calcular multiplicador de altura
     multi_height = 1.0
     age_group = get_age_group(category)
     if age_group:
         for (min_h, max_h), multis in sorted(height_multis.items()):
             if min_h <= height <= max_h:
                 multi_height = multis.get(age_group, 1.0)
                 break

     # Calcular probabilidad final
     if base_prob >= 1:
         base_prob = 0.999  # Evitar división por cero
     odds = base_prob / (1 - base_prob)
     final_odds = odds * multi_pos * multi_leg * multi_height
     final_prob = final_odds / (1 + final_odds)

     # Botón para calcular
     if st.sidebar.button('Calcular'):
         st.write('### Resultados:')
         st.write(f'**Probabilidad base:** {base_prob * 100:.4f}%')
         st.write(f'**Multiplicadores aplicados:** Posición ({multi_pos}), Pierna ({multi_leg}), Altura ({multi_height})')
         st.write(f'**Probabilidad final:** {final_prob * 100:.4f}%')