import os
import gspread
import logging
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Spreadsheet details
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE')

# Initialize Google Sheets client
client = None
sheet = None

async def setup():
    """Setup Google Sheets connection"""
    global client, sheet
    
    # If already set up, just return the sheet
    if sheet is not None:
        return sheet
    
    # Validate environment variables
    if not SPREADSHEET_ID:
        logging.error("SPREADSHEET_ID is not set in the .env file")
        raise ValueError("SPREADSHEET_ID is not set in the .env file")
    
    if not CREDENTIALS_FILE:
        logging.error("GOOGLE_CREDENTIALS_FILE is not set in the .env file")
        raise ValueError("GOOGLE_CREDENTIALS_FILE is not set in the .env file")
    
    if not os.path.exists(CREDENTIALS_FILE):
        logging.error(f"Credentials file not found at: {CREDENTIALS_FILE}")
        raise FileNotFoundError(f"Credentials file not found at: {CREDENTIALS_FILE}")
    
    try:
        # Create credentials from the service account file
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        
        # Authorize with Google
        client = gspread.authorize(creds)
        
        # Open the spreadsheet
        sheet = client.open_by_key(SPREADSHEET_ID)
        
        # Ensure all required worksheets exist
        worksheets = [ws.title for ws in sheet.worksheets()]
        
        required_sheets = ['Services', 'Clients', 'Appointments', 'History', 'Masters', 'Categories', 'Offers', 'VerifiedUsers', 'ServiceTemplates', 'Subscriptions']
        
        for required in required_sheets:
            if required not in worksheets:
                # Create the worksheet if it doesn't exist
                sheet.add_worksheet(title=required, rows=1000, cols=20)
                
                # Add headers based on worksheet
                if required == 'Services':
                    sheet.worksheet(required).append_row(['id', 'name', 'description', 'price', 'duration', 'category_id'])
                elif required == 'Clients':
                    sheet.worksheet(required).append_row(['user_id', 'username', 'full_name', 'role', 'master_id'])
                elif required == 'Appointments':
                    sheet.worksheet(required).append_row(['id', 'user_id', 'service_id', 'date', 'time', 'status', 'master_id', 'payment_method'])
                elif required == 'History':
                    sheet.worksheet(required).append_row(['timestamp', 'user_id', 'service_id', 'date', 'time', 'amount', 'master_id', 'payment_method'])
                elif required == 'Masters':
                    sheet.worksheet(required).append_row(['id', 'telegram_id', 'name', 'telegram', 'phone', 'specialties', 'location', 'description'])
                elif required == 'Categories':
                    sheet.worksheet(required).append_row(['id', 'name'])
                elif required == 'Offers':
                    sheet.worksheet(required).append_row(['id', 'name', 'description', 'price', 'duration'])
                elif required == 'VerifiedUsers':
                    sheet.worksheet(required).append_row(['user_id'])
                elif required == 'ServiceTemplates':
                    sheet.worksheet(required).append_row(['category_name', 'service_name', 'description', 'default_duration', 'category_id'])
                elif required == 'Subscriptions':
                    sheet.worksheet(required).append_row(['user_id', 'start_date', 'end_date', 'trial', 'referrer_id'])
        
        # Initialize template services if ServiceTemplates is empty
        templates_sheet = sheet.worksheet('ServiceTemplates')
        if len(templates_sheet.get_all_records()) == 0:
            initialize_template_services(templates_sheet)
        
        logging.info("Successfully connected to Google Sheets")
        return sheet
    
    except Exception as e:
        logging.error(f"Error connecting to Google Sheets: {str(e)}")
        if "MalformedError" in str(e):
            logging.error("Your credentials file appears to be invalid. Please verify it contains all required fields.")
            logging.error("Run the verify_credentials.py script to check your credentials file.")
        return None

def initialize_template_services(worksheet):
    """Initialize template services with category_id"""
    # Get all categories or create them if they don't exist
    category_ids = {}
    
    templates = [
        # Format: category_name, service_name, description, default_duration
        # Маникюр
        ['Маникюр', 'Классический маникюр', 'Обрезной маникюр с обработкой кутикулы', 45],
        ['Маникюр', 'Аппаратный маникюр', 'Маникюр с использованием аппарата без повреждения кутикулы', 60],
        ['Маникюр', 'Комбинированный маникюр', 'Сочетание классической и аппаратной техники', 60],
        ['Маникюр', 'Маникюр + покрытие гель-лак', 'Маникюр и нанесение стойкого покрытия', 90],
        ['Маникюр', 'Укрепление ногтей (биогель/акрил)', 'Укрепление натуральных ногтей', 75],
        ['Маникюр', 'Снятие гель-лака', 'Бережное снятие старого покрытия', 30],
        ['Маникюр', 'Ремонт ногтя', 'Восстановление поврежденного ногтя', 20],
        ['Маникюр', 'Дизайн 1-2 ногтя', 'Художественное оформление отдельных ногтей', 30],
        ['Маникюр', 'Дизайн всех ногтей', 'Художественное оформление всех ногтей', 60],
        
        # Педикюр
        ['Педикюр', 'Классический педикюр', 'Обрезной педикюр с обработкой кутикулы и стоп', 60],
        ['Педикюр', 'Аппаратный педикюр', 'Современный педикюр с использованием аппарата', 75],
        ['Педикюр', 'Комбинированный педикюр', 'Сочетание классической и аппаратной техники', 75],
        ['Педикюр', 'Педикюр + гель-лак', 'Педикюр со стойким покрытием ногтей', 90],
        ['Педикюр', 'Снятие покрытия', 'Удаление старого гель-лака', 30],
        ['Педикюр', 'Обработка трещин/мозолей', 'Профессиональное решение проблем стоп', 45],
        
        # Брови
        ['Брови', 'Коррекция формы бровей', 'Моделирование формы бровей пинцетом/воском/нитью', 30],
        ['Брови', 'Окрашивание краской', 'Стойкое окрашивание бровей', 30],
        ['Брови', 'Окрашивание хной', 'Натуральное окрашивание хной с эффектом татуажа', 45],
        ['Брови', 'Ламинирование бровей', 'Фиксация волосков в нужном направлении', 60],
        ['Брови', 'Архитектура бровей (комплекс)', 'Полный комплекс по созданию идеальной формы', 75],
        
        # Ресницы
        ['Ресницы', 'Наращивание классика', 'Классическое наращивание ресниц 1:1', 120],
        ['Ресницы', '2D объем', 'Наращивание ресниц с объемом 1:2', 150],
        ['Ресницы', '3D объем', 'Наращивание ресниц с объемом 1:3', 180],
        ['Ресницы', 'Мега-объем', 'Максимально объемное наращивание', 210],
        ['Ресницы', 'Снятие ресниц', 'Безопасное удаление нарощенных ресниц', 30],
        ['Ресницы', 'Ламинирование ресниц', 'Процедура для завитка и укрепления ресниц', 90],
        ['Ресницы', 'Окрашивание ресниц', 'Стойкое окрашивание натуральных ресниц', 30],
        
        # Косметология / уход за лицом
        ['Косметология', 'Чистка лица механическая', 'Глубокое очищение кожи лица', 90],
        ['Косметология', 'Чистка лица ультразвук', 'Деликатная чистка с использованием ультразвука', 75],
        ['Косметология', 'Чистка лица комбинированная', 'Комплексная чистка кожи', 120],
        ['Косметология', 'Пилинг', 'Обновление кожи с помощью химических составов', 60],
        ['Косметология', 'Маска/уходовая процедура', 'Интенсивный уход с применением профессиональных средств', 45],
        ['Косметология', 'Массаж лица', 'Миолифтинг, лимфодренаж и другие техники', 45],
        ['Косметология', 'Карбокситерапия', 'Неинвазивная процедура насыщения кожи кислородом', 60],
        ['Косметология', 'Дарсонваль/аппаратные методики', 'Аппаратное омоложение и лечение кожи', 45],
        
        # Массаж
        ['Массаж', 'Классический массаж', 'Общеоздоровительный массаж тела', 60],
        ['Массаж', 'Антицеллюлитный', 'Интенсивный массаж проблемных зон', 60],
        ['Массаж', 'Лимфодренажный', 'Улучшение лимфотока и вывод лишней жидкости', 75],
        ['Массаж', 'Спина/шея/зона декольте', 'Массаж верхней части тела', 45],
        ['Массаж', 'Массаж лица', 'Омолаживающий и расслабляющий массаж лица', 30],
        ['Массаж', 'Расслабляющий массаж', 'Снятие напряжения, релаксация', 90],
        
        # Парикмахерские услуги
        ['Парикмахерские услуги', 'Стрижка женская', 'Модельная женская стрижка', 60],
        ['Парикмахерские услуги', 'Стрижка мужская', 'Классическая и модельная мужская стрижка', 45],
        ['Парикмахерские услуги', 'Стрижка детская', 'Стрижка для детей', 30],
        ['Парикмахерские услуги', 'Укладка', 'Укладка феном, утюжком или плойкой', 45],
        ['Парикмахерские услуги', 'Окрашивание в один тон', 'Равномерное окрашивание волос', 120],
        ['Парикмахерские услуги', 'Мелирование', 'Частичное окрашивание прядей', 150],
        ['Парикмахерские услуги', 'Балаяж/омбре', 'Градиентное окрашивание волос', 180],
        ['Парикмахерские услуги', 'Ламинирование ��олос', 'Восстановление и глянцевание волос', 90],
        ['Парикмахерские услуги', 'Кератин/ботокс', 'Глубокое восстановление структуры волос', 180],
        ['Парикмахерские услуги', 'Уходовые процедуры', 'Профессиональный уход за волосами', 60],
        
        # Депиляция / шугаринг
        ['Депиляция', 'Ноги полностью', 'Удаление волос на всей поверхности ног', 90],
        ['Депиляция', 'Ноги до колена', 'Удаление волос на голенях', 45],
        ['Депиляция', 'Бедра', 'Удаление волос в области бедер', 45],
        ['Депиляция', 'Руки полностью', 'Удаление волос на руках', 45],
        ['Депиляция', 'Подмышки', 'Удаление волос в подмышечных впадинах', 20],
        ['Депиляция', 'Бикини классическое', 'Удаление волос по линии белья', 30],
        ['Депиляция', 'Бикини глубокое', 'Полное удаление волос в интимной зоне', 60],
        ['Депиляция', 'Лицо', 'Удаление волос на лице (верхняя губа, подбородок)', 20],
        ['Депиляция', 'Мужская депиляция', 'Удаление волос для мужчин (спина/грудь/др.)', 90],
        ['Депиляция', 'Уход после процедуры', 'Успокаивающие и противовоспалительные средства', 15]
    ]
    
    # Add template services in batches to avoid API limits
    batch_size = 20
    for i in range(0, len(templates), batch_size):
        batch = templates[i:i+batch_size]
        
        # Add category_id field to each template service
        enhanced_batch = []
        for template in batch:
            category_name = template[0]
            # We'll set a placeholder for category_id - it will be updated later
            enhanced_template = template + [""]
            enhanced_batch.append(enhanced_template)
            
        worksheet.append_rows(enhanced_batch)
    
    return True

async def get_sheet(sheet_name):
    """Get data from a specific sheet"""
    global sheet
    
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            logging.error(f"Error getting sheet {sheet_name}: sheet is not initialized")
            return []
    
    try:
        # Get the worksheet
        worksheet = sheet.worksheet(sheet_name)
        
        # Get all data from the sheet
        data = worksheet.get_all_records()
        
        return data
    except Exception as e:
        logging.error(f"Error getting sheet {sheet_name}: {str(e)}")
        return []

async def write_to_sheet(sheet_name, data):
    """Write data to a specific sheet"""
    global sheet
    
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            logging.error(f"Error writing to sheet {sheet_name}: sheet is not initialized")
            return False
    
    try:
        # Get the worksheet
        worksheet = sheet.worksheet(sheet_name)
        
        # Get the headers
        headers = worksheet.row_values(1)
        
        # Clear the sheet (except headers)
        if worksheet.row_count > 1:
            worksheet.delete_rows(2, worksheet.row_count)
        
        # Write the data
        rows = []
        for item in data:
            row = []
            for header in headers:
                row.append(item.get(header, ""))
            rows.append(row)
        
        # If there's data, append it
        if rows:
            worksheet.append_rows(rows)
        
        return True
    except Exception as e:
        logging.error(f"Error writing to sheet {sheet_name}: {str(e)}")
        return False
