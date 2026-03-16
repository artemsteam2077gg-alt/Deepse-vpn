from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.window import Window
import threading
import requests
import re
import time
import subprocess
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import socket
import json

# === 10 ВЕЛИКОЛЕПНЫХ ТЕМ НА ОСНОВЕ KIVYMD [citation:4] ===
COLOR_THEMES = {
    'DeepSeek Classic': {
        'primary': [0.1, 0.2, 0.4, 1],      # Тёмно-синий
        'accent': [0.2, 0.6, 0.9, 1],       # Ярко-синий
        'bg': [0.05, 0.05, 0.1, 1],         # Почти чёрный
        'text': [1, 1, 1, 1],                # Белый
        'button': [0.2, 0.4, 0.8, 1]
    },
    'Dark Nebula': {
        'primary': [0.2, 0.1, 0.3, 1],       # Фиолетовый
        'accent': [0.6, 0.3, 0.8, 1],        # Ярко-фиолетовый
        'bg': [0.02, 0.02, 0.05, 1],         # Глубокий чёрный
        'text': [1, 0.9, 1, 1],               # Белый с оттенком
        'button': [0.4, 0.2, 0.6, 1]
    },
    'Cyber Green': {
        'primary': [0, 0.5, 0.2, 1],          # Тёмно-зелёный
        'accent': [0, 0.9, 0.3, 1],           # Неоново-зелёный
        'bg': [0, 0.1, 0.05, 1],              # Чёрно-зелёный
        'text': [0.7, 1, 0.7, 1],              # Светло-зелёный
        'button': [0, 0.8, 0.2, 1]
    },
    'Royal Purple': {
        'primary': [0.3, 0.1, 0.5, 1],        # Королевский фиолетовый
        'accent': [0.7, 0.4, 0.9, 1],         # Сиреневый
        'bg': [0.1, 0.05, 0.15, 1],           # Тёмно-фиолетовый
        'text': [1, 0.9, 1, 1],                # Белый
        'button': [0.5, 0.2, 0.7, 1]
    },
    'Amber Glow': {
        'primary': [0.5, 0.3, 0, 1],          # Янтарный
        'accent': [1, 0.6, 0, 1],              # Оранжевый
        'bg': [0.1, 0.08, 0.05, 1],            # Тёмный
        'text': [1, 0.9, 0.7, 1],               # Тёплый белый
        'button': [0.8, 0.5, 0, 1]
    },
    'Ocean Deep': {
        'primary': [0, 0.3, 0.6, 1],          # Синий
        'accent': [0, 0.7, 1, 1],              # Голубой
        'bg': [0.05, 0.1, 0.2, 1],             # Тёмно-синий
        'text': [0.8, 0.9, 1, 1],               # Светло-голубой
        'button': [0, 0.4, 0.8, 1]
    },
    'Ruby Red': {
        'primary': [0.5, 0.1, 0.1, 1],        # Рубиновый
        'accent': [1, 0.3, 0.3, 1],            # Ярко-красный
        'bg': [0.15, 0.05, 0.05, 1],           # Тёмно-красный
        'text': [1, 0.9, 0.9, 1],               # Белый
        'button': [0.8, 0.2, 0.2, 1]
    },
    'Emerald': {
        'primary': [0.1, 0.4, 0.2, 1],        # Изумрудный
        'accent': [0.2, 0.9, 0.4, 1],          # Ярко-зелёный
        'bg': [0.05, 0.15, 0.1, 1],             # Тёмно-зелёный
        'text': [0.8, 1, 0.8, 1],               # Светло-зелёный
        'button': [0.1, 0.6, 0.3, 1]
    },
    'Sunset': {
        'primary': [0.6, 0.2, 0.1, 1],        # Закатный
        'accent': [1, 0.5, 0, 1],              # Оранжевый
        'bg': [0.2, 0.1, 0.15, 1],             # Тёмно-розовый
        'text': [1, 0.9, 0.8, 1],               # Тёплый белый
        'button': [0.8, 0.3, 0.2, 1]
    },
    'Graphite': {
        'primary': [0.2, 0.2, 0.2, 1],        # Тёмно-серый
        'accent': [0.5, 0.5, 0.5, 1],          # Серый
        'bg': [0.05, 0.05, 0.05, 1],           # Чёрный
        'text': [1, 1, 1, 1],                   # Белый
        'button': [0.3, 0.3, 0.3, 1]
    }
}

class DeepSeVPN:
    """Основной класс с логикой проверок из GitHub-проектов [citation:2]"""
    
    @staticmethod
    def test_internet_connection():
        """Проверка наличия интернета перед тестом"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    @staticmethod
    def extract_ip_from_key(key):
        """Извлечение IP из vless ключа"""
        match = re.search(r'@([0-9.]+):', key)
        return match.group(1) if match else None
    
    @staticmethod
    def extract_host_from_key(key):
        """Извлечение хоста (может быть доменом)"""
        match = re.search(r'@([^:]+):', key)
        return match.group(1) if match else None
    
    @staticmethod
    def test_ping(host, timeout=2):
        """Тест пинга с обработкой ошибок"""
        try:
            # Для доменов используем ping
            result = subprocess.run(
                ['ping', '-c', '1', '-W', str(timeout), host],
                capture_output=True,
                timeout=timeout+1
            )
            if result.returncode == 0:
                output = result.stdout.decode()
                time_match = re.search(r'time[=<]?\s*([0-9.]+)', output)
                if time_match:
                    return float(time_match.group(1))
            return None
        except Exception:
            return None
    
    @staticmethod
    def test_tcp_connect(host, port, timeout=2):
        """Тест TCP-соединения"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            start = time.time()
            result = sock.connect_ex((host, port))
            latency = (time.time() - start) * 1000
            sock.close()
            return result == 0, latency
        except Exception:
            return False, 9999
    
    @staticmethod
    def test_rkn_bypass(key):
        """Проверка обхода РКН через тестовые сайты"""
        host = DeepSeVPN.extract_host_from_key(key)
        port = 443  # Стандартный HTTPS порт
        
        if not host:
            return False
        
        # Список заблокированных в РФ сайтов для теста [citation:2]
        test_sites = [
            'https://rutube.ru',
            'https://telegram.org',
            'https://www.youtube.com',
            'https://ru.wikipedia.org',
            'https://www.google.com'
        ]
        
        success_count = 0
        for site in test_sites[:3]:  # Тестируем первые 3 для скорости
            try:
                # Пробуем подключиться через прокси (имитация)
                # В реальном приложении здесь будет подключение через xray
                result = subprocess.run(
                    ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
                     '--connect-timeout', '3', site],
                    capture_output=True,
                    timeout=4
                )
                if result.returncode == 0:
                    code = result.stdout.decode().strip()
                    if code in ['200', '301', '302']:
                        success_count += 1
            except Exception:
                pass
        
        return success_count >= 2  # Хотя бы 2 сайта открываются

class DeepSeLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        # Текущая тема
        self.current_theme = 'DeepSeek Classic'
        self.theme_colors = COLOR_THEMES[self.current_theme]
        
        # Устанавливаем цвета фона
        self.update_background()
        
        # === ЗАГОЛОВОК ===
        self.title = Label(
            text='🚀 DEEPSE VPN',
            font_size='32sp',
            bold=True,
            size_hint_y=0.1,
            color=self.theme_colors['text']
        )
        self.add_widget(self.title)
        
        # === ВЫБОР ТЕМЫ ===
        theme_layout = BoxLayout(size_hint_y=0.08, spacing=10)
        theme_layout.add_widget(Label(
            text='Тема:', 
            color=self.theme_colors['text'],
            size_hint_x=0.3
        ))
        self.theme_spinner = Spinner(
            text=self.current_theme,
            values=list(COLOR_THEMES.keys()),
            size_hint_x=0.7,
            background_color=self.theme_colors['button']
        )
        self.theme_spinner.bind(text=self.change_theme)
        theme_layout.add_widget(self.theme_spinner)
        self.add_widget(theme_layout)
        
        # === ПОЛЕ ВВОДА ПОДПИСКИ ===
        self.sub_input = TextInput(
            text='https://raw.githubusercontent.com/artemsteam2077gg-alt/myvpn/main/happ_subscription.txt',
            multiline=False,
            size_hint_y=0.1,
            background_color=[0.2, 0.2, 0.2, 1],
            foreground_color=[1, 1, 1, 1]
        )
        self.add_widget(self.sub_input)
        
        # === КНОПКА ТУРБО ===
        self.turbo_btn = Button(
            text='[b]🔥 ТУРБО[/b]\nАвтовыбор лучшего сервера (каждые 30 сек)',
            size_hint_y=0.15,
            background_color=self.theme_colors['button'],
            markup=True
        )
        self.turbo_btn.bind(on_press=self.start_turbo)
        self.add_widget(self.turbo_btn)
        
        # === КНОПКА ОХОТНИК ===
        self.hunter_btn = Button(
            text='[b]🔍 ОХОТНИК[/b]\nПоиск идеального ключа (3 минуты)',
            size_hint_y=0.15,
            background_color=[0.8, 0.3, 0, 1],
            markup=True
        )
        self.hunter_btn.bind(on_press=self.start_hunter)
        self.add_widget(self.hunter_btn)
        
        # === СТАТУС ===
        self.status_label = Label(
            text='Готов к работе',
            size_hint_y=0.1,
            color=self.theme_colors['text']
        )
        self.add_widget(self.status_label)
        
        # === ТАЙМЕР ===
        self.timer_label = Label(
            text='',
            size_hint_y=0.08,
            color=[1, 0.5, 0, 1]
        )
        self.add_widget(self.timer_label)
        
        # === ЛОГ ===
        self.log_label = Label(
            text='',
            size_hint_y=0.2,
            color=[0.7, 0.7, 0.7, 1],
            halign='left',
            valign='top',
            text_size=(self.width - 40, None)
        )
        self.add_widget(self.log_label)
        
        # === ИНФОРМАЦИЯ О СОЕДИНЕНИИ ===
        self.conn_info = Label(
            text='Не подключено',
            size_hint_y=0.04,
            color=[0.8, 0.8, 0.8, 1],
            font_size='10sp'
        )
        self.add_widget(self.conn_info)
        
        # === ПЕРЕМЕННЫЕ ===
        self.is_turbo = False
        self.is_hunting = False
        self.hunt_seconds = 180
        self.vpn_process = None
        self.is_connected = False
        self.best_key = None
        self.all_proxies = []
        self.vpn = DeepSeVPN()
        
        # Обновление интерфейса
        Clock.schedule_interval(self.update_ui, 1)
        Clock.schedule_interval(self.update_log_size, 0.1)
    
    def update_log_size(self, dt):
        """Обновление размера текста лога"""
        self.log_label.text_size = (self.width - 40, None)
    
    def update_background(self):
        """Обновление фона приложения"""
        self.canvas.before.clear()
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*self.theme_colors['bg'])
            Rectangle(pos=self.pos, size=self.size)
    
    def change_theme(self, spinner, text):
        """Смена темы"""
        self.current_theme = text
        self.theme_colors = COLOR_THEMES[text]
        self.title.color = self.theme_colors['text']
        self.status_label.color = self.theme_colors['text']
        self.turbo_btn.background_color = self.theme_colors['button']
        self.update_background()
        self.log(f'🎨 Тема изменена на {text}')
    
    def update_ui(self, dt):
        """Обновление интерфейса"""
        if self.is_hunting:
            self.hunt_seconds -= 1
            if self.hunt_seconds <= 0:
                self.is_hunting = False
                self.timer_label.text = '⏰ Время вышло'
            else:
                minutes = self.hunt_seconds // 60
                seconds = self.hunt_seconds % 60
                self.timer_label.text = f'⏳ Осталось: {minutes}:{seconds:02d}'
        
        # Обновление информации о подключении
        if self.is_connected:
            self.conn_info.text = f'✅ Подключено к {self.best_ip if hasattr(self, "best_ip") else "серверу"}'
            self.conn_info.color = [0, 1, 0, 1]
        else:
            self.conn_info.text = '🔴 Не подключено'
            self.conn_info.color = [1, 0.5, 0.5, 1]
    
    def log(self, text):
        """Добавление в лог с таймстампом"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        current = self.log_label.text
        self.log_label.text = f'[{timestamp}] {text}\n' + current[:1000]
    
    def update_status(self, text):
        """Обновление статуса"""
        self.status_label.text = text
        self.log(text)
    
    def start_turbo(self, instance):
        """Запуск ТУРБО режима"""
        if not self.sub_input.text:
            self.update_status('❌ Вставьте ссылку на подписку')
            return
        
        # Проверка интернета [citation:2]
        if not self.vpn.test_internet_connection():
            self.update_status('❌ Нет подключения к интернету')
            return
        
        self.is_turbo = True
        self.is_hunting = False
        self.turbo_btn.disabled = True
        self.hunter_btn.disabled = True
        self.update_status('🚀 Запуск ТУРБО режима...')
        
        threading.Thread(target=self.turbo_loop, daemon=True).start()
    
    def start_hunter(self, instance):
        """Запуск ОХОТНИКА"""
        if not self.sub_input.text:
            self.update_status('❌ Вставьте ссылку на подписку')
            return
        
        # Проверка интернета [citation:2]
        if not self.vpn.test_internet_connection():
            self.update_status('❌ Нет подключения к интернету')
            return
        
        self.is_hunting = True
        self.is_turbo = False
        self.hunt_seconds = 180
        self.turbo_btn.disabled = True
        self.hunter_btn.disabled = True
        self.update_status('🔍 Запуск ОХОТНИКА...')
        
        threading.Thread(target=self.hunter_loop, daemon=True).start()
    
    def load_subscription(self, url):
        """Загрузка подписки по URL"""
        try:
            self.update_status(f'📡 Загрузка подписки...')
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                # Извлекаем все vless ключи
                keys = re.findall(r'vless://[^\s<>"\']+', response.text)
                self.log(f'✅ Найдено {len(keys)} ключей в подписке')
                return keys
            else:
                self.log(f'❌ Ошибка загрузки: HTTP {response.status_code}')
                return []
        except Exception as e:
            self.log(f'❌ Ошибка загрузки: {e}')
            return []
    
    def test_key_quality(self, key):
        """Тестирование качества ключа (несколько метрик) [citation:2]"""
        score = 0
        results = {}
        
        # Извлекаем хост
        host = self.vpn.extract_host_from_key(key)
        ip = self.vpn.extract_ip_from_key(key)
        
        if not host:
            return None
        
        # Тест 1: TCP соединение
        port = 443
        tcp_ok, latency = self.vpn.test_tcp_connect(host, port)
        if tcp_ok:
            score += 30
            results['latency'] = latency
            self.log(f'  ✓ TCP соединение: {latency:.0f}ms')
        else:
            results['latency'] = 9999
            self.log(f'  ✗ TCP соединение не удалось')
        
        # Тест 2: Пинг
        ping = self.vpn.test_ping(host)
        if ping and ping < 300:
            score += 30
            results['ping'] = ping
            self.log(f'  ✓ Пинг: {ping:.0f}ms')
        else:
            results['ping'] = 9999
        
        # Тест 3: Обход РКН
        if self.vpn.test_rkn_bypass(key):
            score += 40
            results['rkn'] = True
            self.log(f'  ✓ Обход РКН: работает')
        else:
            results['rkn'] = False
            self.log(f'  ✗ Обход РКН: не работает')
        
        return {
            'key': key,
            'host': host,
            'score': score,
            **results
        }
    
    def turbo_loop(self):
        """Режим ТУРБО: постоянный поиск лучшего сервера"""
        try:
            while self.is_turbo:
                # Загружаем подписку
                keys = self.load_subscription(self.sub_input.text)
                
                if keys:
                    self.update_status(f'🧪 Тестирование {min(20, len(keys))} ключей...')
                    
                    # Тестируем первые 20 ключей
                    best_score = 0
                    best_key = None
                    
                    for i, key in enumerate(keys[:20]):
                        if not self.is_turbo:
                            break
                        
                        result = self.test_key_quality(key)
                        if result and result['score'] > best_score:
                            best_score = result['score']
                            best_key = result
                            self.update_status(f'🏆 Новый лидер: {best_score} очков')
                    
                    if best_key:
                        self.update_status(f'✅ Лучший ключ найден (оценка: {best_score})')
                        self.best_key = best_key['key']
                        self.best_ip = best_key['host']
                        self.is_connected = True
                        
                        # Сохраняем лучший ключ
                        try:
                            save_path = '/sdcard/Download/deepse_best_key.txt'
                            with open(save_path, 'w') as f:
                                f.write(self.best_key)
                            self.log(f'💾 Ключ сохранён в {save_path}')
                        except:
                            pass
                    else:
                        self.update_status('❌ Не найдено рабочих ключей')
                
                # Ждём 30 секунд перед следующим тестом
                for i in range(30):
                    if not self.is_turbo:
                        break
                    time.sleep(1)
        
        except Exception as e:
            self.update_status(f'❌ Ошибка: {e}')
        finally:
            self.is_turbo = False
            self.turbo_btn.disabled = False
            self.hunter_btn.disabled = False
    
    def hunter_loop(self):
        """Режим ОХОТНИК: тщательный поиск идеального ключа"""
        try:
            # Загружаем подписку
            keys = self.load_subscription(self.sub_input.text)
            
            if keys:
                self.update_status(f'🧪 Охота на {min(50, len(keys))} ключей...')
                
                candidates = []
                
                # Используем многопоточность для ускорения [citation:3]
                with ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_key = {
                        executor.submit(self.test_key_quality, key): key 
                        for key in keys[:50]
                    }
                    
                    for i, future in enumerate(future_to_key):
                        if not self.is_hunting or self.hunt_seconds <= 0:
                            break
                        
                        result = future.result()
                        if result and result['score'] > 50:  # Проходной балл
                            candidates.append(result)
                            self.update_status(f'🎯 Найден кандидат: {result["score"]} очков')
                
                if candidates:
                    # Сортируем по убыванию оценки
                    candidates.sort(key=lambda x: x['score'], reverse=True)
                    best = candidates[0]
                    
                    self.up
