import os
import pandas as pd
import numpy as np
from django.conf import settings
from django.shortcuts import render
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds

# Load and prepare the data
def load_data():
    csv_path = os.path.join(settings.BASE_DIR, "D:/recommenderpavani/ratings_Electronics.csv")
    df = pd.read_csv(csv_path, header=None)
    df.columns = ['user_id', 'prod_id', 'rating', 'timestamp']
    df = df.drop('timestamp', axis=1)

    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df.dropna(subset=['rating'])
    df['rating'] = df['rating'].astype(float)

    counts = df['user_id'].value_counts()
    df_final = df[df['user_id'].isin(counts[counts >= 50].index)]
    final_ratings_matrix = df_final.pivot(index='user_id', columns='prod_id', values='rating').fillna(0)

    return df_final, final_ratings_matrix

def recommend_products(request):
    # Load and prepare the data
    df_final, final_ratings_matrix = load_data()

    # Convert to sparse matrix
    final_ratings_sparse = csr_matrix(final_ratings_matrix.values)
    U, s, Vt = svds(final_ratings_sparse, k=50)
    sigma = np.diag(s)

    # Predict ratings
    all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt)
    preds_df = pd.DataFrame(all_user_predicted_ratings, columns=final_ratings_matrix.columns)
    preds_matrix = csr_matrix(preds_df.values)

    return render(request, 'product_recommendation/product_recommendation.html')

def recommend_items(user_index, interactions_matrix, preds_matrix, num_recommendations):
    user_ratings = interactions_matrix[user_index, :].toarray().reshape(-1)
    user_predictions = preds_matrix[user_index, :].toarray().reshape(-1)
    temp = pd.DataFrame({'user_ratings': user_ratings, 'user_predictions': user_predictions})
    temp['Recommended Products'] = np.arange(len(user_ratings))
    temp = temp.set_index('Recommended Products')
    temp = temp.loc[temp.user_ratings == 0]
    temp = temp.sort_values('user_predictions', ascending=False)
    return temp['user_predictions'].head(num_recommendations)

def user_recommendations(request, user_id):
    # Load and prepare the data
    df_final, final_ratings_matrix = load_data()

    final_ratings_sparse = csr_matrix(final_ratings_matrix.values)
    U, s, Vt = svds(final_ratings_sparse, k=50)
    sigma = np.diag(s)
    all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt)
    preds_df = pd.DataFrame(all_user_predicted_ratings, columns=final_ratings_matrix.columns)
    preds_matrix = csr_matrix(preds_df.values)

    user_index = final_ratings_matrix.index.get_loc(user_id)
    recommendations = recommend_items(user_index, final_ratings_sparse, preds_matrix, 5).index.tolist()
    return render(request, 'product_recommendation/user_recommendations_list.html', {'recommendations': recommendations})
