from django.contrib.auth.models import User


class BudgetTestCaseMixin(object):
    """
    Helpers for budgeting tests
    """
    def get_or_create_user_with_budget(
            self, email=None, budget=None):
        email = email or 'test@test.com'
        user, _ = User.objects.get_or_create(
            username=email,
            email=email,
            password='#')
        user.total_budget.amount = budget or 1000
        user.total_budget.save(update_fields=['amount', ])
        return user