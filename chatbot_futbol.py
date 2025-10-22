import pandas as pd

# Cargar el archivo Excel
df = pd.read_excel('datos_futbol.xlsx', sheet_name='Full 1')

# Convertir la columna de probabilidad base a numérico (quitando el %)
df['% "Base" per arribar a Laliga'] = df['% "Base" per arribar a Laliga'].astype(str).str.replace('%', '', regex=False).astype(float)

# Filtrar las filas de clubes (donde Categoria y base prob no son NaN)
club_df = df[df['Categoria'].notna() & df['% "Base" per arribar a Laliga'].notna()]

# Multiplicadores hardcoded basados en el Excel
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

# Multiplicadores de altura por rangos y grupos de edad
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
    """
    Obtiene valores únicos de una columna, filtrando por un diccionario de filtros si se proporciona.
    """
    if filters:
        mask = pd.Series(True, index=df.index)
        for key, value in filters.items():
            mask &= (df[key] == value)
        return sorted(df.loc[mask, col].dropna().unique())
    else:
        return sorted(df[col].dropna().unique())

def get_age_group(category):
    """
    Mapea la categoría a un grupo de edad para los multiplicadores de altura.
    """
    if 'Infantil' in category:
        return 'Infantil'
    elif 'Cadet' in category:
        return 'Cadet'
    elif 'Juvenil' in category:
        return 'Juvenil'
    else:
        return None

def select_option(options, prompt):
    """
    Muestra una lista numerada de opciones y permite al usuario seleccionar una por número.
    """
    print(prompt)
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt}")
    while True:
        try:
            choice = int(input("Elige el número de la opción: ")) - 1
            if 0 <= choice < len(options):
                return options[choice]
            else:
                print("Número inválido. Intenta de nuevo.")
        except ValueError:
            print("Entrada inválida. Introduce un número.")

def main():
    print("¡Bienvenido al Chatbot de Probabilidades de Fútbol Juvenil!")
    print("Te haré preguntas paso a paso para calcular la probabilidad final de llegar a LaLiga.\n")

    filters = {}

    # Preguntar categoría
    categories = get_unique_options(club_df, 'Categoria')
    category = select_option(categories, "Selecciona la categoría:")
    filters['Categoria'] = category

    # Preguntar división
    divisions = get_unique_options(club_df, 'Divisió', filters)
    division = select_option(divisions, "Selecciona la división:")
    filters['Divisió'] = division

    # Preguntar zona geográfica
    zones = get_unique_options(club_df, 'Zona geogràfica', filters)
    zone = select_option(zones, "Selecciona la zona geográfica:")
    filters['Zona geogràfica'] = zone

    # Preguntar club
    clubs = get_unique_options(club_df, 'Club', filters)
    club = select_option(clubs, "Selecciona el club:")
    filters['Club'] = club

    # Obtener la probabilidad base del club seleccionado
    row = club_df[(club_df['Categoria'] == category) &
                  (club_df['Divisió'] == division) &
                  (club_df['Zona geogràfica'] == zone) &
                  (club_df['Club'] == club)]
    
    if row.empty:
        print("No se encontró la combinación. Intenta de nuevo.")
        return
    
    base_prob = row['% "Base" per arribar a Laliga'].values[0]

    # Preguntar posición
    pos_options = list(positions.keys())
    position = select_option(pos_options, "Selecciona la posición:")
    multi_pos = positions[position]

    # Preguntar pierna dominante
    leg_options = list(legs.keys())
    leg = select_option(leg_options, "Selecciona la pierna dominante:")
    multi_leg = legs[leg]

    # Preguntar altura
    while True:
        try:
            height = float(input("Introduce la altura en metros (ej: 1.75): "))
            break
        except ValueError:
            print("Entrada inválida. Introduce un número decimal.")

    # Encontrar multiplicador de altura
    multi_height = 1.0  # Default
    age_group = get_age_group(category)
    if age_group:
        for (min_h, max_h), multis in sorted(height_multis.items()):
            if min_h <= height <= max_h:
                multi_height = multis.get(age_group, 1.0)
                break

    # Calcular la probabilidad final (prob → odds → multiplicadores → prob)
    if base_prob >= 1:
        base_prob = 0.999  # Evitar división por cero

    odds = base_prob / (1 - base_prob)  # Convertir probabilidad base a odds
    final_odds = odds * multi_pos * multi_leg * multi_height  # Aplicar multiplicadores
    final_prob = final_odds / (1 + final_odds)  # Convertir odds finales a probabilidad

    # Mostrar resultados
    print("\nResultados:")
    print(f"Probabilidad base: {base_prob * 100:.4f}%")
    print(f"Multiplicadores aplicados: Posición ({multi_pos}), Pierna ({multi_leg}), Altura ({multi_height})")
    print(f"Probabilidad final: {final_prob * 100:.4f}%")

if __name__ == "__main__":
    main()