from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
)

from .forms import CommentForm, PostForm
from .models import Category, Post, Comment, User


def get_filter_post(manager=Post.objects, filter=True, annotation=True):
    queryset = manager.select_related(
        'author',
        'location',
        'category'
    )
    if filter:
        queryset = queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
    if annotation:
        queryset = queryset.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    return queryset


class EditContentMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/index.html'
    pk_url_kwarg = 'post_id'


class IndexListView(PostMixin, ListView):
    paginate_by = settings.PUBLIC_ON_THE_PAGE

    def get_queryset(self):
        return get_filter_post()


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    paginate_by = settings.PUBLIC_ON_THE_PAGE
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostDetailView(PostMixin, DetailView):
    template_name = 'blog/detail.html'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'author',
            'location',
            'category',
        )

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.author != self.request.user and (
                post.is_published is False
                or post.category.is_published is False
                or post.pub_date > timezone.now()
        ):
            raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related(
            'author'
        )
        return context


class PostUpdateView(EditContentMixin, PostMixin, UpdateView):
    paginate_by = settings.PUBLIC_ON_THE_PAGE
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(EditContentMixin, PostMixin, DeleteView):
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class CategoryListView(ListView):
    model = Category
    paginate_by = settings.PUBLIC_ON_THE_PAGE
    template_name = 'blog/category.html'

    def category(self):
        context = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category()
        return context

    def get_queryset(self):
        category = self.category()
        return (
            get_filter_post(
            ).filter(category=category)
        )


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            get_filter_post(),
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)


class CommentUpdateDeleteMixin(LoginRequiredMixin):
    """Надеюсь я правильно понял задачу по редактированию и удалению"""

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateView(CommentUpdateDeleteMixin, CommentMixin, UpdateView):
    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDeleteView(CommentUpdateDeleteMixin, CommentMixin, DeleteView):

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class ProfileListView(ListView):
    paginate_by = settings.PUBLIC_ON_THE_PAGE
    template_name = 'blog/profile.html'

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        if self.request.user != self.author:
            queryset = get_filter_post(
                manager=self.author.posts,
                filter=True,
                annotation=True,
            )
        else:
            queryset = get_filter_post(
                manager=self.author.posts,
                filter=False,
                annotation=True
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_object_or_404(User, username=self.kwargs.get('username'))
        context['profile'] = author
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    fields = ('username', 'first_name', 'last_name', 'email')

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class ProfileCreateView(CreateView):
    form_class = UserCreationForm,
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')
