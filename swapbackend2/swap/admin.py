from django.contrib import admin
from .models import NewUser,User,courses,require,authtok
# Register your models here.
admin.site.register(User)
admin.site.register(courses)
admin.site.register(require)
admin.site.register(NewUser)
admin.site.register(authtok)