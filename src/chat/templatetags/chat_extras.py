from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def room_display_name(room, user):
    return room.get_display_name(user)