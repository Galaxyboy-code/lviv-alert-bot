import requests
import time
from datetime import datetime, timedelta

# VIBER Channels Post API
VIBER_AUTH_TOKEN = "4ff0433b38f5fcc9-a364357ba6cfecf4-beef8c736d55f9f9"
VIBER_POST_URL = "https://chatapi.viber.com/pa/post"

# API тривог
ALERTS_API = "https://api.ukrainealarm.com/api/v2/regions"

# Повідомлення (ТОЛЬКИ ЦІ ЙДУТЬ В КАНАЛ)
ALERT_MSG = "🔴 Львівська область - повітряна тривога!"
CLEAR_MSG = "🟢 Львівська область - відбій повітряної тривоги!"
FOLLOWUP_MSG = """Що куди летить?
Які новини?
Коли тривога?
На каналі Львів
https://invite.viber.com/?g2=AQBzQCL4EeunAk83%2F%2FOF12KWoE%2F7khfwWS%2Brwxzb9s11zTRF6o51lV1zQhg6Gh7S"""

WEEKLY_DONATE_MSG = """Наш канал працює 24/7
І це завдяки вашим донатам 💸
Наш канал цілодобово моніторить обстановку 🔥
По всіх тривогах.
Дуже важко, і довго, моніторимо рано, вдень, і вночі.
🗺️Дякуємо що завжди тут.
➡️Будемо вдячні за підтримку каналу, який працює при потребі 24/7
Карта:
4441 1144 3273 6617
Monobank:
https://send.monobank.ua/jar/ABtvYdkmVS
На зв'язку 🫡"""

class LvivAlertBot:
    def __init__(self):
        self.token = VIBER_AUTH_TOKEN
        self.post_url = VIBER_POST_URL
        self.current_status = None
        self.followup_sent = False
        self.last_donate_time = datetime.now() - timedelta(days=7)
        
        print("🚀 Ініціалізація бота...")
        self.test_connection()
    
    def test_connection(self):
        """Тестує Viber API"""
        test_payload = {
            'auth_token': self.token,
            'from': self.token,
            'type': 'text',
            'text': 'Канал продовжує свою роботу.'
        }
        try:
            response = requests.post(self.post_url, json=test_payload, timeout=10)
            if response.status_code == 200:
                print("✅ Viber API працює! Тест надіслано")
            else:
                print(f"❌ Viber API помилка {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"❌ Помилка тесту: {e}")
    
    def send_viber_post(self, message):
        """Надсилає пост у Viber канал"""
        payload = {
            'auth_token': self.token,
            'from': self.token,
            'type': 'text',
            'text': message
        }
        try:
            response = requests.post(self.post_url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ Пост надіслано: {message[:30]}...")
                return True
            else:
                print(f"❌ Viber помилка {response.status_code}: {response.text[:50]}")
                return False
        except Exception as e:
            print(f"❌ Помилка надсилання: {e}")
            return False
    
    def get_lviv_status(self):
        """Отримати статус Львівської області"""
        try:
            response = requests.get(ALERTS_API, timeout=10)
            response.raise_for_status()
            regions = response.json()
            
            # Шукаємо Львів
            for region in regions:
                region_name = region.get('region', '').lower()
                if any(lviv_name in region_name for lviv_name in ['львів', 'lviv', 'львівська', 'lvivska']):
                    return region.get('status')
            
            print("⚠️ Львів не знайдено в API")
            return None
        except Exception as e:
            print(f"❌ Помилка API тривог: {e}")
            return None
    
    def check_donate_post(self):
        """Щотижневе донат-повідомлення"""
        now = datetime.now()
        if now - self.last_donate_time >= timedelta(days=7):
            print("💰 Час для донат-посту!")
            if self.send_viber_post(WEEKLY_DONATE_MSG):
                self.last_donate_time = now
                print("✅ Донат-пост надіслано")
    
    def run_monitoring(self):
        """Головний цикл моніторингу"""
        print(f"\n🚀 МОНІТОРИНГ ЛЬВІВСЬКОЇ ОБЛАСТІ ЗАПУЩЕНО!")
        print(f"📅 Час запуску: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print("🔄 Перевірка кожні 30 секунд...\n")
        
        consecutive_errors = 0
        max_errors = 5
        
        while True:
            try:
                # Перевірка донат-посту
                self.check_donate_post()
                
                # Отримання статусу Львова
                lviv_status = self.get_lviv_status()
                
                if lviv_status is not None:
                    # Статус отримано
                    consecutive_errors = 0
                    current_time = datetime.now().strftime('%H:%M:%S')
                    status_emoji = "🚨" if lviv_status == 'active' else "🟢"
                    
                    print(f"[{status_emoji}] Львів: {lviv_status} ({current_time})")
                    
                    # Обробка зміни статусу
                    if lviv_status != self.current_status:
                        if lviv_status == 'active':
                            # Початок тривоги
                            print("🚨 ПОЧАТОК ТРИВОГИ!")
                            self.send_viber_post(ALERT_MSG)
                            self.current_status = 'active'
                            self.followup_sent = False
                            
                            # Follow-up через 30 секунд
                            time.sleep(30)
                            if self.current_status == 'active' and not self.followup_sent:
                                print("📢 НАДСИЛАЄМО FOLLOW-UP!")
                                self.send_viber_post(FOLLOWUP_MSG)
                                self.followup_sent = True
                        
                        elif lviv_status == 'inactive' and self.current_status == 'active':
                            # Відбій тривоги
                            print("✅ ОТРИМАНО ВІДБІЙ!")
                            self.send_viber_post(CLEAR_MSG)
                            self.current_status = 'inactive'
                            self.followup_sent = False
                
                else:
                    # Помилка API
                    consecutive_errors += 1
                    print(f"⚠️ Помилка API #{consecutive_errors}")
                    
                    if consecutive_errors >= max_errors:
                        print("💥 БАГАТО ПОМИЛОК — ПАУЗА 5 ХВИЛИН")
                        time.sleep(300)
                        consecutive_errors = 0
                    else:
                        time.sleep(60)
                
                # Пауза між перевірками
                print("⏳ Наступна перевірка через 30 секунд...\n")
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\n⏹️ ЗУПИНКА КОРИСТУВАЧЕМ (Ctrl+C)")
                break
            except Exception as e:
                print(f"💥 НЕОЧІКУВАНА ПОМИЛКА: {e}")
                print("🔄 Продовжуємо через 60 секунд...")
                time.sleep(60)
        
        print("👋 Моніторинг завершено. Дякуємо!")

if __name__ == "__main__":
    print("🎯 VIBER CHANNELS POST API БОТ ДЛЯ ЛЬВОВА")
    print(f"🔑 Auth Token: {VIBER_AUTH_TOKEN[:20]}...")
    print("=" * 50)
    
    # Запуск бота
    bot = LvivAlertBot()
    bot.run_monitoring()
