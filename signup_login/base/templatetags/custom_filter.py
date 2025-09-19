from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Retrieves an item from a dictionary using a variable key.
    """
    return dictionary.get(key)