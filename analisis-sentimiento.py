import pandas as pd
import re
import unicodedata

# Diccionario de sentimientos. Cada conjunto de palabras tiene un puntaje para saber cuánto suma o resta cada una exactamente. Valores positivos representan emociones positivas y negativos son sentimientos negativos.
ponderaciones = {
    # Palabras Positivas
    re.compile(r'\b(mejor|fav|ayudar|genia|7)\b', re.IGNORECASE): 3,
    re.compile(r'\b(excelen|genial|maravillos|grac|preocup|seco|seca|simp|entrete|facil|crack|favorit|cercan|amab|amo|colab|encant|genio|pasion|cariño|agradec|pacien|tiern)\w*\b', re.IGNORECASE): 3,
    re.compile(r'\b(aport|gust|buen|bien|agrada|gran|siempre|sencill|perfec|permit|oportunidad|aplica)\w*\b', re.IGNORECASE): 2,
    re.compile(r'\b(bastante|interes|util|muy|super|general)\w*\b', re.IGNORECASE): 1,

    # Palabras negativas
    re.compile(r'\b(podria|voz|menos|aunque|demasiad|llen|problema|feedback|entrega|a pesar|poc|quiza|dific|penca|mejora|desagradable|insuficiente|deb|escuch|prueba)\w*\b', re.IGNORECASE): -1,
    re.compile(r'\b(gustaria|siento|tard|monoton|pero|incertidumbre|mal|aburrido|demor|perjudic|bulla|falt|mismo|cuesta|negativ|enred|rapido|exces)\w*\b', re.IGNORECASE): -2,
    re.compile(r'\b(irrit|odi|miedo|ansiedad|sobrepas|pesimo|peor|agres|floj|burl|despec|sarcas|defic)\w*\b', re.IGNORECASE): -3,
    re.compile(r'\b(no)\b', re.IGNORECASE): -1,
    re.compile(r'\b(lent(o)?|lent(a)?)\b', re.IGNORECASE): -2,
    re.compile(r'\b(fome)\b', re.IGNORECASE): -3,
    
    # Red Flags
    re.compile(r'\b(sexis|sexu|machis|racis|clasis|sobre peso|sobrepeso|misog|violador|violacion|gordofobi|xenofobi|transfobi|funa|los cuerpos|sus cuerpos)\w*\b', re.IGNORECASE): -40,
}

# Diccionario de palabras que aplica únicamente para la observación positiva
ponderaciones_positivas = {**ponderaciones, 
    re.compile(r'\b(aprend|valor)\w*\b', re.IGNORECASE): 3,
    re.compile(r'\b(clar|respet|dinami|enseñ)\w*\b', re.IGNORECASE): 2,
    re.compile(r'\b(aplic|prepar|dedic|complet|foment|motiva)\w*\b', re.IGNORECASE): 1,
    re.compile(r'\b(nada|ningun)\w*\b', re.IGNORECASE): -2 
}

# Diccionario de palabras que aplica únicamente para la observación negativa
ponderaciones_negativas = {**ponderaciones, 
    re.compile(r'\b(aprend)\w*\b', re.IGNORECASE): -3,
    re.compile(r'\b(clar|respet|dinami|enseñ)\w*\b', re.IGNORECASE): -2,
    re.compile(r'\b(aplic|prepar|dedic|motiva)\w*\b', re.IGNORECASE): -1,
    re.compile(r'\b(nada|ningun)\w*\b', re.IGNORECASE): 2
}

# Diccionario de categorías, se crearon 3 tipos de observaciones y las siguientes palabras sumarán puntos a cada uno de ellos. El conjunto que tenga más puntos será el que se asigne a la observación 
palabras_clave = {
    'Procesos de Enseñanza y Aprendizaje': [
        (r'\b(contenido|ayudantia|materia|aprend|import|relevancia|evaluacion|segur|interesante|actividad)\w*\b', 5),
        (r'\b(curso|clase|entrete|ambiente)\w*\b', 3),
        (r'\b(super)\w*\b', 1)
    ],  
    'Relaciones Interpersonales': [
        (r'\b(excelente|usted|profe|pedagog|docente|alguien|escuch|explic|metodo|preocup|dedic|voz|demor|dispo|pregunt|entend|capaz|enseñ|simp|clar|explic)\w*\b', 5),
        (r'\b(clima|ayudante)\w*\b', 3),
        (r'\b(grande)\w*\b', 1)
    ],
    'Gestión del Proceso Formativo': [
        (r'\b(sala|aula|estructur|orden|desorden|administr|organiz|plan|comunica|coordin|ppt|descoordin|llen|requisito)\w*\b', 5),
        (r'\b(temario|correg)\w*\b', 3),
        (r'\b(ejerci|evalua|prueba|control|notas|calificacion|solemne|examen|tarea|decima|rubrica|tiempo)\w*\b', 1)
    ],
    'Grupo Vacio': [
        (r'^\s*$', 0)  # Para texto vacío
    ]
}

# Función para normalizar texto
def normalizar_texto(texto):
    if pd.isna(texto):
        return ''
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto.lower()

# Función para verificar si un comentario es "basura". Un comentario es considerado es basura si tiene menos de 3 carácteres, si no se incluye en el abecedario, no tiene vocales, 
def es_texto_basura(texto):
    texto = normalizar_texto(texto)
    if len(texto) <= 3 or re.fullmatch(r'[^a-zA-Z\s]*', texto) or not re.search(r'[aeiou]', texto):
        return True
    return False

# Función para calcular el puntaje total de un comentario usando los diccionarios adecuados
def calcular_puntaje_comentario(comentario, ponderaciones_positivas, ponderaciones_negativas):
    comentario = normalizar_texto(comentario)
    puntaje_positivo = 0
    puntaje_negativo = 0

    # Calcula puntajes usando el diccionario de palabras positivas
    for patron, ponderacion in ponderaciones_positivas.items():
        coincidencias = patron.findall(comentario)
        puntaje_positivo += len(coincidencias) * ponderacion

    # Calcula puntajes usando el diccionario de palabras negativas
    for patron, ponderacion in ponderaciones_negativas.items():
        coincidencias = patron.findall(comentario)
        puntaje_negativo += len(coincidencias) * ponderacion

    return puntaje_positivo, puntaje_negativo

# Función para clasificar opiniones
def clasificar_opiniones(datos):
    clasificacion_positiva = []
    emocion_positiva = []
    clasificacion_negativa = []
    emocion_negativa = []

    for indice, fila in datos.iterrows():
        comentario_positivo = fila['Observacion_Positiva']
        if pd.isna(comentario_positivo):
            clasificacion_positiva.append('Grupo Vacío')
            emocion_positiva.append(0)
        else:
            if es_texto_basura(comentario_positivo):
                clasificacion_positiva.append('Grupo Vacío')
                emocion_positiva.append(0)
            else:
                puntaje_positivo, puntaje_negativo = calcular_puntaje_comentario(
                    comentario_positivo,
                    ponderaciones_positivas,
                    ponderaciones_negativas
                )
                emocion_positiva.append(puntaje_positivo)  

                comentario_positivo = normalizar_texto(comentario_positivo)
                puntaje_maximo = 0
                grupo_seleccionado = 'Grupo General'
                grupo_palabras = {}

                print(f"\nComentario Positivo: '{fila['Observacion_Positiva']}'")
                print(f" Puntaje Positivo Calculado: {puntaje_positivo}")

                for clave, patrones in palabras_clave.items():
                    puntaje_actual_grupo = 0
                    total_palabras = 0
                    print(f" Evaluando Grupo: {clave}")
                    for patron, ponderacion in patrones:
                        coincidencias = re.findall(patron, comentario_positivo, flags=re.IGNORECASE)
                        total_palabras += len(coincidencias)
                        puntaje_actual = len(coincidencias) * ponderacion
                        puntaje_actual_grupo += puntaje_actual
                        print(f"  Patrón: '{patron}' - Coincidencias: {len(coincidencias)} - Puntaje: {puntaje_actual}")
                    
                    print(f" Puntaje Total para el Grupo '{clave}': {puntaje_actual_grupo} - Palabras Coincidentes: {total_palabras}")
                    
                    grupo_palabras[clave] = total_palabras

                    if puntaje_actual_grupo > puntaje_maximo:
                        puntaje_maximo = puntaje_actual_grupo
                        grupo_seleccionado = clave
                        print(f"  Grupo Seleccionado Actual: {grupo_seleccionado} - Puntaje: {puntaje_maximo}")
                    elif puntaje_actual_grupo == puntaje_maximo:
                        # Si hay empate, decidir por el número de palabras
                        if total_palabras > grupo_palabras.get(grupo_seleccionado, 0):
                            grupo_seleccionado = clave
                            print(f"  Grupo Seleccionado por Empate: {grupo_seleccionado} - Palabras Coincidentes: {total_palabras}")
                
                clasificacion_positiva.append(grupo_seleccionado)

        comentario_negativo = fila['Observacion_Negativa']
        if pd.isna(comentario_negativo):
            clasificacion_negativa.append('Grupo Vacío')
            emocion_negativa.append(0)
        else:
            if es_texto_basura(comentario_negativo):
                clasificacion_negativa.append('Grupo Vacío')
                emocion_negativa.append(0)
            else:
                puntaje_positivo, puntaje_negativo = calcular_puntaje_comentario(
                    comentario_negativo,
                    ponderaciones_positivas,
                    ponderaciones_negativas
                )
                emocion_negativa.append(puntaje_negativo)  

                comentario_negativo = normalizar_texto(comentario_negativo)
                puntaje_maximo = 0
                grupo_seleccionado = 'Grupo General'
                grupo_palabras = {}

                print(f"\nComentario Negativo: '{fila['Observacion_Negativa']}'")
                print(f" Puntaje Negativo Calculado: {puntaje_negativo}")

                for clave, patrones in palabras_clave.items():
                    puntaje_actual_grupo = 0
                    total_palabras = 0
                    print(f" Evaluando Grupo: {clave}")
                    for patron, ponderacion in patrones:
                        coincidencias = re.findall(patron, comentario_negativo, flags=re.IGNORECASE)
                        total_palabras += len(coincidencias)
                        puntaje_actual = len(coincidencias) * ponderacion
                        puntaje_actual_grupo += puntaje_actual
                        print(f"  Patrón: '{patron}' - Coincidencias: {len(coincidencias)} - Puntaje: {puntaje_actual}")
                    
                    print(f" Puntaje Total para el Grupo '{clave}': {puntaje_actual_grupo} - Palabras Coincidentes: {total_palabras}")
                    
                    grupo_palabras[clave] = total_palabras

                    if puntaje_actual_grupo > puntaje_maximo:
                        puntaje_maximo = puntaje_actual_grupo
                        grupo_seleccionado = clave
                        print(f"  Grupo Seleccionado Actual: {grupo_seleccionado} - Puntaje: {puntaje_maximo}")
                    elif puntaje_actual_grupo == puntaje_maximo:
                        # Si hay empate, decidir por el número de palabras
                        if total_palabras > grupo_palabras.get(grupo_seleccionado, 0):
                            grupo_seleccionado = clave
                            print(f"  Grupo Seleccionado por Empate: {grupo_seleccionado} - Palabras Coincidentes: {total_palabras}")
                
                clasificacion_negativa.append(grupo_seleccionado)

    num_filas = len(datos)
    while len(clasificacion_positiva) < num_filas:
        clasificacion_positiva.append('Grupo Vacío')
        emocion_positiva.append(0)
    while len(clasificacion_negativa) < num_filas:
        clasificacion_negativa.append('Grupo Vacío')
        emocion_negativa.append(0)

    datos['Clasificacion_Observacion_Positiva'] = clasificacion_positiva
    datos['Emocion_Observacion_Positiva'] = emocion_positiva
    datos['Clasificacion_Observacion_Negativa'] = clasificacion_negativa
    datos['Emocion_Observacion_Negativa'] = emocion_negativa

    return datos

# Crear Excel final
datos = pd.read_csv('datos.csv', encoding='latin-1', sep=';')
datos_actualizados = clasificar_opiniones(datos)
datos_actualizados.to_csv('opiniones_estudiantes.csv', index=False, encoding='latin-1', sep=';')

print("Se han guardado los datos clasificados.")