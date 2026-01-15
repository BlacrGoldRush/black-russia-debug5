import os
import logging
import requests
from flask import Flask
from bs4 import BeautifulSoup
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

def super_simple_parser():
    """СУПЕР ПРОСТОЙ парсер - только извлечение данных без сложной обработки"""
    try:
        url = "https://funpay.com/chips/186/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        logger.info("🚀 Запуск супер простого парсера...")
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            logger.error(f"❌ HTTP ошибка: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем карточки
        cards = soup.find_all('a', class_='tc-item')
        logger.info(f"📦 Всего карточек на странице: {len(cards)}")
        
        items = []
        
        # Берем только первые 10 карточек
        for i, card in enumerate(cards[:10]):
            try:
                logger.info(f"\n--- Карточка {i+1} ---")
                
                # 1. Показываем сырой HTML карточки (первые 500 символов)
                card_html = str(card)[:500]
                logger.info(f"HTML карточки: {card_html}...")
                
                # 2. Пробуем извлечь название разными способами
                title = None
                
                # Способ 1: через tc-desc-text
                title_elem = card.find('div', class_='tc-desc-text')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    logger.info(f"Название (tc-desc-text): {title}")
                else:
                    # Способ 2: ищем любой текст в карточке
                    all_text = card.get_text(strip=True)
                    if all_text:
                        # Берем первые 100 символов как заголовок
                        title = all_text[:100]
                        logger.info(f"Название (весь текст): {title}")
                
                if not title:
                    logger.info("❌ Не удалось извлечь название")
                    continue
                
                # 3. Пробуем извлечь цену
                price = None
                price_elem = card.find('div', class_='tc-price')
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    logger.info(f"Текст цены: '{price_text}'")
                    
                    # Пробуем найти цифры в тексте
                    import re
                    digits = re.findall(r'\d+', price_text.replace(' ', ''))
                    if digits:
                        price = int(''.join(digits))
                        logger.info(f"Цена (цифры): {price}")
                
                # 4. Извлекаем ссылку
                link = None
                href = card.get('href', '')
                if href:
                    if href.startswith('/'):
                        link = f"https://funpay.com{href}"
                    else:
                        link = href
                    logger.info(f"Ссылка: {link}")
                
                # 5. Статус онлайн
                online_attr = card.get('data-online', '')
                logger.info(f"data-online атрибут: {online_attr}")
                
                # Если получили и название, и цену - добавляем
                if title and price:
                    items.append({
                        'title': title,
                        'price': price,
                        'link': link or url,
                        'online': online_attr == '1'
                    })
                    logger.info(f"✅ Карточка {i+1} успешно обработана")
                else:
                    logger.info(f"❌ Карточка {i+1} не прошла проверку (title: {bool(title)}, price: {bool(price)})")
                    
            except Exception as e:
                logger.error(f"💥 Ошибка при обработке карточки {i+1}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"\n🎯 ИТОГО успешно обработано: {len(items)} карточек")
        return items
        
    except Exception as e:
        logger.error(f"💥 Критическая ошибка парсера: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

# Маршруты Flask
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>FunPay Парсер - Дебаг версия</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            .btn { display: inline-block; padding: 10px 20px; margin: 5px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>🔧 FunPay Парсер - Дебаг версия</h1>
        <p><strong>Цель:</strong> Узнать почему парсер не обрабатывает карточки</p>
        <p><strong>Время:</strong> ''' + datetime.now().strftime("%H:%M:%S") + '''</p>
        
        <h3>Действие:</h3>
        <a href="/parse" class="btn">🚀 Запустить дебаг-парсер</a>
        
        <h3>Что будет:</h3>
        <ol>
            <li>Парсер обработает первые 10 карточек</li>
            <li>В логах появится ДЕТАЛЬНАЯ информация по каждой карточке</li>
            <li>Мы увидим HTML структуру и данные</li>
            <li>Я смогу понять в чем проблема</li>
        </ol>
        
        <p><strong>После запуска пришлите мне логи!</strong></p>
    </body>
    </html>
    '''

@app.route('/parse')
def parse_page():
    """Страница парсинга"""
    items = super_simple_parser()
    
    if items:
        result = f"<h2>✅ Успешно обработано: {len(items)} карточек</h2>"
        for item in items:
            online_badge = "🟢 ОНЛАЙН" if item['online'] else "🔴 ОФФЛАЙН"
            result += f'''
            <div style="border:1px solid #ddd; padding:15px; margin:10px;">
                <h4>{item['title'][:80]}</h4>
                <p><strong>Цена:</strong> {item['price']} руб.</p>
                <p><strong>Статус:</strong> {online_badge}</p>
                <p><a href="{item['link']}" target="_blank">Ссылка</a></p>
            </div>
            '''
    else:
        result = '''
        <div style="background:#f8d7da; padding:20px; border-radius:5px;">
            <h2>❌ Карточки не обработаны</h2>
            <p>Парсер не смог обработать ни одну карточку.</p>
            <p><strong>Но в логах есть детальная информация!</strong></p>
            <p>Пришлите мне логи из Render, и я увижу в чем проблема.</p>
        </div>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head><title>Результаты парсинга</title></head>
    <body style="font-family:Arial; margin:20px;">
        <a href="/">← Назад</a>
        {result}
        <p><strong>Важно:</strong> Проверьте логи на Render (вкладка Logs). Там будет HTML структура карточек.</p>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return "OK"

# Запуск приложения
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
