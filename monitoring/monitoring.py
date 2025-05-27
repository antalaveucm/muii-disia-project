import pandas as pd
import time
import numpy as np
import os
from datetime import date, timedelta

from sqlalchemy import create_engine, text
import sqlalchemy.types as sqltypes

import psutil
from prometheus_client import Gauge, start_http_server

uid = 'database_admin'
pwd = '1234'
# server = 'localhost' # localhost (pruebas en local), postgres-service (kubernetes)
server = os.getenv('DB_SERVER', 'postgres-service')  # Esto debería usar postgres-service
database = 'movies_recommender'

engine = create_engine(f'postgresql+psycopg2://{uid}:{pwd}@{server}:5432/{database}')

# Metricas de monitorización Prometheus
cpu_usage = Gauge('system_cpu_percent', 'System CPU usage percent')
ram_usage = Gauge('system_memory_percent', 'System memory usage percent')
ram_used = Gauge('system_memory_used_gb', 'Used RAM in GB')
ram_total = Gauge('system_memory_total_gb', 'Total RAM in GB')
engagement = Gauge('user_engagement', 'Mean of all users visualization percentages of movies')

def monitor_user_engagement():
    # Solo nos interesan datos recientes (datos que tiene una antigüedad de 7 o menos días)
    sql = "SELECT visualized FROM users_watch_history WHERE date >= CURRENT_DATE - INTERVAL '7 days';"
    df_visualized = pd.read_sql_query(sql, engine)

    if df_visualized.empty:
        # Si no hay datos eso quiere decir que no hay ningun usuario viendo películas.
        engagement.set(0)
    else:
        engagement.set(round(df_visualized.mean().iloc[0], 2))

    # Prints para comprobar que funciona.
    #print(f"User engagement: {engagement}")

def monitor_system():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()

    cpu_usage.set(cpu)
    ram_usage.set(mem.percent)

    # Memoria en GB
    mem_used_gb = round(mem.used / (1024 ** 3), 2)
    mem_total_gb = round(mem.total / (1024 ** 3), 2)
    ram_used.set(mem_used_gb)
    ram_total.set(mem_total_gb)

    # Prints para comprobar que funciona.
    #print(f"CPU: {cpu}%, RAM: {mem.percent}% {mem_used_gb} GB/{mem_total_gb} GB")

if __name__ == "__main__":
    start_http_server(8000)  # Exponer /metrics al puerto 8000
    while True:
        monitor_system()
        monitor_user_engagement()
        time.sleep(30)  # Espera 30 segundos antes del siguiente chequeo