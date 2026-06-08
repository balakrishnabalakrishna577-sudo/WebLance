from django.apps import AppConfig


class HomeConfig(AppConfig):
    name = 'home'

    def ready(self):
        from django.contrib.auth.signals import user_logged_in

        def set_cookie_flag(sender, request, user, **kwargs):
            request.session['show_cookie_banner'] = True

        user_logged_in.connect(set_cookie_flag)
