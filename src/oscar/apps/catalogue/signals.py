import django.dispatch

product_viewed = django.dispatch.Signal(
    providing_args=["product", "user", "request", "response"])
product_updated = django.dispatch.Signal(
    providing_args=["product", "user", "request", "response"])
