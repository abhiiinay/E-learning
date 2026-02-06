from django.contrib import admin
from instructorApp.models import User,Category,Course,Module,Lesson,Order

# Register your models here.
admin.site.register(User)
admin.site.register(Category)

class CourseModel(admin.ModelAdmin):
    exclude=['owner']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner=request.user
        return super().save_model(request, obj, form, change)

admin.site.register(Course,CourseModel)    

class ModuleModel(admin.ModelAdmin):
    exclude=['order']
    


class LessonModel(admin.ModelAdmin):
    exclude=['order']
admin.site.register(Module,ModuleModel)
admin.site.register(Lesson,LessonModel)
admin.site.register(Order)
