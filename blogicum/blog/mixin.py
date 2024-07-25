from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect

from .forms import CommentForm, PostForm
from .models import Comment, Post


class PostMixin:
    """Основные настройки класса Post"""

    model = Post
    form_class = PostForm
    template_name = 'blog/index.html'
    pk_url_kwarg = 'post_id'


class EditContentMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)


class CommentMixin:
    """Основные настройки класса Comment"""

    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'


class CommentUpdateDeleteMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            post_id=self.kwargs['post_id'],
        )
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)
