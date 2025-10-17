from django import template

register = template.Library()


@register.simple_tag
def get_hub_rate(hub_rates, hub_id, weight_id):
    """Get hub rate from the hub_rates dictionary using hub_id and weight_id."""
    try:
        return hub_rates.get(str(hub_id), {}).get(str(weight_id), '-')
    except (AttributeError, ValueError):
        return '-'


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
