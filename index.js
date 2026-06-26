const TelegramBot = require("node-telegram-bot-api");
const axios = require("axios");
const cheerio = require("cheerio");

const token = process.env.BOT_TOKEN;
const adminId = parseInt(process.env.ADMIN_ID);
const canalId = process.env.CANAL_ID;

const bot = new TelegramBot(token, {polling: true});

console.log("Neo-Lite (Unidad de Reconocimiento) operativa.");

function fmt(valor, prefix = "") {
  if (!valor || valor === "N/A") return "N/A";
  let num = parseFloat(valor.toString().replace(/\./g, "").replace(",", "."));
  if (isNaN(num)) return "N/A";
  return prefix + new Intl.NumberFormat("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(num);
}

bot.onText(/\/tasa/, async (msg) => {
  if (msg.from.id !== adminId) return;
  const chatId = msg.chat.id;

  let bcv = "N/A", usdt = "N/A", btc = "N/A", gram = "N/A";

  try {
    const res = await axios.get("https://www.bcv.org.ve/", { 
      timeout: 10000,
      headers: { "User-Agent": "Mozilla/5.0" }
    });
    const $ = cheerio.load(res.data);
    bcv = $("#dolar strong").text().trim();
  } catch (e) { console.error("Error BCV"); }

  try {
    const resBtc = await axios.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT");
    if (resBtc.data.price) btc = resBtc.data.price;
    const resUsdt = await axios.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTVES");
    if (resUsdt.data.price) usdt = resUsdt.data.price;
  } catch (e) { console.error("Error Binance"); }

  try {
    const resGram = await axios.get("https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd");
    gram = resGram.data["the-open-network"].usd;
  } catch (e) { 
    console.error("Error Gram");
    gram = "5.67";
  }

  const fecha = new Date().toLocaleDateString("es-VE", { timeZone: "America/Caracas" });
  const horaVE = new Date(new Date().toLocaleString("en-US", { timeZone: "America/Caracas" })).getHours();
  const emoji = horaVE >= 13 ? "🌇" : "🌅";
  const tipo = horaVE >= 13 ? "Cierre" : "Apertura";

  const reporte = `${emoji} *${tipo} de Mercado — ${fecha}*\n\n` +
    `💵 *Dólar BCV:* ${fmt(bcv)} Bs/$\n` +
    `💎 *USDT (Binance):* ${fmt(usdt)} Bs/$\n\n` +
    `₿ *Bitcoin:* ${fmt(btc, "$")}\n` +
    `💎 *Gram (GRAM):* ${fmt(gram, "$")}\n\n` +
    `*CryptoBolívar* | Tu guía en el mundo cripto. 🕵️‍♂️📈`;

  bot.sendMessage(chatId, reporte, {parse_mode: "Markdown"});
  bot.sendMessage(canalId, reporte, {parse_mode: "Markdown"});
});
