from django.shortcuts import render,redirect
from django.views import View
from instructorApp.models import Course,Cart,Order,Module,Lesson
from instructorApp.forms import InstructorCreateForm
from django.contrib.auth import authenticate,login,logout
from django.utils.decorators import method_decorator
from django.db.models import Sum
import razorpay

RZP_KEY_ID="rzp_test_RjSOcWIIw5Nlrj"
RZP_KEY_SECRET="kOoBf1vfX765nbHtpZD6hR4p"


# Create your views here.
class StudentHome(View):
    def get(self,request):
        courses=Course.objects.all()
        purchased_course=Order.objects.filter(user_instance=request.user).values_list("course_instance",flat=True)
        print(purchased_course)
        return render(request,'index.html',{'courses':courses,'purchased_course':purchased_course})
    
class CourseDetailView(View):
    def get(self,request,**kwargs):
        courses=Course.objects.get(id=kwargs.get("id"))
        return render(request,"coursedetail.html",{"course":courses})
    
class StudentRegister(View):
    def get(self,request):
        form=InstructorCreateForm()
        return render(request,"student.html",{'form':form})
    
    def post(self,request):
        form_instance=InstructorCreateForm(request.POST)
        if form_instance.is_valid():
            form_instance.save()
            return redirect("stud_log")
    
class StudentLogin(View):
    def get(self,request):
        form=InstructorCreateForm()
        return render(request,'student.html',{'form':form})
    def post(self,request):
        uname=request.POST.get("username")
        psw=request.POST.get("password")
        res=authenticate(request,username=uname,password=psw)
        if res:
            login(request,res)
            if res.role=="student":
                return redirect("student_check")
        else:
                return redirect("stud_log")

def login_required(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            return redirect("stud_log")
        else:
            return fn(request,*args,**kwargs)
    return wrapper

@method_decorator(login_required,name="dispatch")
class AddToCart(View):
    def get(self,request,*args,**kwargs):
        user=request.user
        course=Course.objects.get(id=kwargs.get("id"))
        Cart.objects.get_or_create(user_instance=user,course_instance=course)
        return redirect("cart_view")
    
class CartView(View):
    def get(self,request):
        carts=request.user.user_cart.all()
        # carts=Cart.objects.filter(user=request.user)
        total=sum([cart.course_instance.price for cart in carts])
        return render(request,"cartview.html",{'carts':carts,'total':total})
    
class CartDelete(View):
    def get(self,request,*args,**kwargs):
        Cart.objects.get(id=kwargs.get("id")).delete()
        return redirect("cart_view")

     

class CheckoutView(View):
    def get(self,request,*args,**kwargs):
        cart_list=Cart.objects.filter(user_instance=request.user)
        user=request.user
        total=cart_list.aggregate(total=Sum("course_instance__price")).get("total")
        # total=sum([cart.course_instance.price for cart in cart_list])
        order_instance=Order.objects.create(user_instance=user,total=total)
        if cart_list:
            for cart in cart_list:
                order_instance.course_instance.add(cart.course_instance)
                cart.delete()

            client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))

            DATA = {
            "amount": float(total*100),
            "currency": "INR",
            "receipt": "receipt#1",
            "notes": {
                "key1": "value3",
                "key2": "value2"
                }
            }
            payment=client.order.create(data=DATA)
            print(payment)
            order_id=payment.get("id")
            order_instance.rzp_order_id=order_id
            order_instance.save()
            context={
                "total":float(total*100),
                "key_id":RZP_KEY_ID,
                "order_id":order_id
            }
            return render(request,'payment.html',context)

from django.views.decorators.csrf import csrf_exempt
@method_decorator(csrf_exempt,name="dispatch")
class PaymentConfirm(View):
    def post(self,request,*args,**kwargs):
        client=razorpay.Client(auth=(RZP_KEY_ID,RZP_KEY_SECRET))
        res=client.utility.verify_payment_signature(request.POST)
        print(res)
        order_id=request.POST.get("razorpay_order_id")
        order_instance=Order.objects.get(rzp_order_id=order_id)
        order_instance.is_paid=True
        order_instance.save()
        return redirect("student_check")

class Mycourse(View):
    def get(self,request):
        orders=Order.objects.filter(user_instance=request.user,is_paid=True)
        return render (request,"my_course.html",{'orders':orders})
    
class LessonView(View):
    def get(self,request,**kwargs):
        course=Course.objects.get(id=kwargs.get("id"))
        print(request.GET)
        module_id=request.GET.get("module") if "module" in request.GET else course.module.all().first().id
        module_instance=Module.objects.get(id=module_id)
        lesson_id=request.GET.get("lesson") if "lesson" in request.GET else module_instance.lesson.all().first().id
        lesson_instance=Lesson.objects.get(id=lesson_id)
        return render(request,"lesson.html",{'course':course,'lesson':lesson_instance})