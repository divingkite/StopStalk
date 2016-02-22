from rest_framework import serializers
from stalker_api.models import Person,Contest,Question
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=50)
    email    = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    people   = serializers.PrimaryKeyRelatedField(many=True, queryset=Person.objects.all())

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return User.objects.create(**validated_data)
class PersonSerializer(serializers.Serializer):
    #pk = serializers.IntegerField(read_only=True)
    cc = serializers.CharField(required=False, allow_blank=True, max_length=20)
    cf = serializers.CharField(required=False, allow_blank=True, max_length=20)
    name = serializers.CharField(required=True)
    owner = serializers.CharField(read_only=True)
    
    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Person.objects.create(**validated_data)

class QuestionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    link = serializers.CharField(required = False)
    site = serializers.CharField(max_length=20)
    index = serializers.CharField(required=False,max_length=2)
    person = PersonSerializer()
    contest = None

class ContestSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    contestId = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    site = serializers.CharField(max_length=20)
    question = QuestionSerializer(required=False,many=True)

QuestionSerializer.contest = ContestSerializer()