from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import ModuleInstance
from .serializers import ModuleInstanceSerializer
from django.db.models import Avg
from .models import Professor, Module, Rating

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        return Response({"username": request.user.username})

class RegisterUser(APIView):
    def post(self, request, format=None):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({'error': 'username, email, and password are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # create_user() hashes the password automatically.
        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)

class ModuleInstanceList(APIView):
    def get(self, request, format=None):
        instances = ModuleInstance.objects.all()
        serializer = ModuleInstanceSerializer(instances, many=True)
        return Response(serializer.data)

class ProfessorRatingView(APIView):
    def get(self, request, format=None):
        professors = Professor.objects.all()
        data = []
        for prof in professors:
            avg_rating = Rating.objects.filter(professor=prof).aggregate(Avg('rating'))['rating__avg']
            # Round the average and convert rating to stars (e.g., '***')
            stars = '*' * int(round(avg_rating)) if avg_rating is not None else "No ratings"
            data.append({
                "professor_id": prof.professor_id,
                "name": f"{prof.first_name} {prof.last_name}",
                "rating": stars,
            })
        return Response(data)

class ProfessorModuleAverageView(APIView):
    def get(self, request, professor_id, module_code, format=None):
        # Filter relevant ratings
        ratings = Rating.objects.filter(
            professor__professor_id=professor_id,
            module_instance__module__module_code=module_code
        )
        if not ratings.exists():
            return HttpResponse("No ratings found for this professor in this module.", status=404)
        
        # Compute average rating and convert to stars
        avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        stars = '*' * int(round(avg_rating))

        # Retrieve the professor object to get first_name and last_name
        try:
            professor = Professor.objects.get(professor_id=professor_id)
            professor_full_name = f"{professor.first_name} {professor.last_name}"
        except Professor.DoesNotExist:
            return HttpResponse("Professor not found.", status=404)

        # Retrieve the module object to get module name
        try:
            module = Module.objects.get(module_code=module_code)
            module_full_name = module.name
        except Module.DoesNotExist:
            return HttpResponse("Module not found.", status=404)

        # Constructing the final plain text message
        message = (
            f"The rating of Professor {professor_full_name} ({professor_id}) "
            f"in module {module_full_name} ({module_code}) is {stars}"
        )

        # Return the message as plain text
        return HttpResponse(message, content_type="text/plain", status=200)

class RateProfessor(APIView):
    def post(self, request, format=None):
        data = request.data
        professor_id = data.get('professor_id')
        module_code = data.get('module_code')
        year = data.get('year')
        semester = data.get('semester')
        rating_value = data.get('rating')
        
        # Basic validation
        if not all([professor_id, module_code, year, semester, rating_value]):
            return Response({"error": "Missing fields in request data."}, status=400)
        
        try:
            year = int(year)
            semester = int(semester)
            rating_value = int(rating_value)
        except ValueError:
            return Response({"error": "Year, semester, and rating must be integers."}, status=400)
        
        if rating_value < 1 or rating_value > 5:
            return Response({"error": "Rating must be between 1 and 5."}, status=400)
        
        # Retrieve professor
        try:
            professor = Professor.objects.get(professor_id=professor_id)
        except Professor.DoesNotExist:
            return Response({"error": "Professor not found."}, status=404)
        
        # Retrieve module instance
        try:
            module_instance = ModuleInstance.objects.get(
                module__module_code=module_code,
                year=year,
                semester=semester
            )
        except ModuleInstance.DoesNotExist:
            return Response({"error": "Module instance not found."}, status=404)
        
        # Ensure the user is authenticated
        user = request.user if request.user.is_authenticated else None
        if user is None:
            return Response({"error": "Authentication required to rate."}, status=401)
        
        # Prevent duplicate ratings by the same user for this professor in the same module instance
        if Rating.objects.filter(user=user, professor=professor, module_instance=module_instance).exists():
            return Response({"error": "You have already rated this professor in this module instance."}, status=400)
        
        rating_obj = Rating.objects.create(
            user=user,
            professor=professor,
            module_instance=module_instance,
            rating=rating_value
        )
        
        from .serializers import RatingSerializer
        serializer = RatingSerializer(rating_obj)
        return Response(serializer.data, status=201)