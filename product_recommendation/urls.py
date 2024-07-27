from django.urls import path,include
from . import views

urlpatterns = [
    path('recommendations/', views.recommend_products, name='recommend_products'),
    path('recommendations/<int:user_id>/', views.user_recommendations, name='user_recommendations'),
     path('product_recommendation/', include('product_recommendation.urls')),
]
