from rest_framework import serializers
from .models import Professor, Module, ModuleInstance, Rating

class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ['professor_id', 'first_name', 'last_name']

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['module_code', 'name']

class ModuleInstanceSerializer(serializers.ModelSerializer):
    module = ModuleSerializer()
    professors = ProfessorSerializer(many=True)
    
    class Meta:
        model = ModuleInstance
        fields = ['module', 'year', 'semester', 'professors']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['user', 'professor', 'module_instance', 'rating']
