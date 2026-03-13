import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from sqlmodel import Session, select
from models.inform_sys import InformSys
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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
    similarity_threshold: float = 0.0,
    top_k_users: int = 50
) -> List[InformSys]:
    """
    Коллаборативная фильтрация (user-based) с использованием inform_sys.
    Учитывает все оценки похожих пользователей (положительные и отрицательные)
    с весом value * similarity.
    """
    logger.info(f"Запрос рекомендаций для пользователя {user_id}")

    # 1. Загружаем все оценки из inform_sys
    ratings_query = select(InformSys).where(InformSys.source_table == "rating")
    ratings_rows = session.exec(ratings_query).all()
    logger.info(f"Загружено оценок: {len(ratings_rows)}")

    if not ratings_rows:
        logger.warning("Нет данных об оценках, возвращаем популярные")
        return get_popular_anecdotes(session, limit)

    # 2. Преобразуем в DataFrame, отбрасывая записи с пустыми идентификаторами
    data = []
    for r in ratings_rows:
        if r.author_or_user_id is not None and r.anecdote_id is not None:
            data.append({
                "user_id": int(r.author_or_user_id),
                "anecdote_id": int(r.anecdote_id),
                "value": r.value
            })
    df = pd.DataFrame(data)
    logger.info(f"DataFrame после фильтрации: {df.shape[0]} строк")

    if df.empty:
        return get_popular_anecdotes(session, limit)

    # 3. Построение отображений для индексов
    user_ids = df["user_id"].unique()
    anecdote_ids = df["anecdote_id"].unique()
    user_to_idx = {uid: i for i, uid in enumerate(user_ids)}
    anecdote_to_idx = {aid: i for i, aid in enumerate(anecdote_ids)}

    # 4. Создание разреженной матрицы оценок
    rows = df["user_id"].map(user_to_idx).values
    cols = df["anecdote_id"].map(anecdote_to_idx).values
    rating_matrix = csr_matrix(
        (df["value"].values, (rows, cols)),
        shape=(len(user_ids), len(anecdote_ids))
    )

    # 5. Проверка наличия текущего пользователя
    if user_id not in user_to_idx:
        logger.info(f"Пользователь {user_id} не найден в матрице (нет оценок)")
        return get_popular_anecdotes(session, limit)

    user_idx = user_to_idx[user_id]
    user_vector = rating_matrix[user_idx]

    # 6. Вычисление косинусного сходства со всеми пользователями
    similarities = cosine_similarity(user_vector, rating_matrix).flatten()
    similarities[user_idx] = -1  # исключаем себя

    # 7. Выбор top_k_users самых похожих
    top_indices = np.argsort(similarities)[::-1][:top_k_users]
    top_scores = similarities[top_indices]

    # 8. Фильтр по порогу сходства
    mask = top_scores >= similarity_threshold
    top_indices = top_indices[mask]
    top_scores = top_scores[mask]

    logger.info(f"Найдено похожих пользователей после фильтра: {len(top_indices)}")
    if len(top_indices) == 0:
        logger.info("Не найдено похожих пользователей, возвращаем популярные")
        return get_popular_anecdotes(session, limit)

    # 9. Сбор кандидатов – анекдоты, оценённые похожими пользователями
    current_user_rated = set(df[df["user_id"] == user_id]["anecdote_id"])
    candidate_scores: Dict[int, float] = {}

    for idx, score in zip(top_indices, top_scores):
        similar_user_id = user_ids[idx]
        user_ratings = df[df["user_id"] == similar_user_id]
        for _, row in user_ratings.iterrows():
            aid = row["anecdote_id"]
            if aid not in current_user_rated:
                candidate_scores[aid] = candidate_scores.get(aid, 0) + row["value"] * score

    logger.info(f"Найдено кандидатов: {len(candidate_scores)}")
    if not candidate_scores:
        return get_popular_anecdotes(session, limit)

    # 10. Сортировка кандидатов по убыванию веса
    sorted_candidates = sorted(
        candidate_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:limit]

    anecdote_ids = [aid for aid, _ in sorted_candidates]
    logger.info(f"Итоговые ID анекдотов: {anecdote_ids}")

    # 11. Загрузка полных объектов анекдотов из inform_sys
    stmt = select(InformSys).where(
        InformSys.source_table == "anecdote",
        InformSys.original_id.in_(anecdote_ids)
    )
    anecdotes = session.exec(stmt).all()

    # Восстановление порядка сортировки
    order_map = {aid: i for i, aid in enumerate(anecdote_ids)}
    anecdotes.sort(key=lambda a: order_map[a.original_id])

    return anecdotes
