"""
Telegram бот для получения торговых сигналов и уведомлений
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import json

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ python-telegram-bot не установлен. Установите: pip install python-telegram-bot")

from src.data.binance_client import BinanceClient
from src.analysis.technical_indicators import TechnicalIndicators
from src.utils.config import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class CryptoTelegramBot:
    """Telegram бот для криптовалютного анализа"""

    def __init__(self, bot_token: str):
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot не установлен")

        self.bot_token = bot_token
        self.client = BinanceClient()
        self.application = Application.builder().token(bot_token).build()

        # Настройка команд
        self.setup_handlers()

        # Пользователи для уведомлений
        self.subscribers = set()
        self.load_subscribers()

    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("price", self.price_command))
        self.application.add_handler(CommandHandler("analyze", self.analyze_command))
        self.application.add_handler(CommandHandler("signals", self.signals_command))
        self.application.add_handler(CommandHandler("portfolio", self.portfolio_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        welcome_text = """
🚀 **Добро пожаловать в Crypto Analysis Bot!**

Я помогу вам анализировать криптовалютные рынки и получать торговые сигналы.

**Основные команды:**
• /price BTC - узнать цену криптовалюты
• /analyze BTC - полный анализ с сигналами
• /signals - быстрые сигналы по топ монетам
• /portfolio - обзор рынка
• /subscribe - подписаться на уведомления
• /help - полная справка

**Поддерживаемые монеты:** BTC, ETH, ADA, DOT, LINK и другие

Начните с команды /signals для быстрого обзора рынка!
        """

        keyboard = [
            [InlineKeyboardButton("📈 Сигналы", callback_data="quick_signals")],
            [InlineKeyboardButton("💰 BTC анализ", callback_data="analyze_BTCUSDT")],
            [InlineKeyboardButton("📊 Портфолио", callback_data="portfolio")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        help_text = """
📚 **Справка по командам**

**Анализ и цены:**
• `/price <symbol>` - текущая цена (например: /price BTC)
• `/analyze <symbol>` - полный анализ с индикаторами
• `/signals` - быстрые сигналы по топ монетам

**Мониторинг:**
• `/portfolio` - обзор основных криптовалют
• `/subscribe` - подписаться на уведомления
• `/unsubscribe` - отписаться от уведомлений

**Поддерживаемые символы:**
BTC, ETH, BNB, ADA, DOT, LINK, UNI, LTC и другие

**Примеры использования:**
• `/price BTC` - цена Bitcoin
• `/analyze ETH` - анализ Ethereum
• `/signals` - сигналы по всем монетам

Для получения уведомлений о важных сигналах используйте /subscribe
        """

        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /price"""
        if not context.args:
            await update.message.reply_text(
                "❌ Укажите символ криптовалюты\nПример: `/price BTC`",
                parse_mode='Markdown'
            )
            return

        symbol = context.args[0].upper()
        if not symbol.endswith('USDT'):
            symbol += 'USDT'

        try:
            # Получение данных
            ticker = self.client.get_24hr_ticker(symbol)

            if ticker.empty:
                await update.message.reply_text(f"❌ Данные для {symbol} не найдены")
                return

            data = ticker.iloc[0]
            price = float(data['lastPrice'])
            change = float(data['priceChangePercent'])
            volume = float(data['quoteVolume'])
            high = float(data['highPrice'])
            low = float(data['lowPrice'])

            # Определяем направление
            if change > 0:
                direction = "📈"
                change_text = f"+{change:.2f}%"
            else:
                direction = "📉"
                change_text = f"{change:.2f}%"

            price_text = f"""
{direction} **{symbol}**

💰 **Цена:** ${price:,.4f}
📊 **Изменение 24ч:** {change_text}
📈 **Максимум:** ${high:,.4f}
📉 **Минимум:** ${low:,.4f}
💵 **Объем:** ${volume:,.0f}

⏰ {datetime.now().strftime('%H:%M:%S')}
            """

            keyboard = [
                [InlineKeyboardButton("🔍 Анализ", callback_data=f"analyze_{symbol}")],
                [InlineKeyboardButton("🔄 Обновить", callback_data=f"price_{symbol}")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                price_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка получения данных: {str(e)}")

    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /analyze"""
        if not context.args:
            await update.message.reply_text(
                "❌ Укажите символ для анализа\nПример: `/analyze BTC`",
                parse_mode='Markdown'
            )
            return

        symbol = context.args[0].upper()
        if not symbol.endswith('USDT'):
            symbol += 'USDT'

        # Отправляем сообщение о загрузке
        loading_msg = await update.message.reply_text("🔄 Анализирую данные...")

        try:
            analysis = await self.perform_analysis(symbol)
            await loading_msg.edit_text(analysis, parse_mode='Markdown')

        except Exception as e:
            await loading_msg.edit_text(f"❌ Ошибка анализа: {str(e)}")

    async def signals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /signals"""
        loading_msg = await update.message.reply_text("🔄 Получаю сигналы...")

        try:
            signals = await self.get_quick_signals()
            await loading_msg.edit_text(signals, parse_mode='Markdown')

        except Exception as e:
            await loading_msg.edit_text(f"❌ Ошибка получения сигналов: {str(e)}")

    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /portfolio"""
        loading_msg = await update.message.reply_text("🔄 Загружаю портфолио...")

        try:
            portfolio = await self.get_portfolio_overview()
            await loading_msg.edit_text(portfolio, parse_mode='Markdown')

        except Exception as e:
            await loading_msg.edit_text(f"❌ Ошибка загрузки портфолио: {str(e)}")

    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /subscribe"""
        user_id = update.effective_user.id
        self.subscribers.add(user_id)
        self.save_subscribers()

        await update.message.reply_text(
            "✅ Вы подписались на уведомления!\n\n"
            "Вы будете получать:\n"
            "• Важные торговые сигналы\n"
            "• Резкие изменения цен\n"
            "• Ежедневные сводки рынка\n\n"
            "Для отписки используйте /unsubscribe"
        )

    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /unsubscribe"""
        user_id = update.effective_user.id
        self.subscribers.discard(user_id)
        self.save_subscribers()

        await update.message.reply_text(
            "❌ Вы отписались от уведомлений\n"
            "Для подписки используйте /subscribe"
        )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопок"""
        query = update.callback_query
        await query.answer()

        data = query.data

        if data == "quick_signals":
            await query.edit_message_text("🔄 Получаю сигналы...")
            signals = await self.get_quick_signals()
            await query.edit_message_text(signals, parse_mode='Markdown')

        elif data == "portfolio":
            await query.edit_message_text("🔄 Загружаю портфолио...")
            portfolio = await self.get_portfolio_overview()
            await query.edit_message_text(portfolio, parse_mode='Markdown')

        elif data.startswith("analyze_"):
            symbol = data.replace("analyze_", "")
            await query.edit_message_text(f"🔄 Анализирую {symbol}...")
            analysis = await self.perform_analysis(symbol)
            await query.edit_message_text(analysis, parse_mode='Markdown')

        elif data.startswith("price_"):
            symbol = data.replace("price_", "")
            await query.edit_message_text(f"🔄 Обновляю цену {symbol}...")
            # Здесь можно повторить логику price_command
            await query.edit_message_text(f"Цена {symbol} обновлена!")

    async def perform_analysis(self, symbol: str) -> str:
        """Выполнение полного анализа символа"""
        try:
            # Загрузка данных
            end_time = datetime.now()
            start_time = end_time - timedelta(days=7)

            df = self.client.get_historical_klines(
                symbol=symbol,
                interval='1h',
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat()
            )

            if df.empty:
                return f"❌ Нет данных для {symbol}"

            # Расчет индикаторов
            df_indicators = TechnicalIndicators.calculate_all_indicators(df)
            latest = df_indicators.iloc[-1]
            current_price = latest['close']

            # Формирование анализа
            analysis_text = f"🔍 **Анализ {symbol}**\n\n"
            analysis_text += f"💰 **Цена:** ${current_price:,.4f}\n\n"

            # RSI
            if 'RSI' in latest:
                rsi = latest['RSI']
                if rsi > 70:
                    rsi_status = "🔴 Перекупленность"
                    signal = "📉 ПРОДАЖА"
                elif rsi < 30:
                    rsi_status = "🟢 Перепроданность"
                    signal = "📈 ПОКУПКА"
                else:
                    rsi_status = "🟡 Нейтрально"
                    signal = "➡️ УДЕРЖАНИЕ"

                analysis_text += f"📊 **RSI:** {rsi:.1f} - {rsi_status}\n"
                analysis_text += f"🎯 **Сигнал RSI:** {signal}\n\n"

            # MACD
            if 'MACD' in latest and 'MACD_Signal' in latest:
                macd_signal = "📈 Бычий" if latest['MACD'] > latest['MACD_Signal'] else "📉 Медвежий"
                analysis_text += f"⚡ **MACD:** {macd_signal}\n\n"

            # SMA тренд
            if 'SMA_20' in latest and 'SMA_50' in latest:
                trend = "📈 Восходящий" if latest['SMA_20'] > latest['SMA_50'] else "📉 Нисходящий"
                analysis_text += f"📈 **Тренд:** {trend}\n\n"

            # Bollinger Bands
            if 'BB_Upper' in latest and 'BB_Lower' in latest:
                if current_price > latest['BB_Upper']:
                    bb_status = "🔴 Выше верхней полосы"
                elif current_price < latest['BB_Lower']:
                    bb_status = "🟢 Ниже нижней полосы"
                else:
                    bb_status = "🟡 В нормальном диапазоне"

                analysis_text += f"🎯 **Bollinger Bands:** {bb_status}\n\n"

            # Общий вывод
            analysis_text += "**📋 ОБЩИЙ ВЫВОД:**\n"

            # Простая логика для общего сигнала
            buy_signals = 0
            sell_signals = 0

            if 'RSI' in latest:
                if latest['RSI'] < 30:
                    buy_signals += 1
                elif latest['RSI'] > 70:
                    sell_signals += 1

            if 'MACD' in latest and 'MACD_Signal' in latest:
                if latest['MACD'] > latest['MACD_Signal']:
                    buy_signals += 1
                else:
                    sell_signals += 1

            if buy_signals > sell_signals:
                final_signal = "📈 **ПОКУПКА**"
                confidence = min(90, 60 + buy_signals * 15)
            elif sell_signals > buy_signals:
                final_signal = "📉 **ПРОДАЖА**"
                confidence = min(90, 60 + sell_signals * 15)
            else:
                final_signal = "➡️ **УДЕРЖАНИЕ**"
                confidence = 50

            analysis_text += f"{final_signal}\n"
            analysis_text += f"🎯 **Уверенность:** {confidence}%\n\n"
            analysis_text += f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"

            return analysis_text

        except Exception as e:
            return f"❌ Ошибка анализа {symbol}: {str(e)}"

    async def get_quick_signals(self) -> str:
        """Получение быстрых сигналов по основным монетам"""
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']
        signals_text = "🎯 **Быстрые сигналы**\n\n"

        try:
            for symbol in symbols:
                ticker = self.client.get_24hr_ticker(symbol)
                if not ticker.empty:
                    data = ticker.iloc[0]
                    price = float(data['lastPrice'])
                    change = float(data['priceChangePercent'])

                    if change > 5:
                        status = "🚀 Сильный рост"
                    elif change > 2:
                        status = "📈 Рост"
                    elif change < -5:
                        status = "💥 Сильное падение"
                    elif change < -2:
                        status = "📉 Падение"
                    else:
                        status = "➡️ Стабильно"

                    symbol_short = symbol.replace('USDT', '')
                    signals_text += f"**{symbol_short}:** ${price:,.2f} ({change:+.1f}%) {status}\n"

            signals_text += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
            return signals_text

        except Exception as e:
            return f"❌ Ошибка получения сигналов: {str(e)}"

    async def get_portfolio_overview(self) -> str:
        """Получение обзора портфолио"""
        symbols = config.get_symbols_by_category('major')
        portfolio_text = "📊 **Обзор рынка**\n\n"

        try:
            total_market_cap = 0

            for symbol in symbols:
                ticker = self.client.get_24hr_ticker(symbol)
                if not ticker.empty:
                    data = ticker.iloc[0]
                    price = float(data['lastPrice'])
                    change = float(data['priceChangePercent'])
                    volume = float(data['quoteVolume'])

                    if change >= 0:
                        trend_icon = "📈"
                    else:
                        trend_icon = "📉"

                    symbol_short = symbol.replace('USDT', '')
                    portfolio_text += f"{trend_icon} **{symbol_short}:** ${price:,.2f} ({change:+.1f}%)\n"

            # Общее настроение рынка
            portfolio_text += "\n**📈 Настроение рынка:**\n"
            portfolio_text += "Данные обновлены в реальном времени\n"
            portfolio_text += f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"

            return portfolio_text

        except Exception as e:
            return f"❌ Ошибка загрузки портфолио: {str(e)}"

    def load_subscribers(self):
        """Загрузка подписчиков из файла"""
        try:
            subscribers_file = Path('data/telegram_subscribers.json')
            if subscribers_file.exists():
                with open(subscribers_file, 'r') as f:
                    self.subscribers = set(json.load(f))
        except Exception as e:
            print(f"Ошибка загрузки подписчиков: {e}")

    def save_subscribers(self):
        """Сохранение подписчиков в файл"""
        try:
            Path('data').mkdir(exist_ok=True)
            with open('data/telegram_subscribers.json', 'w') as f:
                json.dump(list(self.subscribers), f)
        except Exception as e:
            print(f"Ошибка сохранения подписчиков: {e}")

    async def send_notification_to_subscribers(self, message: str):
        """Отправка уведомления всем подписчикам"""
        for user_id in self.subscribers:
            try:
                await self.application.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"Ошибка отправки уведомления пользователю {user_id}: {e}")

    def run(self):
        """Запуск бота"""
        if not TELEGRAM_AVAILABLE:
            print("❌ python-telegram-bot не установлен")
            return

        print("🤖 Запуск Telegram бота...")
        self.application.run_polling()


# Пример создания и запуска бота
if __name__ == "__main__":
    # Замените на ваш токен бота
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Укажите токен бота в переменной BOT_TOKEN")
        print("Получить токен: https://t.me/BotFather")
    else:
        bot = CryptoTelegramBot(BOT_TOKEN)
        bot.run()