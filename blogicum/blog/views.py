from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
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
from .function import get_general_queryset_posts
from .mixin import (
    PostMixin,
    EditContentMixin,
    CommentMixin,
    CommentUpdateDeleteMixin
)
from .models import Category, Post, User


class IndexListView(PostMixin, ListView):
    paginate_by = settings.PUBLIC_ON_THE_PAGE

    def get_queryset(self):
        return get_general_queryset_posts()


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
        queryset = get_general_queryset_posts(
            manager=Post.objects,
            filter=False,
            annotation=False)
        return queryset

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
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category()
        return context

    def get_queryset(self):
        category = self.category()
        return get_general_queryset_posts(manager=category.posts)


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            get_general_queryset_posts(),
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)


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

    def get_autor(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self):
        author = self.get_autor()
        filter_ = True
        if self.request.user == author:
            filter_ = False
        queryset = get_general_queryset_posts(
            manager=author.posts,
            filter=filter_,
            annotation=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.get_autor()
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
