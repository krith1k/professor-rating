from django.urls import path
from .views import (
    RegisterUser,
    ModuleInstanceList,
    ProfessorRatingView,
    ProfessorModuleAverageView,
    RateProfessor,
    ProfileView
)

urlpatterns = [
    # Option 1: Register user
    path('api/register/', RegisterUser.as_view(), name='register'),

    # Option 1: List module instances
    path('api/modules/', ModuleInstanceList.as_view(), name='module-instance-list'),
    
    # Option 2: View overall professor ratings
    path('api/professors/ratings/', ProfessorRatingView.as_view(), name='professor-rating'),
    
    # Option 3: Average rating for a specific professor in a specific module
    path('api/professors/<str:professor_id>/modules/<str:module_code>/average/', ProfessorModuleAverageView.as_view(), name='professor-module-average'),
    
    # Option 4: Rate a professor
    path('api/rate/', RateProfessor.as_view(), name='rate-professor'),

    #
    path('api/profile/', ProfileView.as_view(), name='profile')
]
