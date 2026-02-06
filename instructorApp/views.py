from django.shortcuts import render
from instructorApp.forms import InstructorCreateForm
from instructorApp.models import User
from django.views import View
from django.http import HttpResponse

# Create your views here.
class InstructorCreateView(View):
    def get(self,request):
        form=InstructorCreateForm()
        return render(request,'instructor_reg.html',{'form':form})
    
    def post(self,request):
        form_instance=InstructorCreateForm(request.POST)
        print(form_instance)
        if form_instance.is_valid():
            form_instance.instance.is_superuser=True
            form_instance.instance.is_staff=True
            form_instance.instance.role="instructor"
            form_instance.save()
            return HttpResponse("poli moneeeeee")