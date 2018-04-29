import environ
root = environ.Path(__file__) - 3 # three folder back
env = environ.Env(DEBUG=(bool, False),)
environ.Env.read_env()

DATABASES = {
    'default': env.db(
        'DATABASE_URL', 
        default='sqlite:////tmp/expenses-tmp-sqlite.db')
}