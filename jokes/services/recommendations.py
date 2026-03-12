import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from sqlmodel import Session, select
from models.inform_sys import InformSys
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def get_popular_anecdotes(session: Session, limit: int = 5) -> List[InformSys]:
    """
    Возвращает limit самых популярных анекдотов (по likes_count)
    из денормализованной таблицы (source_table='anecdote').
    """
    stmt = select(InformSys).where(
        InformSys.source_table == "anecdote"
    ).order_by(InformSys.likes_count.desc()).limit(limit)
    return session.exec(stmt).all()


def get_recommendations_for_user(
    session: Session,
    user_id: int,
    limit: int = 5,
    similarity_threshold: float = 0.1,
    top_k_users: int = 20
) -> List[InformSys]:
    """
    Коллаборативная фильтрация (user-based) с использованием данных из inform_sys.
    - Читает все оценки из inform_sys (source_table='rating').
    - Строит матрицу пользователь-анекдот.
    - Находит top_k_users наиболее похожих на текущего.
    - Собирает анекдоты, которые понравились похожим пользователям,
      но не оценены текущим.
    - Возвращает объекты InformSys (анекдоты) для отображения.
    """
    # 1. Загружаем все оценки из inform_sys
    ratings_query = select(InformSys).where(InformSys.source_table == "rating")
    ratings_rows = session.exec(ratings_query).all()

    if not ratings_rows:
        logger.info("Нет данных об оценках, возвращаем популярные")
        return get_popular_anecdotes(session, limit)

    # Преобразуем в DataFrame
    df = pd.DataFrame([
        {
            "user_id": r.author_or_user_id,
            "anecdote_id": r.anecdote_id,
            "value": r.value
        }
        for r in ratings_rows
        if r.author_or_user_id is not None and r.anecdote_id is not None
    ])

    if df.empty:
        return get_popular_anecdotes(session, limit)

    # 2. Построим отображения для индексов
    user_ids = df["user_id"].unique()
    anecdote_ids = df["anecdote_id"].unique()
    user_to_idx = {uid: i for i, uid in enumerate(user_ids)}
    anecdote_to_idx = {aid: i for i, aid in enumerate(anecdote_ids)}

    # 3. Создаём разреженную матрицу оценок
    rows = df["user_id"].map(user_to_idx).values
    cols = df["anecdote_id"].map(anecdote_to_idx).values
    data = df["value"].values
    rating_matrix = csr_matrix(
        (data, (rows, cols)),
        shape=(len(user_ids), len(anecdote_ids))
    )

    # 4. Проверяем, есть ли текущий пользователь
    if user_id not in user_to_idx:
        logger.info("У пользователя %d нет оценок", user_id)
        return get_popular_anecdotes(session, limit)

    user_idx = user_to_idx[user_id]
    user_vector = rating_matrix[user_idx]

    # 5. Вычисляем косинусное сходство со всеми пользователями
    similarities = cosine_similarity(user_vector, rating_matrix).flatten()
    similarities[user_idx] = -1  # исключаем себя

    # 6. Выбираем top_k_users с порогом
    top_indices = np.argsort(similarities)[::-1][:top_k_users]
    top_scores = similarities[top_indices]

    mask = top_scores >= similarity_threshold
    top_indices = top_indices[mask]
    top_scores = top_scores[mask]

    if len(top_indices) == 0:
        logger.info("Не найдено похожих пользователей")
        return get_popular_anecdotes(session, limit)

    # 7. Собираем кандидатов – анекдоты, которые понравились похожим
    current_user_rated = set(df[df["user_id"] == user_id]["anecdote_id"])
    candidate_scores: Dict[int, float] = {}

    for idx, score in zip(top_indices, top_scores):
        similar_user_id = user_ids[idx]
        # Берём только положительные оценки похожего пользователя
        liked = df[(df["user_id"] == similar_user_id) & (df["value"] > 0)]
        for _, row in liked.iterrows():
            aid = row["anecdote_id"]
            if aid not in current_user_rated:
                candidate_scores[aid] = candidate_scores.get(aid, 0) + score

    if not candidate_scores:
        return get_popular_anecdotes(session, limit)

    # 8. Сортируем кандидатов по убыванию веса
    sorted_candidates = sorted(
        candidate_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:limit]

    anecdote_ids = [aid for aid, _ in sorted_candidates]

    # 9. Загружаем полные объекты анекдотов из inform_sys
    stmt = select(InformSys).where(
        InformSys.source_table == "anecdote",
        InformSys.original_id.in_(anecdote_ids)
    )
    anecdotes = session.exec(stmt).all()

    # Восстанавливаем порядок сортировки
    order_map = {aid: i for i, aid in enumerate(anecdote_ids)}
    anecdotes.sort(key=lambda a: order_map[a.original_id])

    return anecdotes
