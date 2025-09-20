import requests
import time
import json
from datetime import datetime, timedelta

# VIBER Channels Post API — ваш токен
VIBER_AUTH_TOKEN = "4ff0433b38f5fcc9-a364357ba6cfecf4-beef8c736d55f9f9"
VIBER_POST_URL = "https://chatapi.viber.com/pa/post"

# НОВИЙ ПУБЛІЧНИЙ API ТРИВОГ (без ключа, siren.pp.ua)
ALERTS_API = "https://siren.pp.ua/api/v1/regions"  # Публічний wrapper для Ukraine Alarm

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
        
        print("=" * 50)
        print(f"🚀 VIBER BOT ДЛЯ ЛЬВОВА ЗАПУЩЕНО (НОВИЙ API siren.pp.ua)!")
        print(f"📅 Час: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print(f"🔑 Auth Token: {self.token[:20]}...")
        print(f"📡 API тривог: {ALERTS_API}")
        print("=" * 50)
        
        # ТЕСТ VIBER API
        self.test_viber_api()
    
    def test_viber_api(self):
        """Тест з повним логуванням"""
        print("\n🧪 ТЕСТ VIBER API...")
        
        test_payload = {
            'auth_token': self.token,
            'from': self.token,
            'type': 'text',
            'text': '🧪 Railway: Бот оновлено! Новий API тривог.'
        }
        
        print(f"📤 Відправляємо запит: {json.dumps(test_payload, indent=2)}")
        
        try:
            response = requests.post(self.post_url, json=test_payload, timeout=15)
            print(f"📥 Відповідь Viber:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
            if response.status_code == 200:
                print("✅ ✅ ✅ VIBER API ПРАЦЮЄ! Тест надіслано в канал")
            else:
                print(f"❌ ❌ ❌ VIBER API ПОМИЛКА {response.status_code}")
                if response.status_code == 2:
                    print("   ПРИЧИНА: Невірний auth_token")
                elif response.status_code == 12:
                    print("   ПРИЧИНА: Rate limit")
                
        except Exception as e:
            print(f"❌ ❌ ❌ ПОМИЛКА ТЕСТУ: {type(e).__name__}: {str(e)}")
        
        print("\n" + "=" * 50)
    
    def send_viber_post(self, message):
        """Надсилає пост з логуванням"""
        print(f"\n📤 НАДСИЛАЄМО: '{message[:50]}...'")
        
        payload = {
            'auth_token': self.token,
            'from': self.token,
            'type': 'text',
            'text': message
        }
        
        try:
            response = requests.post(self.post_url, json=payload, timeout=15)
            print(f"📥 Status: {response.status_code}")
            print(f"📥 Response: {response.text[:100]}")
            
            if response.status_code == 200:
                print("✅ ✅ ✅ ПОСТ НАДІСЛАНО!")
                return True
            else:
                print(f"❌ ❌ ❌ ПОМИЛКА {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ ❌ ❌ ПОМИЛКА НАДСИЛАННЯ: {type(e).__name__}: {str(e)}")
            return False
    
    def get_lviv_status(self):
        """Статус Львова з НОВИМ API siren.pp.ua"""
        print("\n🔍 ОТРИМУЄМО СТАТУС ЛЬВОВА (siren.pp.ua)...")
        
        try:
            print(f"📡 Запит до {ALERTS_API}")
            response = requests.get(ALERTS_API, timeout=15)
            print(f"📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Структура відповіді: {json.dumps(data, indent=2)[:200]}...")  # Перші 200 символів
                
                # Формат siren.pp.ua: {"data": {"regions": [{"name": "Львівська", "status": "active/inactive"}]}}
                if 'data' in data and 'regions' in data['data']:
                    regions = data['data']['regions']
                    print(f"📊 Знайдено регіонів: {len(regions)}")
                    
                    for i, region in enumerate(regions):
                        region_name = region.get('name', '')
                        status = region.get('status', 'unknown')
                        print(f"   Регіон {i+1}: '{region_name}' — статус: {status}")
                        
                        if 'львів' in region_name.lower() or 'lviv' in region_name.lower():
                            print(f"🎯 ЗНАЙДЕНО ЛЬВІВ: '{region_name}' — статус: {status}")
                            return status
                
                print("⚠️ ⚠️ ЛЬВІВ НЕ ЗНАЙДЕНО В СПИСКІ РЕГІОНІВ")
                return None
            else:
                print(f"❌ ❌ НОВИЙ API ПОМИЛКА {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ ❌ ПОМИЛКА НОВОГО API: {type(e).__name__}: {str(e)}")
            return None
    
    def check_donate_post(self):
        """Щотижневе донат-повідомлення"""
        now = datetime.now()
        days_since_donate = (now - self.last_donate_time).days
        
        if days_since_donate >= 7:
            print(f"\n💰 ЧАС ДЛЯ ДОНАТ-ПОСТУ (минуло {days_since_donate} днів)")
            if self.send_viber_post(WEEKLY_DONATE_MSG):
                self.last_donate_time = now
                print("✅ ✅ ✅ ДОНАТ-ПОСТ НАДІСЛАНО!")
            else:
                print("❌ ❌ ❌ ПОМИЛКА ДОНАТ-ПОСТУ")
    
    def run_monitoring(self):
        """Головний цикл з детальним логуванням"""
        print(f"\n🚀 🚀 🚀 ПОЧАТОК МОНІТОРИНГУ ЛЬВОВА (НОВИЙ API)!")
        print(f"📅 Старт: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print("🔄 Перевірка кожні 30 секунд...\n")
        
        cycle_count = 0
        consecutive_errors = 0
        max_errors = 5
        
        while True:
            try:
                cycle_count += 1
                print(f"\n🔄 ЦИКЛ #{cycle_count} — {datetime.now().strftime('%H:%M:%S')}")
                
                # Перевірка донат-посту
                self.check_donate_post()
                
                # Отримання статусу Львова
                lviv_status = self.get_lviv_status()
                
                if lviv_status is not None:
                    # Статус отримано успішно
                    consecutive_errors = 0
                    status_emoji = "🚨" if lviv_status == 'active' else "🟢"
                    current_time = datetime.now().strftime('%H:%M:%S')
                    
                    print(f"📊 СТАТУС ЛЬВОВА: [{status_emoji}] {lviv_status} ({current_time})")
                    
                    # Обробка зміни статусу
                    if lviv_status != self.current_status:
                        print(f"🔄 🔄 ЗМІНА СТАТУСУ: {self.current_status} → {lviv_status}")
                        
                        if lviv_status == 'active':
                            # ТРИВОГА!
                            print("🚨 🚨 🚨 ПОЧАТОК ПОВІТРЯНОЇ ТРИВОГИ!")
                            if self.send_viber_post(ALERT_MSG):
                                print("✅ ✅ ✅ ТРИВОГА НАДІСЛАНА!")
                            self.current_status = 'active'
                            self.followup_sent = False
                            
                            # Follow-up через 30 секунд
                            print("⏳ Чекаємо 30 секунд для follow-up...")
                            time.sleep(30)
                            
                            if self.current_status == 'active' and not self.followup_sent:
                                print("📢 📢 НАДСИЛАЄМО FOLLOW-UP!")
                                if self.send_viber_post(FOLLOWUP_MSG):
                                    print("✅ ✅ ✅ FOLLOW-UP НАДІСЛАНО!")
                                self.followup_sent = True
                        
                        elif lviv_status == 'inactive' and self.current_status == 'active':
                            # ВІДБІЙ!
                            print("✅ ✅ ✅ ОТРИМАНО ВІДБІЙ ТРИВОГИ!")
                            if self.send_viber_post(CLEAR_MSG):
                                print("✅ ✅ ✅ ВІДБІЙ НАДІСЛАНО!")
                            self.current_status = 'inactive'
                            self.followup_sent = False
                    else:
                        print(f"📊 Статус не змінився: {lviv_status}")
                
                else:
                    # Помилка отримання статусу
                    consecutive_errors += 1
                    print(f"⚠️ ⚠️ ПОМИЛКА ОТРИМАННЯ СТАТУСУ #{consecutive_errors}")
                    
                    if consecutive_errors >= max_errors:
                        print("💥 💥 БАГАТО ПОМИЛОК — ПАУЗА 5 ХВИЛИН")
                        time.sleep(300)
                        consecutive_errors = 0
                    else:
                        print("⏳ Пауза 60 секунд...")
                        time.sleep(60)
                
                # Пауза між циклами
                print(f"⏳ Цикл #{cycle_count} завершено. Пауза 30 секунд...")
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\n⏹️ ⏹️ ЗУПИНКА КОРИСТУВАЧЕМ (Ctrl+C)")
                break
            except Exception as e:
                print(f"\n💥 💥 НЕОЧІКУВАНА ПОМИЛКА В ЦИКЛІ #{cycle_count}:")
                print(f"   Тип: {type(e).__name__}")
                print(f"   Повідомлення: {str(e)}")
                print("🔄 Продовжуємо через 60 секунд...")
                time.sleep(60)
        
        print("\n👋 👋 Моніторинг завершено. Дякуємо!")

# ЗАПУСК
if __name__ == "__main__":
    print("🎯 🎯 VIBER BOT ДЛЯ ЛЬВОВА — РОБОЧИЙ РЕЖИМ")
    print("=" * 60)
    
    try:
        bot = LvivAlertBot()
        bot.run_monitoring()
    except Exception as e:
        print(f"\n💥 💥 КРИТИЧНА ПОМИЛКА ПРИ ЗАПУСКУ: {type(e).__name__}: {str(e)}")
        print("🔧 Спробуйте перезапустити або перевірте налаштування")
