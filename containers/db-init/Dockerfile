FROM python:3.9-slim
WORKDIR /app

# ─── 1. Copiamos scripts ─────────────────────────────────────────────
COPY application/preprocessing/movies_data_processing.py .
COPY application/preprocessing/user_generator.py .

# ─── 2. Copiamos CSV al mismo lugar que busca el script (/tmp) ────────
COPY data/tmdb_5000_movies.csv   /tmp/
COPY data/tmdb_5000_credits.csv  /tmp/
# (ajusta la ruta a donde tengas los ficheros en tu repo)

# ─── 3. Instalamos dependencias ───────────────────────────────────────
RUN pip install --no-cache-dir pandas sqlalchemy psycopg2-binary

# ─── 4. Cadena de conexión por defecto; se puede sobreescribir via env ─
ENV DB_URL=postgresql://database_admin:1234@postgres-service:5432/movies_recommender

# ─── 5. Comando por defecto: carga CSV y después genera usuarios ──────
CMD ["sh", "-c", "python -u movies_data_processing.py && python -u user_generator.py"]


