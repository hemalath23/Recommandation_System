import os
import pandas as pd
from django.conf import settings
from django.shortcuts import render

def recommend_products(request):
    csv_path = os.path.join(settings.BASE_DIR, "D:/recommenderpavani/ratings_Electronics.csv")
    df = pd.read_csv(csv_path, header=None)
    df.columns = ['user_id', 'prod_id', 'rating', 'timestamp']
    df = df.drop('timestamp', axis=1)

    # Ensure 'rating' column contains only numeric values
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

    # Drop rows with invalid ratings
    df = df.dropna(subset=['rating'])

    # Convert 'rating' column to float to ensure all values are numeric
    df['rating'] = df['rating'].astype(float)

    # Your recommendation logic here
    average_rating = df.groupby('prod_id')['rating'].mean()
    count_rating = df.groupby('prod_id')['rating'].count()
    final_rating = pd.DataFrame({'average_rating': average_rating, 'rating_count': count_rating})
    final_rating = final_rating.sort_values(by='average_rating', ascending=False)

    # Assuming you want to recommend the top 5 products with more than 50 ratings
    top_products = final_rating[final_rating['rating_count'] > 50].head(5)
    top_products_list = top_products.reset_index().to_dict('records')

    return render(request, 'recommendations.html', {'products': top_products_list})
