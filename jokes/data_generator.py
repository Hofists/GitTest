import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
from sqlmodel import Session, select
from database.connection import engine
from models.users import User
from models.anecdotes import Anecdote
from models.interactions import Rating, Favorite
from models.inform_sys import InformSys
from tqdm import tqdm
import os

fake = Faker('ru_RU')

class TestDataGenerator:
    def __init__(self):
        self.fake = fake
        # Расширенные шаблоны и словари из задания
        self.anecdote_templates = [
            # Классические шаблоны
            "Идет {} по {} и видит {}. {} говорит: '{}'",
            "Встречаются {} и {}. Первый спрашивает: '{}?', второй отвечает: '{}'",
            "Приходит {} к {} и просит: '{}'. {} отвечает: '{}'",
            "Стоит {} на {}. Вдруг подходит {} и говорит: '{}'",
            "Почему {} не может {}? Потому что {}!",
            
            # Новые IT-шаблоны
            "{} заходит в {} и видит {}, который {}: '{}'",
            "Сколько {} нужно, чтобы {}? Ни одного, потому что {}",
            "{} вызывает {} и просит: '{}'. {} в ответ: '{}'",
            "Сидит {} за {}, вдруг {} и {}: '{}'",
            "Приходит {} на собеседование. Спрашивают: '{}?'. {} отвечает: '{}'",
            
            # Диалоговые шаблоны
            "{} жалуется {}: '{}'. {} советует: '{}'",
            "Разговаривают {} и {} о {}. Вдруг {} говорит: '{}'",
            "Спорят {} и {}: первый говорит '{}', второй возражает: '{}'",
            "{} звонит {} среди ночи: '{}'. {} спросонья: '{}'",
            
            # Жизненные ситуации
            "Приходит {} из {} и видит, что {} {}: '{}'",
            "Собрались {} в {} и решили {}: '{}'",
            "Просыпается {} утром и понимает, что {}: '{}'",
            "Заходит {} в лифт, а там {} и {}: '{}'",
            
            # Абсурдные комбинации
            "Если {} встретит {} в {}, то {} обязательно {}: '{}'",
            "{} мечтает {}, но {} ему: '{}'",
            "Однажды {} решил стать {}, но {} был против: '{}'",
            "Представьте: {} работает {}, а {} его учит {}: '{}'",
            
            # Короткие анекдоты
            "Объявление: {} ищет {}, чтобы {}: '{}'",
            "{} не может {} уже {} дней. Всё из-за того, что {}",
            "Секрет {}: чтобы {}, нужно просто {}!",
            "{} попросил {} объяснить {}, но {} сам {} не понимает",
        ]
        
        self.characters = [
            # IT-специалисты
            "программист", "сисадмин", "хакер", "QA-инженер", "тимлид", "джун", "сеньор", 
            "верстальщик", "фронтендер", "бэкендер", "фуллстек-разработчик", "девопс",
            "программист на Python", "программист на Java", "программист на C++",
            "айтишник", "криптограф", "дата-сайентист", "сетевой инженер", 
            "тестировщик", "продукт-менеджер", "аналитик", "дизайнер",
            
            # Обычные люди
            "студент", "школьник", "преподаватель", "директор", "бухгалтер",
            "менеджер", "маркетолог", "фрилансер", "стартапер", "инвестор",
            "бабушка", "дедушка", "внук", "внучка", "сосед", "соседка",
            "дворник", "продавец", "полицейский", "врач", "учительница",
            "домохозяйка", "пенсионер", "бизнесмен", "блогер", "тиктокер",
            
            # Животные и персонажи
            "кот", "собака", "попугай", "хомяк", "рыбка", "робот",
            "нейросеть", "бот", "ChatGPT", "Яндекс.Алиса", "Siri",
            "Ктулху", "Билл Гейтс", "Илон Маск", "Марк Цукерберг",
            "Стив Джобс", "Линус Торвальдс", "Дональд Кнут"
        ]
        
        self.locations = [
            # Рабочие места
            "работе", "офисе", "удаленке", "коворкинге", "переговорке",
            "айти-конференции", "хакатоне", "митапе", "лекции", "паре",
            "универе", "школе", "библиотеке", "кабинете директора",
            "серверной", "дата-центре", "коворкинге", "стартап-инкубаторе",
            
            # Домашние места
            "кухне", "балконе", "ванной", "спальне", "коридоре",
            "квартире", "общаге", "гараже", "подвале", "чердаке",
            
            # Городские места
            "улице", "парке", "сквере", "набережной", "пляже",
            "кафе", "ресторане", "баре", "столовой", "пиццерии",
            "магазине", "рынке", "торговом центре", "аптеке", "банке",
            "метро", "остановке", "вокзале", "аэропорту", "поезде",
            "такси", "автобусе", "троллейбусе", "трамвае",
            
            # Виртуальные места
            "интернете", "соцсетях", "Telegram", "ВКонтакте", "TikTok",
            "YouTube", "GitHub", "Stack Overflow", "Zoom", "Discord",
            "матрице", "метавселенной", "криптобирже", "даркнете",
            
            # Фантастические места
            "планете Python", "острове Java", "горах C++", "пустыне JavaScript",
            "лесу бинарных деревьев", "море данных", "облаке AWS"
        ]
        
        self.objects = [
            # Техника
            "компьютер", "ноутбук", "нетбук", "планшет", "смартфон",
            "айфон", "самсунг", "макбук", "сервер", "роутер",
            "клавиатуру", "мышку", "монитор", "принтер", "сканер",
            "наушники", "веб-камеру", "микрофон", "джойстик", "стилус",
            "флешку", "внешний диск", "SSD", "процессор", "видеокарту",
            
            # Книги и информация
            "книгу", "учебник", "методичку", "конспект", "диплом",
            "курсовую", "реферат", "лабораторную", "код", "программу",
            "базу данных", "репозиторий", "алгоритм", "фреймворк",
            
            # Животные
            "кота", "собаку", "попугая", "хомяка", "рыбку", "черепаху",
            "хамелеона", "ежа", "белку", "лису",
            
            # Предметы
            "кружку кофе", "чай", "пиццу", "бургер", "сэндвич",
            "доширак", "энергетик", "колу", "пиво", "печеньки",
            "бутерброд", "яблоко", "банан", "шоколадку",
            
            # Странные вещи
            "баг", "фичу", "легаси-код", "техдолг", "дедлайн",
            "спринт", "бэклог", "микросервис", "контейнер", "виртуалку",
            "биткоин", "крипту", "блокчейн", "смарт-контракт", "токен",
            "нейросеть", "искусственный интеллект", "алгоритм", "функцию", "класс"
        ]
        
        self.phrases = [
            # Технические проблемы
            "почему не работает интернет", "сломался компьютер", "зависла программа",
            "не грузится Windows", "синий экран смерти", "пропал звук",
            "не включается монитор", "мышка не двигается", "клавиатура залипла",
            "принтер жует бумагу", "закончилась память", "села батарейка",
            "упал сервер", "потерялись данные", "вирус всё съел",
            
            # IT-запросы
            "как взломать Пентагон", "напиши мне нейросеть", "создай TikTok за час",
            "закодируй блокчейн", "задеплой на прод", "оптимизируй код",
            "перепиши с Python на Java", "добавь фичу", "пофикси баги",
            "напиши ТЗ", "сделай ревью кода", "помоги с алгоритмом",
            "как выучить Python за неделю", "где скачать IDE", "установи линукс",
            
            # Бытовые фразы
            "дай денег в долг", "одолжи до зарплаты", "угости пиццей",
            "принеси кофе", "сходи в магазин", "открой дверь",
            "помоги переставить мебель", "посиди с котом", "погуляй с собакой",
            "позвони маме", "напиши сообщение", "отправь фотку",
            
            # Учебные запросы
            "напиши курсовую за меня", "реши контрольную", "сделай лабораторную",
            "объясни тему", "помоги с экзаменом", "подготовь презентацию",
            "переведи текст", "найди информацию", "напиши реферат",
            
            # Странные вопросы
            "почему я не могу зайти в TikTok", "как накрутить лайки",
            "где скачать Windows бесплатно", "как взломать ВКонтакте",
            "почему меня никто не лайкает", "как стать блогером",
            "сколько зарабатывает программист", "как уйти в айти",
            "почему котики такие милые", "в чем смысл жизни",
            "как выучить английский за месяц", "что такое любовь",
            
            # Ответы и фразы
            "я не знаю", "отстань", "иди сам разбирайся", "гугли в помощь",
            "стек оверфлоу в помощь", "заплатишь - сделаю", "я устал, я ухожу",
            "попробуй перезагрузить", "а ты антивирус обновил", "виноват глобал варминг",
            "это не баг, это фича", "у меня тоже не работает", "понедельник - день тяжелый",
            "всё сложно", "легко!", "сделано", "работает на моей машине",
            "нужно больше кофе", "без кофе не разговариваю", "пиши код, а то застрелю",
            
            # Шутки
            "я программист, я отдыхаю только когда комп зависает",
            "мы не волшебники, мы только учимся",
            "кто рано встает, тот ничего не делает, пока все спят",
            "ленивый программист - хороший программист",
            "работа не волк, а козел - и траву жрет, и людей бодает"
        ]
        
        self.actions = [
            "завис", "упал", "сломался", "отвалился", "сгорел", "утонул",
            "сбежал", "заблудился", "влюбился", "женился", "родил",
            "написал код", "удалил всё", "сломал прод", "залил фикс",
            "пропатчил", "закоммитил", "запушил", "замержил",
            "рефакторил", "оптимизировал", "деплоил", "тестировал"
        ]
        
        self.conditions = [
            "без кофе", "без интернета", "с похмелья", "в трусах",
            "в маске", "с котом на руках", "под столом", "на стуле",
            "на удаленке", "в носках разных цветов", "с чашкой чая",
            "с ноутбуком на коленях", "в наушниках", "с микрофоном"
        ]
        
    def generate_anecdote_text(self):
        """Генерирует текст анекдота по шаблону"""
        template = random.choice(self.anecdote_templates)
        # Подсчитываем количество плейсхолдеров {}
        placeholders = template.count('{}')
        args = []
        for i in range(placeholders):
            # Выбираем случайный тип данных для каждого плейсхолдера
            choice = random.choice(['char', 'loc', 'obj', 'phrase', 'action', 'cond'])
            if choice == 'char':
                args.append(random.choice(self.characters))
            elif choice == 'loc':
                args.append(random.choice(self.locations))
            elif choice == 'obj':
                args.append(random.choice(self.objects))
            elif choice == 'phrase':
                args.append(random.choice(self.phrases))
            elif choice == 'action':
                args.append(random.choice(self.actions))
            elif choice == 'cond':
                args.append(random.choice(self.conditions))
        return template.format(*args)

    def generate_users_batch(self, session, num_users, batch_size=1000):
        """Генерирует пользователей пачками и возвращает список их ID"""
        user_ids = []
        users_batch = []
        inform_batch = []
        
        for i in tqdm(range(num_users), desc="Генерация пользователей"):
            email = self.fake.unique.email()
            username = self.fake.unique.user_name()
            password = self.fake.password(length=10)
            
            user = User(email=email, password=password, username=username)
            users_batch.append(user)
            
            # Для inform_sys нужно сохранить связь после получения ID
            # Поэтому сначала добавим пользователя, flush, потом inform
            # Но для массовости лучше сделать два этапа: сначала вставить пользователей, получить их ID, потом inform.
        
        # Вставляем пользователей пачками
        session.add_all(users_batch)
        session.flush()  # присваивает ID
        
        # Теперь создаём inform-записи
        for user in users_batch:
            inform = InformSys(
                source_table="user",
                original_id=user.id,
                email=user.email,
                username=user.username
            )
            inform_batch.append(inform)
            user_ids.append(user.id)
        
        session.add_all(inform_batch)
        session.commit()
        
        return user_ids

    def generate_anecdotes_batch(self, session, author_ids, num_anecdotes, batch_size=1000):
        """Генерирует анекдоты пачками и возвращает список их ID"""
        anecdote_ids = []
        anecdotes_batch = []
        inform_batch = []
        
        for i in tqdm(range(num_anecdotes), desc="Генерация анекдотов"):
            author_id = random.choice(author_ids)
            content = self.generate_anecdote_text()
            publication_date = datetime.now() - timedelta(days=random.randint(0, 365))
            
            anecdote = Anecdote(
                content=content,
                author_id=author_id,
                publication_date=publication_date,
                likes_count=0
            )
            anecdotes_batch.append(anecdote)
            
            if len(anecdotes_batch) >= batch_size:
                session.add_all(anecdotes_batch)
                session.flush()
                
                for a in anecdotes_batch:
                    inform = InformSys(
                        source_table="anecdote",
                        original_id=a.id,
                        content=a.content,
                        author_or_user_id=a.author_id,
                        publication_date=a.publication_date,
                        likes_count=a.likes_count
                    )
                    inform_batch.append(inform)
                    anecdote_ids.append(a.id)
                
                session.add_all(inform_batch)
                session.commit()
                anecdotes_batch = []
                inform_batch = []
        
        # Остаток
        if anecdotes_batch:
            session.add_all(anecdotes_batch)
            session.flush()
            for a in anecdotes_batch:
                inform = InformSys(
                    source_table="anecdote",
                    original_id=a.id,
                    content=a.content,
                    author_or_user_id=a.author_id,
                    publication_date=a.publication_date,
                    likes_count=a.likes_count
                )
                inform_batch.append(inform)
                anecdote_ids.append(a.id)
            session.add_all(inform_batch)
            session.commit()
        
        return anecdote_ids

    def generate_interactions_batch(self, session, user_ids, anecdote_ids, 
                                    num_ratings, num_favorites, batch_size=5000):
        """Генерирует оценки и избранное, гарантируя уникальность пар (user, anecdote)"""
        
        # Множество для контроля уникальности
        used_pairs = set()
        
        # Генерация оценок
        ratings_batch = []
        ratings_inform_batch = []
        ratings_count = 0
        
        # Для обновления likes_count в анекдотах будем накапливать изменения
        anecdote_likes_delta = {}
        
        # Сначала генерируем оценки
        pbar = tqdm(total=num_ratings, desc="Генерация оценок")
        while ratings_count < num_ratings:
            user_id = random.choice(user_ids)
            anecdote_id = random.choice(anecdote_ids)
            # Не оцениваем свой анекдот? Для реализма можно разрешить, но пусть будет нельзя
            # Узнаем автора анекдота – для этого нужен запрос к БД, что медленно.
            # Упростим: разрешим оценивать свой анекдот (иногда так бывает)
            
            pair = (user_id, anecdote_id)
            if pair in used_pairs:
                continue
            
            value = random.choice([-1, 1])
            rating = Rating(
                user_id=user_id,
                anecdote_id=anecdote_id,
                value=value
            )
            ratings_batch.append(rating)
            used_pairs.add(pair)
            
            # Накопим изменения лайков
            anecdote_likes_delta[anecdote_id] = anecdote_likes_delta.get(anecdote_id, 0) + value
            
            if len(ratings_batch) >= batch_size:
                session.add_all(ratings_batch)
                session.flush()
                
                for r in ratings_batch:
                    inform = InformSys(
                        source_table="rating",
                        original_id=r.id,
                        author_or_user_id=r.user_id,
                        anecdote_id=r.anecdote_id,
                        value=r.value
                    )
                    ratings_inform_batch.append(inform)
                
                session.add_all(ratings_inform_batch)
                session.commit()
                
                ratings_count += len(ratings_batch)
                pbar.update(len(ratings_batch))
                
                ratings_batch = []
                ratings_inform_batch = []
        
        # Остаток оценок
        if ratings_batch:
            session.add_all(ratings_batch)
            session.flush()
            for r in ratings_batch:
                inform = InformSys(
                    source_table="rating",
                    original_id=r.id,
                    author_or_user_id=r.user_id,
                    anecdote_id=r.anecdote_id,
                    value=r.value
                )
                ratings_inform_batch.append(inform)
            session.add_all(ratings_inform_batch)
            session.commit()
            ratings_count += len(ratings_batch)
            pbar.update(len(ratings_batch))
        pbar.close()
        
        # Теперь обновляем likes_count в анекдотах
        print("Обновление лайков анекдотов...")
        for anecdote_id, delta in tqdm(anecdote_likes_delta.items(), desc="Обновление лайков"):
            # Получаем анекдот из БД
            anecdote = session.get(Anecdote, anecdote_id)
            if anecdote:
                anecdote.likes_count += delta
                session.add(anecdote)
                
                # Обновляем inform_sys для этого анекдота
                inform = session.exec(
                    select(InformSys).where(
                        InformSys.source_table == "anecdote",
                        InformSys.original_id == anecdote_id
                    )
                ).first()
                if inform:
                    inform.likes_count = anecdote.likes_count
                    session.add(inform)
        
        session.commit()
        
        # Генерация избранного (уникальность тоже важна, но можно пересекаться с оценками)
        favorites_batch = []
        favorites_inform_batch = []
        favorites_count = 0
        
        pbar = tqdm(total=num_favorites, desc="Генерация избранного")
        while favorites_count < num_favorites:
            user_id = random.choice(user_ids)
            anecdote_id = random.choice(anecdote_ids)
            pair = (user_id, anecdote_id)
            if pair in used_pairs:
                continue  # избегаем дубликатов среди всех взаимодействий
                # можно разрешить и оценку и избранное, но для простоты запретим дубликаты вообще.
            
            favorite = Favorite(
                user_id=user_id,
                anecdote_id=anecdote_id
            )
            favorites_batch.append(favorite)
            used_pairs.add(pair)
            
            if len(favorites_batch) >= batch_size:
                session.add_all(favorites_batch)
                session.flush()
                
                for f in favorites_batch:
                    inform = InformSys(
                        source_table="favorite",
                        original_id=f.id,
                        author_or_user_id=f.user_id,
                        anecdote_id=f.anecdote_id
                    )
                    favorites_inform_batch.append(inform)
                
                session.add_all(favorites_inform_batch)
                session.commit()
                
                favorites_count += len(favorites_batch)
                pbar.update(len(favorites_batch))
                
                favorites_batch = []
                favorites_inform_batch = []
        
        if favorites_batch:
            session.add_all(favorites_batch)
            session.flush()
            for f in favorites_batch:
                inform = InformSys(
                    source_table="favorite",
                    original_id=f.id,
                    author_or_user_id=f.user_id,
                    anecdote_id=f.anecdote_id
                )
                favorites_inform_batch.append(inform)
            session.add_all(favorites_inform_batch)
            session.commit()
            favorites_count += len(favorites_batch)
            pbar.update(len(favorites_batch))
        pbar.close()
        
        return ratings_count, favorites_count

    def generate_dataset(self, num_users=5000, num_anecdotes=50000, 
                         num_ratings=800000, num_favorites=200000, batch_size=5000):
        """
        Основной метод генерации датасета.
        
        Args:
            num_users: количество пользователей
            num_anecdotes: количество анекдотов
            num_ratings: количество оценок
            num_favorites: количество добавлений в избранное
            batch_size: размер пачки для вставки
        """
        with Session(engine) as session:
            print("Очищаем существующие данные...")
            session.execute(InformSys.__table__.delete())
            session.execute(Rating.__table__.delete())
            session.execute(Favorite.__table__.delete())
            session.execute(Anecdote.__table__.delete())
            session.execute(User.__table__.delete())
            session.commit()
            
            print(f"Генерируем {num_users} пользователей...")
            user_ids = self.generate_users_batch(session, num_users, batch_size)
            
            print(f"Генерируем {num_anecdotes} анекдотов...")
            anecdote_ids = self.generate_anecdotes_batch(session, user_ids, num_anecdotes, batch_size)
            
            print(f"Генерируем {num_ratings} оценок и {num_favorites} избранных...")
            ratings_created, fav_created = self.generate_interactions_batch(
                session, user_ids, anecdote_ids, num_ratings, num_favorites, batch_size
            )
            
            # Итоговая статистика
            print("\n" + "="*50)
            print("ГЕНЕРАЦИЯ ДАННЫХ ЗАВЕРШЕНА")
            print("="*50)
            print(f"Пользователей: {len(user_ids)}")
            print(f"Анекдотов: {len(anecdote_ids)}")
            print(f"Оценок: {ratings_created}")
            print(f"Избранного: {fav_created}")
            print(f"Всего взаимодействий: {ratings_created + fav_created}")
            print("="*50)

def export_to_csv():
    """Экспорт данных в CSV для отчета"""
    with Session(engine) as session:
        # Создаём папку export
        os.makedirs("export", exist_ok=True)
        
        # Экспорт пользователей
        users = session.exec(select(User)).all()
        users_data = [{"id": u.id, "email": u.email, "username": u.username} for u in users]
        pd.DataFrame(users_data).to_csv("export/users.csv", index=False, encoding='utf-8')
        
        # Экспорт анекдотов
        anecdotes = session.exec(select(Anecdote)).all()
        anecdotes_data = [{
            "id": a.id, 
            "content": a.content, 
            "author_id": a.author_id,
            "publication_date": a.publication_date,
            "likes_count": a.likes_count
        } for a in anecdotes]
        pd.DataFrame(anecdotes_data).to_csv("export/anecdotes.csv", index=False, encoding='utf-8')
        
        # Экспорт оценок
        ratings = session.exec(select(Rating)).all()
        ratings_data = [{
            "id": r.id,
            "user_id": r.user_id,
            "anecdote_id": r.anecdote_id,
            "value": r.value
        } for r in ratings]
        pd.DataFrame(ratings_data).to_csv("export/ratings.csv", index=False, encoding='utf-8')
        
        # Экспорт избранного
        favorites = session.exec(select(Favorite)).all()
        favorites_data = [{
            "id": f.id,
            "user_id": f.user_id,
            "anecdote_id": f.anecdote_id
        } for f in favorites]
        pd.DataFrame(favorites_data).to_csv("export/favorites.csv", index=False, encoding='utf-8')
        
        # Экспорт денормализованной таблицы (можно только часть для отчета, но экспортируем все)
        inform_sys = session.exec(select(InformSys)).all()
        # Для больших данных экспорт в CSV может быть объёмным, ограничим первые 10000 для отчета?
        # Но в задании, вероятно, нужно приложить данные. Оставим полный экспорт, но предупредим.
        print("Экспорт inform_sys может занять время...")
        inform_data = [{
            "source_table": i.source_table,
            "original_id": i.original_id,
            "content": i.content,
            "author_or_user_id": i.author_or_user_id,
            "publication_date": i.publication_date,
            "likes_count": i.likes_count,
            "anecdote_id": i.anecdote_id,
            "value": i.value,
            "email": i.email,
            "username": i.username
        } for i in inform_sys]
        df_inform = pd.DataFrame(inform_data)
        df_inform.to_csv("export/inform_sys.csv", index=False, encoding='utf-8')
        
        print("Данные экспортированы в папку export/")

if __name__ == "__main__":
    # Параметры для генерации ~1 млн записей
    generator = TestDataGenerator()
    generator.generate_dataset(
        num_users=5000,
        num_anecdotes=50000,
        num_ratings=800000,
        num_favorites=200000,
        batch_size=5000
    )
    
    export_to_csv()
