from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key) if dictionary else None

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def divide(value, arg):
    if arg:
        return value / arg
    return 0

@register.simple_tag
def course_progress(user, course):
    try:
        enrollment = Enrollment.objects.get(user=user, course=course)
        return enrollment.progress
    except Enrollment.DoesNotExist:
        return 0

@register.inclusion_tag('courses/partials/course_card.html')
def render_course_card(course, user=None):
    return {
        'course': course,
        'user': user,
        'is_favorite': FavoriteService.is_favorite(user, course) if user and user.is_authenticated else False
    }