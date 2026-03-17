import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from sqlmodel import Session, select
from models.inform_sys import InformSys
from typing import List

def get_popular_anecdotes(session: Session, limit: int = 5) -> List[InformSys]:
    """Возвращает популярные анекдоты для неавторизованных пользователей."""
    stmt = select(InformSys).where(
        InformSys.source_table == "anecdote"
    ).order_by(InformSys.likes_count.desc()).limit(limit)
    return session.exec(stmt).all()

def get_recommendations_for_user(
    session: Session, 
    user_id: int, 
    limit: int = 5,
    top_k_users: int = 50
) -> List[InformSys]:
    """Коллаборативная фильтрация на основе лайков и дизлайков."""
    # Получаем все оценки из денормализованной таблицы
    stmt = select(InformSys).where(InformSys.source_table == "rating")
    ratings = session.exec(stmt).all()
    
    if not ratings:
        return get_popular_anecdotes(session, limit)
        
    data = []
    for r in ratings:
        if r.author_or_user_id is not None and r.anecdote_id is not None:
            data.append({
                "user_id": int(r.author_or_user_id),
                "anecdote_id": int(r.anecdote_id),
                "value": float(r.value) if r.value is not None else 0.0
            })
            
    df = pd.DataFrame(data)
    if df.empty:
        return get_popular_anecdotes(session, limit)
        
    user_ids = df["user_id"].unique()
    anecdote_ids = df["anecdote_id"].unique()
    
    user_to_idx = {uid: i for i, uid in enumerate(user_ids)}
    anecdote_to_idx = {aid: i for i, aid in enumerate(anecdote_ids)}
    
    # Если у пользователя нет оценок — выдаем популярное
    if user_id not in user_to_idx:
        return get_popular_anecdotes(session, limit)
        
    # Собираем разреженную матрицу оценок
    rows = df["user_id"].map(user_to_idx).values
    cols = df["anecdote_id"].map(anecdote_to_idx).values
    vals = df["value"].values
    
    rating_matrix = csr_matrix((vals, (rows, cols)), shape=(len(user_ids), len(anecdote_ids)))
    
    user_idx = user_to_idx[user_id]
    user_vector = rating_matrix[user_idx]
    
    # Вычисляем косинусное сходство
    similarities = cosine_similarity(user_vector, rating_matrix).flatten()
    similarities[user_idx] = -1.0 # Исключаем самого себя
    
    # Отбираем наиболее похожих пользователей
    top_indices = np.argsort(similarities)[::-1][:top_k_users]
    
    current_user_rated = set(df[df["user_id"] == user_id]["anecdote_id"])
    candidate_scores = {}
    
    for idx in top_indices:
        sim = similarities[idx]
        if sim <= 0:
            continue # Рассматриваем только тех, с кем есть позитивное сходство
            
        similar_user_id = user_ids[idx]
        user_ratings = df[df["user_id"] == similar_user_id]
        
        for _, row in user_ratings.iterrows():
            aid = int(row["anecdote_id"])
            if aid not in current_user_rated:
                # Скоринг: если похожий юзер лайкнул, скор растет; если дизлайкнул - падает.
                contribution = row["value"] * sim
                candidate_scores[aid] = candidate_scores.get(aid, 0.0) + contribution
                
    # Отсеиваем те, что набрали отрицательный или нулевой скор (в целом не понравились похожим)
    sorted_candidates = sorted(
        [(aid, score) for aid, score in candidate_scores.items() if score > 0],
        key=lambda x: x[1], 
        reverse=True
    )
    
    if not sorted_candidates:
        return get_popular_anecdotes(session, limit)
        
    top_anecdote_ids = [aid for aid, score in sorted_candidates[:limit]]
    
    # Вытягиваем из БД полные записи рекомендуемых анекдотов
    stmt = select(InformSys).where(
        InformSys.source_table == "anecdote",
        InformSys.original_id.in_(top_anecdote_ids)
    )
    anecdotes = session.exec(stmt).all()
    
    # Возвращаем в правильном порядке
    order_map = {aid: i for i, aid in enumerate(top_anecdote_ids)}
    anecdotes.sort(key=lambda a: order_map.get(a.original_id, 999))
    
    return anecdotes
