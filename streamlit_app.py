import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar

st.title("🕒 Control de Horas Laborales")

# --- CONFIGURACIÓN ---
horas_mensuales_meta = 173.33          # meta mensual estándar (40 h/semana)
inicio_contrato = date(2025, 9, 4)     # inicio anual
vacaciones_semanas = 3                 # semanas libres al año

# --- CARGA DE CSV ---
st.subheader("📂 Cargar datos guardados (CSV opcional)")
csv_file = st.file_uploader("Sube tu archivo CSV previamente guardado", type="csv")
if csv_file is not None:
    df = pd.read_csv(csv_file)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
else:
    df = pd.DataFrame(columns=["Fecha", "Entrada", "Salida", "Horas"])

# --- SELECCIÓN DE MES ---
st.subheader("📅 Selecciona mes y año")
year = st.number_input("Año:", min_value=2025, max_value=2100, value=date.today().year, step=1)
month = st.selectbox(
    "Mes:", list(calendar.month_name[1:]),
    index=date.today().month-1
)
month_index = list(calendar.month_name).index(month)

# --- GENERAR DÍAS DEL MES ---
days_in_month = calendar.monthrange(year, month_index)[1]
dias = pd.date_range(start=f"{year}-{month_index:02d}-01", end=f"{year}-{month_index:02d}-{days_in_month}")

# --- TABLA DE ENTRADAS ---
st.subheader("✍️ Introducir horas (formato HH:MM-HH:MM)")
rows = []
for d in dias:
    weekday = d.strftime("%A")
    if weekday == "Tuesday":
        continue  # omitir martes
    default_in = ""
    default_out = ""
    entrada_salida = st.text_input(f"{d.strftime('%d-%m-%Y')} ({weekday})", value="")
    if entrada_salida:
        try:
            entrada, salida = entrada_salida.split("-")
            t1 = datetime.strptime(entrada.strip(), "%H:%M")
            t2 = datetime.strptime(salida.strip(), "%H:%M")
            horas = round((t2 - t1).seconds / 3600, 2)
            rows.append({"Fecha": d, "Entrada": entrada, "Salida": salida, "Horas": horas})
        except:
            st.error("⚠️ Formato inválido. Usa HH:MM-HH:MM")

# --- ACTUALIZAR DATAFRAME ---
if rows:
    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
    df = df.drop_duplicates(subset=["Fecha"], keep="last").sort_values("Fecha")

# --- CÁLCULOS ---
st.subheader("📊 Resultados")

horas_mes = df[df["Fecha"].dt.month == month_index]["Horas"].sum()
st.write(f"**Horas registradas este mes:** {horas_mes:.2f} h")

horas_faltan_mes = horas_mensuales_meta - horas_mes
st.write(f"**Horas restantes este mes:** {horas_faltan_mes:.2f} h")

# Conteo anual desde inicio
df_desde_inicio = df[df["Fecha"] >= inicio_contrato]
dias_laborales_ano = (52*5) - (vacaciones_semanas*5)    # 5 días/semana menos vacaciones
horas_anuales_meta = round((horas_mensuales_meta*12) * (dias_laborales_ano/(52*5)),2)

horas_totales = df_desde_inicio["Horas"].sum()
st.write(f"**Total acumulado desde {inicio_contrato.strftime('%d-%m-%Y')}:** {horas_totales:.2f} h")
st.write(f"**Meta anual ajustada (vacaciones descontadas):** {horas_anuales_meta:.2f} h")
st.write(f"**Horas restantes para meta anual:** {max(horas_anuales_meta - horas_totales, 0):.2f} h")

# --- TABLA Y GUARDADO ---
st.subheader("📜 Registro de horas")
st.dataframe(df)

st.download_button(
    "💾 Guardar como CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="registro_horas.csv",
    mime="text/csv"
)
