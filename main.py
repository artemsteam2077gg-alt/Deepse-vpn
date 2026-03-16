from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
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

# === 10 ПОЛНЫХ ТЕМ ===
COLOR_THEMES = {
    'DeepSeek Classic': {
        'bg': [0.05, 0.05, 0.1, 1],
        'button': [0.2, 0.4, 0.8, 1],
        'text': [1, 1, 1, 1],
        'accent': [0.3, 0.6, 0.9, 1]
    },
    'Dark Nebula': {
        'bg': [0.02, 0.02, 0.05, 1],
        'button': [0.4, 0.2, 0.6, 1],
        'text': [1, 0.9, 1, 1],
        'accent': [0.6, 0.3, 0.8, 1]
    },
    'Cyber Green': {
        'bg': [0, 0.1, 0, 1],
        'button': [0, 0.8, 0.2, 1],
        'text': [0.8, 1, 0.8, 1],
        'accent': [0, 0.9, 0.3, 1]
    },
    'Royal Purple': {
        'bg': [0.1, 0.05, 0.15, 1],
        'button': [0.5, 0.2, 0.7, 1],
        'text': [1, 0.9, 1, 1],
        'accent': [0.7, 0.4, 0.9, 1]
    },
    'Amber Glow': {
        'bg': [0.1, 0.08, 0.05, 1],
        'button': [0.8, 0.5, 0, 1],
        'text': [1, 0.9, 0.7, 1],
        'accent': [1, 0.6, 0, 1]
    },
    'Ocean Deep': {
        'bg': [0.05, 0.1, 0.2, 1],
        'button': [0, 0.4, 0.8, 1],
        'text': [0.8, 0.9, 1, 1],
        'accent': [0, 0.7, 1, 1]
    },
    'Ruby Red': {
        'bg': [0.15, 0.05, 0.05, 1],
        'button': [0.8, 0.2, 0.2, 1],
        'text': [1, 0.9, 0.9, 1],
        'accent': [1, 0.3, 0.3, 1]
    },
    'Emerald': {
        'bg': [0.05, 0.15, 0.1, 1],
        'button': [0.1, 0.6, 0.3, 1],
        'text': [0.8, 1, 0.8, 1],
        'accent': [0.2, 0.9, 0.4, 1]
    },
    'Sunset': {
        'bg': [0.2, 0.1, 0.15, 1],
        'button': [0.8, 0.3, 0.2, 1],
        'text': [1, 0.9, 0.8, 1],
        'accent': [1, 0.5, 0, 1]
    },
    'Graphite': {
        'bg': [0.05, 0.05, 0.05, 1],
        'button': [0.3, 0.3, 0.3, 1],
        'text': [1, 1, 1, 1],
        'accent': [0.5, 0.5, 0.5, 1]
    }
}

class DeepSeVPN:
    @staticmethod
    def extract_host(key):
        match = re.search(r'@([^:]+):', key)
        return match.group(1) if match else None
    
    @staticmethod
    def test_ping(host):
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '2', host], 
                                  capture_output=True, timeout=3)
            if result.returncode == 0:
                output = result.stdout.decode()
                match = re.search(r'time[=<]?\s*([0-9.]+)', output)
                return float(match.group(1)) if match else None
        except: pass
        return None
    
    @staticmethod
    def test_tcp(host, port=443):
        try:
            sock = socket.socket()
            sock.settimeout(2)
            start = time.time()
            result = sock.connect_ex((host, port))
            latency = (time.time() - start) * 1000
            sock.close()
            return result == 0, latency
        except: return False, 9999

class DeepSeLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        
        self.current_theme = 'DeepSeek Classic'
        self.colors = COLOR_THEMES[self.current_theme]
        self.is_hunting = False
        self.hunt_seconds = 300  # 5 минут
        self.vpn = DeepSeVPN()
        
        # Применяем фон
        self.update_background()
        
        # Заголовок
        self.title = Label(
            text='🚀 DEEPSE VPN',
            font_size='32sp',
            bold=True,
            size_hint_y=0.1,
            color=self.colors['text']
        )
        self.add_widget(self.title)
        
        # Выбор темы
        theme_box = BoxLayout(size_hint_y=0.08, spacing=5)
        theme_box.add_widget(Label(
            text='Тема:',
            color=self.colors['text'],
            size_hint_x=0.3
        ))
        self.theme_spinner = Spinner(
            text=self.current_theme,
            values=list(COLOR_THEMES.keys()),
            size_hint_x=0.7
        )
        self.theme_spinner.bind(text=self.change_theme)
        theme_box.add_widget(self.theme_spinner)
        self.add_widget(theme_box)
        
        # Поле подписки
        self.sub_input = TextInput(
            text='https://raw.githubusercontent.com/artemsteam2077gg-alt/myvpn/main/happ_subscription.txt',
            multiline=False,
            size_hint_y=0.1,
            background_color=[0.2, 0.2, 0.2, 1],
            foreground_color=[1, 1, 1, 1]
        )
        self.add_widget(self.sub_input)
        
        # Кнопка ТУРБО
        self.turbo_btn = Button(
            text='🔥 ТУРБО',
            size_hint_y=0.15,
            background_color=self.colors['button']
        )
        self.turbo_btn.bind(on_press=self.start_turbo)
        self.add_widget(self.turbo_btn)
        
        # Кнопка ОХОТНИК
        self.hunter_btn = Button(
            text='🔍 ОХОТНИК',
            size_hint_y=0.15,
            background_color=[0.8, 0.3, 0, 1]
        )
        self.hunter_btn.bind(on_press=self.start_hunter)
        self.add_widget(self.hunter_btn)
        
        # Статус
        self.status_label = Label(
            text='Готов к работе',
            size_hint_y=0.1,
            color=self.colors['text']
        )
        self.add_widget(self.status_label)
        
        # Таймер
        self.timer_label = Label(
            text='',
            size_hint_y=0.07,
            color=[1, 0.5, 0, 1]
        )
        self.add_widget(self.timer_label)
        
        # Лог
        self.log_label = Label(
            text='',
            size_hint_y=0.25,
            color=[0.7, 0.7, 0.7, 1],
            halign='left',
            valign='top'
        )
        self.add_widget(self.log_label)
        
        Clock.schedule_interval(self.update_ui, 1)
    
    def update_background(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.colors['bg'])
            Rectangle(pos=self.pos, size=self.size)
    
    def change_theme(self, spinner, text):
        self.current_theme = text
        self.colors = COLOR_THEMES[text]
        self.title.color = self.colors['text']
        self.status_label.color = self.colors['text']
        self.turbo_btn.background_color = self.colors['button']
        self.update_background()
        self.log_msg(f'Тема: {text}')
    
    def log_msg(self, text):
        ts = datetime.now().strftime('%H:%M:%S')
        current = self.log_label.text
        self.log_label.text = f'[{ts}] {text}\n' + current[:500]
    
    def update_ui(self, dt):
        if self.is_hunting:
            self.hunt_seconds -= 1
            if self.hunt_seconds <= 0:
                self.is_hunting = False
                self.hunter_btn.disabled = False
                self.timer_label.text = ''
                self.status_label.text = 'Охота завершена'
            else:
                m, s = divmod(self.hunt_seconds, 60)
                self.timer_label.text = f'⏳ {m:02d}:{s:02d}'
    
    def start_turbo(self, btn):
        if not self.sub_input.text:
            self.status_label.text = 'Нет подписки'
            return
        self.is_hunting = False
        self.turbo_btn.disabled = True
        self.hunter_btn.disabled = True
        self.status_label.text = '🚀 ТУРБО'
        threading.Thread(target=self.turbo_loop, daemon=True).start()
    
    def start_hunter(self, btn):
        if not self.sub_input.text:
            self.status_label.text = 'Нет подписки'
            return
        self.is_hunting = True
        self.hunt_seconds = 300
        self.turbo_btn.disabled = True
        self.hunter_btn.disabled = True
        self.status_label.text = '🔍 ОХОТНИК'
        threading.Thread(target=self.hunter_loop, daemon=True).start()
    
    def turbo_loop(self):
        try:
            r = requests.get(self.sub_input.text, timeout=10)
            if r.status_code == 200:
                keys = re.findall(r'vless://[^\s<>"\']+', r.text)
                self.log_msg(f'Ключей: {len(keys)}')
                
                best = None
                best_ping = 9999
                for key in keys[:20]:
                    host = self.vpn.extract_host(key)
                    if host:
                        ping = self.vpn.test_ping(host)
                        if ping and ping < best_ping:
                            best_ping = ping
                            best = key
                            self.status_label.text = f'🏆 {ping}ms'
                    time.sleep(0.1)
                
                if best:
                    self.log_msg(f'Лучший пинг: {best_ping}ms')
        except Exception as e:
            self.log_msg(f'Ошибка: {e}')
        finally:
            self.turbo_btn.disabled = False
            self.hunter_btn.disabled = False
            self.status_label.text = 'Готов'
    
    def hunter_loop(self):
        try:
            r = requests.get(self.sub_input.text, timeout=10)
            if r.status_code == 200:
                keys = re.findall(r'vless://[^\s<>"\']+', r.text)
                self.log_msg(f'Загружено: {len(keys)}')
                
                results = []
                with ThreadPoolExecutor(max_workers=6) as ex:
                    futures = []
                    for key in keys[:100]:
                        futures.append(ex.submit(self.test_key, key))
                    
                    for f in futures:
                        if not self.is_hunting:
                            break
                        res = f.result(timeout=3)
                        if res:
                            results.append(res)
                            self.status_label.text = f'🎯 {len(results)}'
                
                if results:
                    results.sort(key=lambda x: x[1])
                    best_key, best_ping = results[0]
                    self.log_msg(f'Лучший пинг: {best_ping}ms')
                    try:
                        with open('/sdcard/Download/deepse_key.txt', 'w') as f:
                            f.write(best_key)
                        self.log_msg('Ключ сохранён')
                    except: pass
        except Exception as e:
            self.log_msg(f'Ошибка: {e}')
        finally:
            self.is_hunting = False
            self.turbo_btn.disabled = False
            self.hunter_btn.disabled = False
            self.status_label.text = 'Готов'
    
    def test_key(self, key):
        host = self.vpn.extract_host(key)
        if host:
            ping = self.vpn.test_ping(host)
            if ping and ping < 300:
                return (key, ping)
        return None

class DeepSeApp(App):
    def build(self):
        Window.size = (450, 750)
        return DeepSeLayout()

if __name__ == '__main__':
    DeepSeApp().run()
