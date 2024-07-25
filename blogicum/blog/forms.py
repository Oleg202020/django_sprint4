from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма для добавления постов"""

    class Meta:
        model = Post
        fields = '__all__'
        exclude = (
            'author',
        )
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'}
            ),
        }


class CommentForm(forms.ModelForm):
    """Форма для добавления комментариев"""

    class Meta:
        model = Comment
        fields = ('text',)
