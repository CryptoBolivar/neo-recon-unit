import os
import sys
import time
import telebot
import requests
import logging
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime

# --- CONFIGURACIÓN DE SEGURIDAD ---
# Silenciamos el warning del bypass SSL del BCV para evitar ruido en logs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Cargamos variables de entorno (Secrets en Replit)
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
CANAL_ID = int(os.getenv('CANAL_ID', '0'))

if not TOKEN:
    print("❌ Error: BOT_TOKEN no configurado en los Secrets.")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)

# --- MOTOR DE TASAS (EXTRACCIÓN) ---

def fmt(valor):
    """Formato venezolano: 1.234,56"""
    if valor is None or valor == "N/A": return "N/A"
    try:
        return "{:,.2f}".format(float(valor)).replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "N/A"

def get_bcv():
    """Extrae el oficial del BCV saltándose el SSL."""
    try:
        url = "https://www.bcv.org.ve/"
        # El parámetro verify=False es la clave para entrar al BCV sin errores
        res = requests.get(url, verify=False, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.content, 'html.parser')
        tasa = soup.find("div", {"id": "dolar"}).find("strong").text.strip()
        return float(tasa.replace(',', '.'))
    except Exception as e:
        print(f"Error BCV: {e}")
        return None

def get_gram():
    """Extrae precio de Gram (TON) desde CoinGecko."""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd"
        res = requests.get(url, timeout=10).json()
        return res['the-open-network']['usd']
    except Exception as e:
        print(f"Error Gram: {e}")
        return None

# --- COMANDO PRINCIPAL ---

@bot.message_handler(commands=['tasa'])
def publicar_tasa(message):
    """Ejecuta el reporte de élite (Solo Admin)."""
    if message.from_user.id != ADMIN_ID:
        return

    # Avisamos que estamos trabajando
    status_msg = bot.reply_to(message, "⏳ Unidad de Reconocimiento procesando datos...")

    # Extraemos datos
    bcv_raw = get_bcv()
    gram_raw = get_gram()
    
    fecha = datetime.now().strftime("%d/%m/%Y")
    hora_ve = datetime.now().hour # Nota: En Replit la hora puede variar, pero se usa como referencia
    
    emoji = "🌇" if hora_ve >= 13 else "🌅"
    tipo = "Cierre" if hora_ve >= 13 else "Apertura"

    # Construcción del reporte
    reporte = (
        f"{emoji} *{tipo} de Mercado — {fecha}*\n\n"
        f"💵 *Dólar BCV:* {fmt(bcv_raw)} Bs/$\n"
        f"💎 *Gram (GRAM):* ${fmt(gram_raw)}\n\n"
        f"*CryptoBolívar* | Tu guía en el mundo cripto. 🕵️‍♂️📈"
    )

    # Envío al Canal
    try:
        bot.send_message(CANAL_ID, reporte, parse_mode="Markdown")
        bot.edit_message_text("✅ Reporte publicado con éxito en el canal.", message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error al publicar: {e}", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    print("🚀 Neo-Recon (Python Edition) iniciado.")
    bot.infinity_polling()
