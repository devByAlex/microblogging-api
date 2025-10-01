"""
Módulo de Machine Learning para análisis de sentimiento.

Este módulo proporciona funcionalidades de análisis de sentimiento
utilizando la biblioteca TextBlob para clasificar automáticamente
el tono emocional de las publicaciones en el microblogging.

Dependencies:
    - textblob: Biblioteca de procesamiento de lenguaje natural
"""

from textblob import TextBlob

def analyze_sentiment(text: str) -> str:
    """
    Analiza el sentimiento de un texto y lo clasifica en tres categorías.
    
    Utilizo TextBlob para realizar análisis de sentimiento basado en polaridad,
    clasificando el texto como "Positivo", "Negativo" o "Neutral".
    Esta función se integra automáticamente en el proceso de creación
    de publicaciones para añadir metadatos de sentimiento.
    
    Args:
        text (str): Texto a analizar (contenido de la publicación)
        
    Returns:
        str: Clasificación del sentimiento:
            - "Positivo": Para textos con sentimiento positivo (polaridad > 0)
            - "Negativo": Para textos con sentimiento negativo (polaridad < 0)
            - "Neutral": Para textos neutrales (polaridad = 0)
            
    Example:
        >>> analyze_sentiment("¡Me encanta este día!")
        "Positivo"
        >>> analyze_sentiment("Estoy muy triste")
        "Negativo"
        >>> analyze_sentiment("El clima está nublado")
        "Neutral"
        
    Note:
        TextBlob utiliza un modelo pre-entrenado que funciona mejor
        con textos en inglés, aunque tiene soporte básico para español.
        La polaridad va de -1.0 (muy negativo) a 1.0 (muy positivo).
    """
    # Creo un objeto TextBlob a partir del texto de entrada. 
    # TextBlob se encarga de todo el trabajo complejo de procesamiento del lenguaje y tokenización
    analysis= TextBlob(text)
    
    # Obtengo la polaridad del sentimiento. 
    # El valor es un flotante entre -1.0 y 1.0.
    polarity = analysis.sentiment.polarity  
    
    # Clasifico el sentimiento en una de las tres categorías. 
    # Uso condicionales para interpretar el valor númerico. 
    
    if polarity > 0: 
        return "Positivo"
    elif polarity < 0: 
        return "Negativo"
    else: 
        #Si la polaridad no es ni mayor ni menor que 0, entonces es 0. 
        return "Neutral"
    
    