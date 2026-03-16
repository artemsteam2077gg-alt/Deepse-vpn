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
from datetime import datetime

# Цветовые темы
THEMES = {
    'DeepSeek Classic': {
        'bg': [0.1, 0.2, 0.3, 1],
        'button': [0.2, 0.4, 0.8, 1],
        'text': [1, 1, 1, 1]
    },
    'Dark Nebula': {
        'bg': [0.05, 0.05, 0.1, 1],
        'button': [0.4, 0.2, 0.6, 1],
        'text': [1, 1, 1, 1]
    },
    'Cyber Green': {
        'bg': [0, 0.1, 0, 1],
        'button': [0, 0.8, 0.2, 1],
        'text': [0.8, 1, 0.8, 1]
    }
}

class DeepSeLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        self.current_theme = 'DeepSeek Classic'
        self.theme_colors = THEMES[self.current_theme]
        
        # Заголовок
        self.title = Label(
            text='🚀 DEEPSE VPN',
            font_size='32sp',
            bold=True,
            size_hint_y=0.15,
            color=self.theme_colors['text']
        )
        self.add_widget(self.title)
        
        # Выбор темы
        theme_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        theme_layout.add_widget(Label(text='Тема:', color=self.theme_colors['text']))
        self.theme_spinner = Spinner(
            text=self.current_theme,
            values=list(THEMES.keys()),
            size_hint_x=0.7
        )
        self.theme_spinner.bind(text=self.change_theme)
        theme_layout.add_widget(self.theme_spinner)
        self.add_widget(theme_layout)
        
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
            text='[b]🔥 ТУРБО[/b]\nАвтовыбор сервера',
            size_hint_y=0.2,
            background_color=self.theme_colors['button'],
            markup=True
        )
        self.turbo_btn.bind(on_press=self.start_turbo)
        self.add_widget(self.turbo_btn)
        
        # Кнопка ОХОТНИК
        self.hunter_btn = Button(
            text='[b]🔍 ОХОТНИК[/b]\nПоиск ключа (3 мин)',
            size_hint_y=0.2,
            background_color=[0.8, 0.3, 0, 1],
            markup=True
        )
        self.hunter_btn.bind(on_press=self.start_hunter)
        self.add_widget(self.hunter_btn)
        
        # Статус
        self.status_label = Label(
            text='Готов к работе',
            size_hint_y=0.1,
            color=self.theme_colors['text']
        )
        self.add_widget(self.status_label)
        
        # Таймер
        self.timer_label = Label(
            text='',
            size_hint_y=0.1,
            color=[1, 0.5, 0, 1]
        )
        self.add_widget(self.timer_label)
        
        # Переменные
        self.is_turbo = False
        self.is_hunting = False
        self.hunt_seconds = 180
        
        Clock.schedule_interval(self.update_ui, 1)
        
    def change_theme(self, spinner, text):
        self.current_theme = text
        self.theme_colors = THEMES[text]
        self.title.color = self.theme_colors['text']
        self.status_label.color = self.theme_colors['text']
        self.turbo_btn.background_color = self.theme_colors['button']
        
    def update_ui(self, dt):
        if self.is_hunting:
            minutes = self.hunt_seconds // 60
            seconds = self.hunt_seconds % 60
            self.timer_label.text = f'⏳ Осталось: {minutes}:{seconds:02d}'
            
    def update_status(self, text):
        self.status_label.text = text
        
    def start_turbo(self, instance):
        if not self.sub_input.text:
            self.update_status('❌ Вставь ссылку')
            return
        self.is_turbo = True
        self.turbo_btn.disabled = True
        self.hunter_btn.disabled = True
        self.update_status('🚀 ТУРБО запущен')
        threading.Thread(target=self.turbo_loop, daemon=True).start()
        
    def start_hunter(self, instance):
        if not self.sub_input.text:
            self.update_status('❌ Вставь ссылку')
            return
        self.is_hunting = True
        self.hunt_seconds = 180
        self.turbo_btn.disabled = True
        self.hunter_btn.disabled = True
        self.update_status('🔍 ОХОТНИК запущен')
        threading.Thread(target=self.hunter_loop, daemon=True).start()
        
    def extract_ip(self, key):
        match = re.search(r'@([0-9.]+):', key)
        return match.group(1) if match else None
        
    def test_ping(self, ip):
        try:
            result = os.system(f'ping -c 1 -W 1 {ip} >/dev/null 2>&1')
            return result == 0
        except:
            return False
            
    def turbo_loop(self):
        try:
            response = requests.get(self.sub_input.text(), timeout=10)
            if response.status_code == 200:
                keys = re.findall(r'vless://[^\s<>"\']+', response.text)
                self.update_status(f'✅ Найдено {len(keys)} ключей')
                time.sleep(2)
        except Exception as e:
            self.update_status(f'❌ Ошибка: {e}')
        finally:
            self.is_turbo = False
            self.turbo_btn.disabled = False
            self.hunter_btn.disabled = False
            
    def hunter_loop(self):
        try:
            response = requests.get(self.sub_input.text(), timeout=10)
            if response.status_code == 200:
                keys = re.findall(r'vless://[^\s<>"\']+', response.text)
                self.update_status(f'✅ Загружено {len(keys)} ключей')
                
                for i, key in enumerate(keys[:50]):
                    if not self.is_hunting or self.hunt_seconds <= 0:
                        break
                    self.update_status(f'🔍 Проверка {i+1}/{len(keys[:50])}')
                    self.hunt_seconds -= 1
                    time.sleep(0.5)
                    
                self.update_status('🏆 Поиск завершён')
        except Exception as e:
            self.update_status(f'❌ Ошибка: {e}')
        finally:
            self.is_hunting = False
            self.turbo_btn.disabled = False
            self.hunter_btn.disabled = False

class DeepSeApp(App):
    def build(self):
        Window.size = (400, 700)
        return DeepSeLayout()

if __name__ == '__main__':
    DeepSeApp().run()
