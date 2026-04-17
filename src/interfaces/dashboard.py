"""
Веб-дашборд для отображения результатов анализа и торговых сигналов
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data.binance_client import BinanceClient
from src.data.data_collector import DataCollector
from src.analysis.technical_indicators import TechnicalIndicators
from src.prediction.ml_models import CryptoPricePredictor
from src.utils.config import config

class CryptoDashboard:
    """Класс веб-дашборда для криптовалютного анализа"""

    def __init__(self):
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.client = BinanceClient()
        self.collector = DataCollector()

        # Данные для дашборда
        self.current_data = {}
        self.predictions = {}

        self.setup_layout()
        self.setup_callbacks()

    def setup_layout(self):
        """Настройка интерфейса дашборда"""

        self.app.layout = dbc.Container([
            # Заголовок
            dbc.Row([
                dbc.Col([
                    html.H1("🚀 Crypto Analysis Dashboard", className="text-center mb-4"),
                    html.Hr()
                ])
            ]),

            # Панель управления
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("⚙️ Настройки анализа"),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Криптовалюта:"),
                                    dcc.Dropdown(
                                        id='symbol-dropdown',
                                        options=[
                                            {'label': 'Bitcoin (BTC)', 'value': 'BTCUSDT'},
                                            {'label': 'Ethereum (ETH)', 'value': 'ETHUSDT'},
                                            {'label': 'Binance Coin (BNB)', 'value': 'BNBUSDT'},
                                            {'label': 'Cardano (ADA)', 'value': 'ADAUSDT'},
                                            {'label': 'Polkadot (DOT)', 'value': 'DOTUSDT'},
                                            {'label': 'Chainlink (LINK)', 'value': 'LINKUSDT'},
                                        ],
                                        value='BTCUSDT'
                                    )
                                ], md=4),
                                dbc.Col([
                                    html.Label("Интервал:"),
                                    dcc.Dropdown(
                                        id='interval-dropdown',
                                        options=[
                                            {'label': '1 минута', 'value': '1m'},
                                            {'label': '5 минут', 'value': '5m'},
                                            {'label': '15 минут', 'value': '15m'},
                                            {'label': '1 час', 'value': '1h'},
                                            {'label': '4 часа', 'value': '4h'},
                                            {'label': '1 день', 'value': '1d'},
                                        ],
                                        value='1h'
                                    )
                                ], md=4),
                                dbc.Col([
                                    html.Label("Горизонт прогноза:"),
                                    dcc.Dropdown(
                                        id='horizon-dropdown',
                                        options=[
                                            {'label': '1 час', 'value': 1},
                                            {'label': '4 часа', 'value': 4},
                                            {'label': '12 часов', 'value': 12},
                                            {'label': '24 часа', 'value': 24},
                                            {'label': '48 часов', 'value': 48},
                                            {'label': '7 дней', 'value': 168},
                                        ],
                                        value=24
                                    )
                                ], md=4),
                            ], className="mb-3"),
                            dbc.Button("🔄 Обновить анализ", id="update-button",
                                     color="primary", className="mb-3"),
                        ])
                    ])
                ], md=12)
            ], className="mb-4"),

            # Торговые сигналы
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("🎯 Торговые сигналы")),
                        dbc.CardBody(id="trading-signals")
                    ])
                ], md=12)
            ], className="mb-4"),

            # Прогнозы моделей
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("🤖 Прогнозы ML моделей")),
                        dbc.CardBody(id="ml-predictions")
                    ])
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("📊 Технические индикаторы")),
                        dbc.CardBody(id="technical-indicators")
                    ])
                ], md=6)
            ], className="mb-4"),

            # График цены
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("📈 График цены и индикаторов")),
                        dbc.CardBody([
                            dcc.Graph(id="price-chart")
                        ])
                    ])
                ], md=12)
            ], className="mb-4"),

            # Дополнительные индикаторы
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("🔍 Дополнительные индикаторы")),
                        dbc.CardBody([
                            dcc.Graph(id="indicators-chart")
                        ])
                    ])
                ], md=12)
            ], className="mb-4"),

            # Статус обновления
            dbc.Row([
                dbc.Col([
                    html.Div(id="status-message", className="text-center")
                ])
            ]),

            # Автообновление
            dcc.Interval(
                id='interval-component',
                interval=300*1000,  # Обновление каждые 5 минут
                n_intervals=0
            )

        ], fluid=True)

    def setup_callbacks(self):
        """Настройка колбеков для интерактивности"""

        @self.app.callback(
            [Output('trading-signals', 'children'),
             Output('ml-predictions', 'children'),
             Output('technical-indicators', 'children'),
             Output('price-chart', 'figure'),
             Output('indicators-chart', 'figure'),
             Output('status-message', 'children')],
            [Input('update-button', 'n_clicks'),
             Input('interval-component', 'n_intervals')],
            [State('symbol-dropdown', 'value'),
             State('interval-dropdown', 'value'),
             State('horizon-dropdown', 'value')]
        )
        def update_dashboard(n_clicks, n_intervals, symbol, interval, horizon):
            """Обновление всех компонентов дашборда"""

            try:
                # Получение данных
                status = f"🔄 Обновление данных для {symbol}..."

                # Загрузка исторических данных
                end_time = datetime.now()
                start_time = end_time - timedelta(days=30)

                df = self.client.get_historical_klines(
                    symbol=symbol,
                    interval=interval,
                    start_time=start_time.isoformat(),
                    end_time=end_time.isoformat()
                )

                if df.empty:
                    return [
                        dbc.Alert("❌ Не удалось загрузить данные", color="danger"),
                        dbc.Alert("❌ Данные недоступны", color="danger"),
                        dbc.Alert("❌ Данные недоступны", color="danger"),
                        go.Figure(),
                        go.Figure(),
                        dbc.Alert("❌ Ошибка загрузки данных", color="danger")
                    ]

                # Расчет технических индикаторов
                df_indicators = TechnicalIndicators.calculate_all_indicators(df)

                # Торговые сигналы
                signals = self.generate_trading_signals(df_indicators)

                # ML прогнозы (упрощенная версия для демо)
                predictions = self.generate_predictions(df_indicators, horizon)

                # Технические индикаторы
                indicators_summary = self.generate_indicators_summary(df_indicators)

                # Графики
                price_chart = self.create_price_chart(df_indicators, symbol)
                indicators_chart = self.create_indicators_chart(df_indicators)

                status_msg = dbc.Alert(f"✅ Данные обновлены: {datetime.now().strftime('%H:%M:%S')}",
                                     color="success")

                return [signals, predictions, indicators_summary,
                       price_chart, indicators_chart, status_msg]

            except Exception as e:
                error_msg = dbc.Alert(f"❌ Ошибка: {str(e)}", color="danger")
                return [error_msg, error_msg, error_msg,
                       go.Figure(), go.Figure(), error_msg]

    def generate_trading_signals(self, df):
        """Генерация торговых сигналов"""
        latest = df.iloc[-1]
        signals = []

        # RSI сигналы
        if 'RSI' in latest:
            rsi = latest['RSI']
            if rsi > 70:
                signals.append({
                    'indicator': 'RSI',
                    'signal': '📉 ПРОДАЖА',
                    'strength': 'Сильный',
                    'value': f'{rsi:.1f}',
                    'reason': 'Перекупленность',
                    'color': 'danger'
                })
            elif rsi < 30:
                signals.append({
                    'indicator': 'RSI',
                    'signal': '📈 ПОКУПКА',
                    'strength': 'Сильный',
                    'value': f'{rsi:.1f}',
                    'reason': 'Перепроданность',
                    'color': 'success'
                })
            else:
                signals.append({
                    'indicator': 'RSI',
                    'signal': '➡️ НЕЙТРАЛЬНО',
                    'strength': 'Слабый',
                    'value': f'{rsi:.1f}',
                    'reason': 'Нормальная зона',
                    'color': 'secondary'
                })

        # MACD сигналы
        if 'MACD' in latest and 'MACD_Signal' in latest:
            macd_bullish = latest['MACD'] > latest['MACD_Signal']
            if macd_bullish:
                signals.append({
                    'indicator': 'MACD',
                    'signal': '📈 ПОКУПКА',
                    'strength': 'Средний',
                    'value': f"{latest['MACD']:.4f}",
                    'reason': 'MACD выше сигнальной линии',
                    'color': 'success'
                })
            else:
                signals.append({
                    'indicator': 'MACD',
                    'signal': '📉 ПРОДАЖА',
                    'strength': 'Средний',
                    'value': f"{latest['MACD']:.4f}",
                    'reason': 'MACD ниже сигнальной линии',
                    'color': 'danger'
                })

        # SMA тренд
        if 'SMA_20' in latest and 'SMA_50' in latest:
            sma_bullish = latest['SMA_20'] > latest['SMA_50']
            price_above_sma = latest['close'] > latest['SMA_20']

            if sma_bullish and price_above_sma:
                signals.append({
                    'indicator': 'SMA Тренд',
                    'signal': '📈 ПОКУПКА',
                    'strength': 'Средний',
                    'value': f"SMA20: {latest['SMA_20']:.2f}",
                    'reason': 'Восходящий тренд, цена выше SMA20',
                    'color': 'success'
                })
            elif not sma_bullish and not price_above_sma:
                signals.append({
                    'indicator': 'SMA Тренд',
                    'signal': '📉 ПРОДАЖА',
                    'strength': 'Средний',
                    'value': f"SMA20: {latest['SMA_20']:.2f}",
                    'reason': 'Нисходящий тренд, цена ниже SMA20',
                    'color': 'danger'
                })

        # Создание карточек сигналов
        signal_cards = []
        for signal in signals:
            card = dbc.Card([
                dbc.CardBody([
                    html.H5(signal['indicator'], className="card-title"),
                    html.H4(signal['signal'], className=f"text-{signal['color']}"),
                    html.P([
                        html.Strong(f"Сила: {signal['strength']}"), html.Br(),
                        f"Значение: {signal['value']}", html.Br(),
                        f"Причина: {signal['reason']}"
                    ], className="card-text")
                ])
            ], color=signal['color'], outline=True, className="mb-2")
            signal_cards.append(card)

        if not signal_cards:
            signal_cards = [dbc.Alert("⚠️ Недостаточно данных для генерации сигналов", color="warning")]

        return signal_cards

    def generate_predictions(self, df, horizon):
        """Генерация прогнозов (упрощенная версия для демо)"""
        current_price = df['close'].iloc[-1]

        # Простые прогнозы на основе трендов и волатильности
        price_change = df['close'].pct_change().mean()
        volatility = df['close'].pct_change().std()

        # Различные сценарии
        predictions = [
            {
                'model': 'Трендовая модель',
                'prediction': current_price * (1 + price_change * horizon),
                'confidence': 65,
                'change': (price_change * horizon) * 100,
                'color': 'primary'
            },
            {
                'model': 'Консервативная модель',
                'prediction': current_price * (1 + price_change * horizon * 0.5),
                'confidence': 75,
                'change': (price_change * horizon * 0.5) * 100,
                'color': 'info'
            },
            {
                'model': 'Волатильность модель',
                'prediction': current_price * (1 + (price_change + volatility) * horizon * 0.3),
                'confidence': 55,
                'change': ((price_change + volatility) * horizon * 0.3) * 100,
                'color': 'warning'
            }
        ]

        prediction_cards = []
        for pred in predictions:
            direction = "📈" if pred['change'] > 0 else "📉"
            card = dbc.Card([
                dbc.CardBody([
                    html.H5(pred['model'], className="card-title"),
                    html.H4(f"${pred['prediction']:.2f}", className=f"text-{pred['color']}"),
                    html.P([
                        f"{direction} Изменение: {pred['change']:+.2f}%", html.Br(),
                        f"🎯 Уверенность: {pred['confidence']}%"
                    ], className="card-text"),
                    dbc.Progress(value=pred['confidence'], color=pred['color'], className="mb-2")
                ])
            ], outline=True, className="mb-2")
            prediction_cards.append(card)

        return prediction_cards

    def generate_indicators_summary(self, df):
        """Сводка по техническим индикаторам"""
        latest = df.iloc[-1]

        indicators = []

        # RSI
        if 'RSI' in latest:
            rsi_status = "Перекупленность" if latest['RSI'] > 70 else \
                        "Перепроданность" if latest['RSI'] < 30 else "Нормально"
            indicators.append(('RSI', f"{latest['RSI']:.1f}", rsi_status))

        # MACD
        if 'MACD' in latest:
            macd_status = "Бычий" if latest['MACD'] > 0 else "Медвежий"
            indicators.append(('MACD', f"{latest['MACD']:.4f}", macd_status))

        # ATR
        if 'ATR' in latest:
            atr_pct = (latest['ATR'] / latest['close']) * 100
            atr_status = "Высокая" if atr_pct > 2 else "Низкая" if atr_pct < 1 else "Средняя"
            indicators.append(('ATR', f"{latest['ATR']:.2f} ({atr_pct:.1f}%)", f"Волатильность: {atr_status}"))

        # Bollinger Bands
        if 'BB_Upper' in latest and 'BB_Lower' in latest:
            bb_width = ((latest['BB_Upper'] - latest['BB_Lower']) / latest['close']) * 100
            bb_position = "Верх" if latest['close'] > latest['BB_Upper'] else \
                         "Низ" if latest['close'] < latest['BB_Lower'] else "Середина"
            indicators.append(('Bollinger Bands', f"Ширина: {bb_width:.1f}%", f"Позиция: {bb_position}"))

        # Создание таблицы
        table_rows = []
        for name, value, status in indicators:
            row = html.Tr([
                html.Td(name, style={'font-weight': 'bold'}),
                html.Td(value),
                html.Td(status)
            ])
            table_rows.append(row)

        if table_rows:
            table = dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Индикатор"),
                        html.Th("Значение"),
                        html.Th("Статус")
                    ])
                ]),
                html.Tbody(table_rows)
            ], striped=True, hover=True, responsive=True)
        else:
            table = dbc.Alert("⚠️ Недостаточно данных", color="warning")

        return table

    def create_price_chart(self, df, symbol):
        """Создание графика цены"""
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3],
            subplot_titles=[f'{symbol} - Цена и индикаторы', 'Объем']
        )

        # Свечной график
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Цена'
            ), row=1, col=1
        )

        # Bollinger Bands
        if 'BB_Upper' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper',
                          line=dict(color='red', dash='dash')), row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower',
                          line=dict(color='green', dash='dash'),
                          fill='tonexty', fillcolor='rgba(0,100,80,0.1)'), row=1, col=1
            )

        # SMA
        if 'SMA_20' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20',
                          line=dict(color='orange')), row=1, col=1
            )

        # Объем
        fig.add_trace(
            go.Bar(x=df.index, y=df['volume'], name='Объем',
                   opacity=0.6), row=2, col=1
        )

        fig.update_layout(
            title=f'{symbol} - Анализ цены',
            xaxis_rangeslider_visible=False,
            height=600
        )

        return fig

    def create_indicators_chart(self, df):
        """Создание графика индикаторов"""
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=['RSI', 'MACD']
        )

        # RSI
        if 'RSI' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['RSI'], name='RSI',
                          line=dict(color='purple')), row=1, col=1
            )
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=1, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=1, col=1)

        # MACD
        if 'MACD' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['MACD'], name='MACD',
                          line=dict(color='blue')), row=2, col=1
            )
            if 'MACD_Signal' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal',
                              line=dict(color='red')), row=2, col=1
                )
            if 'MACD_Histogram' in df.columns:
                fig.add_trace(
                    go.Bar(x=df.index, y=df['MACD_Histogram'], name='Histogram',
                           opacity=0.6), row=2, col=1
                )

        fig.update_layout(height=500, title="Технические индикаторы")
        return fig

    def run(self, host='127.0.0.1', port=8050, debug=False):
        """Запуск дашборда"""
        print(f"🚀 Запуск Crypto Dashboard на http://{host}:{port}")
        self.app.run_server(host=host, port=port, debug=debug)


if __name__ == "__main__":
    dashboard = CryptoDashboard()
    dashboard.run(debug=True)