# Utiliser l'image Python officielle (version stable)
FROM python:3.11-slim

# Paramètres Python standards
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dossier de travail dans le conteneur
WORKDIR /app

# On saute l'étape apt-get qui bloque et on installe direct les libs Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# On copie le reste du code
COPY . .

# Port pour Cloud Run
EXPOSE 8080

# Lancement de l'app
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]