from django.db.models import Count
from django.utils import timezone

from .models import Post


def get_general_queryset_posts(
        manager=Post.objects,
        filter=True,
        annotation=True
):
    """Функция производит сортировку данных по условиям фильтра"""
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
