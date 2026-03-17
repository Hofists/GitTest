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
        self.anecdote_templates = [
            "Идет {} по {} и видит {}. {} говорит: '{}'",
            "Встречаются {} и {}. Первый спрашивает: '{}?', второй отвечает: '{}'",
            "Приходит {} к {} и просит: '{}'. {} отвечает: '{}'",
            "Стоит {} на {}. Вдруг подходит {} и говорит: '{}'",
            "Почему {} не может {}? Потому что {}!",
            "{} заходит в {} и видит {}, который {}: '{}'",
            "Сколько {} нужно, чтобы {}? Ни одного, потому что {}",
            "{} вызывает {} и просит: '{}'. {} в ответ: '{}'",
            "Сидит {} за {}, вдруг {} и {}: '{}'",
            "Приходит {} на собеседование. Спрашивают: '{}?'. {} отвечает: '{}'",
            "{} жалуется {}: '{}'. {} советует: '{}'",
            "Разговаривают {} и {} о {}. Вдруг {} говорит: '{}'",
            "Спорят {} и {}: первый говорит '{}', второй возражает: '{}'",
            "{} звонит {} среди ночи: '{}'. {} спросонья: '{}'",
            "Приходит {} из {} и видит, что {} {}: '{}'",
            "Собрались {} в {} и решили {}: '{}'",
            "Просыпается {} утром и понимает, что {}: '{}'",
            "Заходит {} в лифт, а там {} и {}: '{}'",
            "Если {} встретит {} в {}, то {} обязательно {}: '{}'",
            "{} мечтает {}, но {} ему: '{}'",
            "Однажды {} решил стать {}, но {} был против: '{}'",
            "Представьте: {} работает {}, а {} его учит {}: '{}'",
            "Объявление: {} ищет {}, чтобы {}: '{}'",
            "{} не может {} уже {} дней. Всё из-за того, что {}",
            "Секрет {}: чтобы {}, нужно просто {}!",
            "{} попросил {} объяснить {}, но {} сам {} не понимает",
        ]
        
        self.characters = ["программист", "сисадмин", "хакер", "QA-инженер", "тимлид", "джун", "сеньор", "верстальщик", "фронтендер", "бэкендер", "студент", "преподаватель", "директор", "бухгалтер", "менеджер", "кот", "собака", "робот", "нейросеть", "ChatGPT"]
        self.locations = ["работе", "офисе", "удаленке", "коворкинге", "переговорке", "универе", "кухне", "балконе", "ванной", "улице", "парке", "кафе", "интернете", "соцсетях", "Telegram", "матрице"]
        self.objects = ["компьютер", "ноутбук", "роутер", "клавиатуру", "кота", "собаку", "кружку кофе", "баг", "фичу", "легаси-код", "дедлайн", "спринт", "нейросеть", "алгоритм"]
        self.phrases = ["почему не работает интернет", "сломался компьютер", "как взломать Пентагон", "напиши мне нейросеть", "задеплой на прод", "дай денег в долг", "принеси кофе", "я не знаю", "гугли в помощь", "это не баг, это фича", "работает на моей машине"]
        self.actions = ["завис", "упал", "сломался", "сбежал", "написал код", "удалил всё", "сломал прод", "закоммитил", "оптимизировал"]
        self.conditions = ["без кофе", "без интернета", "с похмелья", "на удаленке", "с чашкой чая", "в наушниках"]

    def generate_anecdote_text(self):
        template = random.choice(self.anecdote_templates)
        placeholders = template.count('{}')
        args = []
        for i in range(placeholders):
            choice = random.choice(['char', 'loc', 'obj', 'phrase', 'action', 'cond'])
            if choice == 'char': args.append(random.choice(self.characters))
            elif choice == 'loc': args.append(random.choice(self.locations))
            elif choice == 'obj': args.append(random.choice(self.objects))
            elif choice == 'phrase': args.append(random.choice(self.phrases))
            elif choice == 'action': args.append(random.choice(self.actions))
            elif choice == 'cond': args.append(random.choice(self.conditions))
        return template.format(*args)

    def generate_users_batch(self, session, num_users, batch_size=1000):
        user_ids = []
        users_batch = []
        
        for i in tqdm(range(num_users), desc="Генерация пользователей"):
            user = User(
                email=self.fake.unique.email(), 
                password=self.fake.password(length=10), 
                username=self.fake.unique.user_name()
            )
            users_batch.append(user)
            
        session.add_all(users_batch)
        session.flush() 
        user_ids = [u.id for u in users_batch]
        session.commit()
        # В inform_sys пользователей больше НЕ добавляем!
        return user_ids

    def generate_anecdotes_batch(self, session, author_ids, num_anecdotes, batch_size=1000):
        anecdote_ids = []
        anecdotes_batch = []
        inform_batch = []
        
        for i in tqdm(range(num_anecdotes), desc="Генерация анекдотов"):
            anecdotes_batch.append(Anecdote(
                content=self.generate_anecdote_text(),
                author_id=random.choice(author_ids),
                publication_date=datetime.now() - timedelta(days=random.randint(0, 365)),
                likes_count=0
            ))
            
            if len(anecdotes_batch) >= batch_size:
                session.add_all(anecdotes_batch)
                session.flush()
                
                for a in anecdotes_batch:
                    inform_batch.append(InformSys(
                        source_table="anecdote",
                        original_id=a.id,
                        content=a.content,
                        author_or_user_id=a.author_id,
                        publication_date=a.publication_date,
                        likes_count=a.likes_count
                    ))
                    anecdote_ids.append(a.id)
                
                session.add_all(inform_batch)
                session.commit()
                anecdotes_batch, inform_batch = [], []

        if anecdotes_batch:
            session.add_all(anecdotes_batch)
            session.flush()
            for a in anecdotes_batch:
                inform_batch.append(InformSys(
                    source_table="anecdote",
                    original_id=a.id,
                    content=a.content,
                    author_or_user_id=a.author_id,
                    publication_date=a.publication_date,
                    likes_count=a.likes_count
                ))
                anecdote_ids.append(a.id)
            session.add_all(inform_batch)
            session.commit()
        return anecdote_ids

    def generate_interactions_batch(self, session, user_ids, anecdote_ids, num_ratings, num_favorites, batch_size=5000):
        used_pairs = set()
        ratings_batch = []
        ratings_inform_batch = []
        ratings_count = 0
        anecdote_likes_delta = {}
        
        pbar = tqdm(total=num_ratings, desc="Генерация оценок")
        while ratings_count < num_ratings:
            user_id = random.choice(user_ids)
            anecdote_id = random.choice(anecdote_ids)
            pair = (user_id, anecdote_id)
            if pair in used_pairs: continue
            
            value = random.choice([-1, 1])
            rating = Rating(user_id=user_id, anecdote_id=anecdote_id, value=value)
            ratings_batch.append(rating)
            used_pairs.add(pair)
            anecdote_likes_delta[anecdote_id] = anecdote_likes_delta.get(anecdote_id, 0) + value
            
            if len(ratings_batch) >= batch_size:
                session.add_all(ratings_batch)
                session.flush()
                
                for r in ratings_batch:
                    ratings_inform_batch.append(InformSys(
                        source_table="rating",
                        original_id=r.id,
                        author_or_user_id=r.user_id,
                        anecdote_id=r.anecdote_id,
                        value=r.value
                    ))
                
                session.add_all(ratings_inform_batch)
                session.commit()
                ratings_count += len(ratings_batch)
                pbar.update(len(ratings_batch))
                ratings_batch, ratings_inform_batch = [], []

        if ratings_batch:
            session.add_all(ratings_batch)
            session.flush()
            for r in ratings_batch:
                ratings_inform_batch.append(InformSys(
                    source_table="rating",
                    original_id=r.id,
                    author_or_user_id=r.user_id,
                    anecdote_id=r.anecdote_id,
                    value=r.value
                ))
            session.add_all(ratings_inform_batch)
            session.commit()
            ratings_count += len(ratings_batch)
            pbar.update(len(ratings_batch))
        pbar.close()
        
        print("Обновление лайков анекдотов...")
        for anecdote_id, delta in tqdm(anecdote_likes_delta.items(), desc="Обновление лайков"):
            anecdote = session.get(Anecdote, anecdote_id)
            if anecdote:
                anecdote.likes_count += delta
                session.add(anecdote)
                inform = session.exec(select(InformSys).where(
                    InformSys.source_table == "anecdote", InformSys.original_id == anecdote_id
                )).first()
                if inform:
                    inform.likes_count = anecdote.likes_count
                    session.add(inform)
        session.commit()
        
        favorites_batch = []
        favorites_count = 0
        pbar = tqdm(total=num_favorites, desc="Генерация избранного")
        while favorites_count < num_favorites:
            user_id = random.choice(user_ids)
            anecdote_id = random.choice(anecdote_ids)
            pair = (user_id, anecdote_id)
            if pair in used_pairs: continue 
            
            favorites_batch.append(Favorite(user_id=user_id, anecdote_id=anecdote_id))
            used_pairs.add(pair)
            
            if len(favorites_batch) >= batch_size:
                session.add_all(favorites_batch)
                session.commit() # В inform_sys избранное больше НЕ добавляем!
                favorites_count += len(favorites_batch)
                pbar.update(len(favorites_batch))
                favorites_batch = []

        if favorites_batch:
            session.add_all(favorites_batch)
            session.commit()
            favorites_count += len(favorites_batch)
            pbar.update(len(favorites_batch))
        pbar.close()
        
        return ratings_count, favorites_count

    def generate_dataset(self, num_users=2000, num_anecdotes=20000, num_ratings=180000, num_favorites=48000, batch_size=5000):
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
            
            print("\n" + "="*50)
            print("ГЕНЕРАЦИЯ ДАННЫХ ЗАВЕРШЕНА")
            print("="*50)
            print(f"Пользователей: {len(user_ids)}")
            print(f"Анекдотов: {len(anecdote_ids)}")
            print(f"Оценок: {ratings_created}")
            print(f"Избранного: {fav_created}")
            print(f"Всего сгенерировано записей: {len(user_ids) + len(anecdote_ids) + ratings_created + fav_created}")
            print("="*50)

if __name__ == "__main__":
    generator = TestDataGenerator()
    # Итого: 2000 + 20000 + 180000 + 48000 = 250 000 записей
    generator.generate_dataset(
        num_users=2000,
        num_anecdotes=20000,
        num_ratings=180000,
        num_favorites=48000,
        batch_size=5000
    )
