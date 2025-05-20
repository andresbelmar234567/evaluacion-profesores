# Sentiment Analysis of Student Feedback on Teaching

This project implements a rule-based sentiment and topic classification system for analyzing student feedback on university-level instructors. It is designed to automatically classify positive and negative comments into relevant pedagogical categories and assess the emotional tone using weighted keyword patterns.

# Project Purpose

This script is a passion project I created to better understand how students feel about their teachers. The output has primarily been used to detect serious incidents that may require administrative attention, such as discrimination or harassment. It has also helped inform improvements in teaching methods, classroom management, and interpersonal relationships with students.

# Features

- **Custom Sentiment Scoring**: Rule-based scoring using regular expressions for both positive and negative sentiment.
- **Multi-dimensional Classification**: Comments are categorized into three core themes:
  - *Teaching and Learning Processes*
  - *Interpersonal Relationships*
  - *Management of the Educational Process*
- **Comment Filtering**: Detection and exclusion of meaningless or spam-like feedback.
- **Normalization**: Text is normalized (accents removed, converted to lowercase) for consistent processing.
- **Red Flag Detection**: Sensitive language (e.g. discriminatory or inappropriate terms) is heavily penalized.
- **Output Generation**: Results are saved in a clean CSV file with added columns for sentiment scores and thematic classification.

# Input

The input file must be a CSV named 'datos.csv' with the following structure:

---
Observacion_Positiva;Observacion_Negativa
"Un gran profesor";"A veces va demasiado rápido"
---

Encoding: latin-1
Separator: ; (semicolon)



# Output

The output is a CSV file named opiniones_estudiantes_actualizado.csv which contains:

    Clasificacion_Observacion_Positiva
    Emocion_Observacion_Positiva
    Clasificacion_Observacion_Negativa
    Emocion_Observacion_Negativa

# Technologies Used

    Python 3.10
    Pandas
    Regular Expressions (re)
    Unicode normalization (unicodedata)

# How to Run

    Place datos.csv in the same directory as the script.
    Run the script:

python analisis-sentimiento.py

    The classified data will be saved in the output CSV.

# Design Highlights

    Entirely rule-based (no external ML models required).
    Built to be language-aware and culturally contextualized (optimized only for Spanish).
    Easily extensible: new patterns and categories can be added as needed.

# License

This project is shared as part of a professional application and may be reused or adapted with appropriate credit.

# Disclaimer

The 'datos.csv' file used in this project was generated using artificial intelligence and does not contain any real student feedback. It was created solely for demonstration purposes in compliance with confidentiality policies of my organization.
