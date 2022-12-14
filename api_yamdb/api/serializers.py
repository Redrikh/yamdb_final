from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""

    class Meta:
        fields = (
            'username',
            'bio',
            'email',
            'first_name',
            'last_name',
            'role',
        )
        model = User

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Создать пользователя me нельзя'
            )
        return value


class UserPatchSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя с ограничением изменения роли."""

    class Meta:
        fields = (
            'username',
            'bio',
            'email',
            'first_name',
            'last_name',
            'role',
        )
        read_only_fields = ['role']
        model = User


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для заголовка."""

    rating = serializers.IntegerField(
        source='reviews__score__avg',
        read_only=True,
    )
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'category',
            'genre',
            'description',
        )
        model = Title

    def get_rating(self, title):
        rating = title.reviews.aggregate(Avg('score')).get('score__avg')
        if not rating:
            return None
        return round(rating, 1)


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания заголовка."""

    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug',
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'category', 'genre', 'description')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для ревью."""

    title = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        fields = '__all__'
        model = Review

    def validate(self, data):
        request = self.context.get('request')
        queryset = self.context.get('view').get_queryset()
        if request.method == 'PATCH':
            return data
        if queryset.filter(author=request.user).exists():
            raise serializers.ValidationError(
                'Нельзя оставлять больше 1 отзыва на произведение'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
