from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from dashboard.models import Examform
from app.models import UserProfile
from django.db.models import Q



def dashboard_view(req):
    user_id=req.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    profiles=UserProfile.objects.filter(id=user_id)
    if not profiles.exists():
        return redirect('login')

    return render(req,'dashboard/dashboard.html',{'user':profiles.first()})







def fill_exam_form_view(req):
    user_id=req.session.get('user_id')
    if not user_id:
        return redirect('login')
    

    profiles=UserProfile.objects.filter(id=user_id)
    if not profiles.exists():
        return redirect('login')
    user=profiles.first()

    if req.method=='POST':
        name=req.POST.get('name','').strip()
        enrollment=req.POST.get('enrollment','').strip()
        semester=req.POST.get('semester')
        year=req.POST.get('year')
        subject=req.POST.get('subject','').strip()
        exam_type=req.POST.get('exam_type')


        if not all([name,enrollment,semester,year,subject,exam_type]):
            messages.error(req,"Saare fields bharna compulsory hai")
            return redirect('fill_exam_form')



        if Examform.objects.filter(user_profile=user,semester=semester).exists():
            messages.error(req,f'Apne pehle se he {semester} ka form submit kr diya hai')
            return redirect('fill_exam_form')


        Examform.objects.create(
            user_profile=user,
            name=name,
            enrollment_no=enrollment,
            semester=semester,
            year=year,
            subject=subject,
            exam_type=exam_type,
        
        )

        messages.success(req,'Form submitted successfully')
        return redirect('fill_exam_form')

    

    return render(req,'dashboard/fill_form.html', {
                'user':user, 
                'semesters':Examform.SEMESTER_CHOISES ,
                'years':Examform.YEAR_CHOISES

    })
        



        






def show_form_view(req):
   user_id=req.session.get('user_id')
   if not user_id:
       return redirect('login')

   search=req.GET.get('search')

   profiles=UserProfile.objects.filter(id=user_id)
   if not profiles.exists():
       return redirect('login')
   

   user=profiles.first()
   user_form=Examform.objects.filter(user_profile=user)


   if search:
        user_form=user_form.filter(
            Q(name__icontains=search) |
            Q(enrollment_no__icontains=search) |
            Q(semester__icontains=search) |
            Q(year__icontains=search) |
            Q(subject__icontains=search) |
            Q(exam_type__icontains=search)
              

        )
        
       


   return render(req, 'dashboard/show_details.html',{

             'forms_data':user_form,
             'user':user,
             'search_query':search
       
   })








def edit_exam_form_view(req, form_id): 
    user_id = req.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    user = UserProfile.objects.filter(id=user_id).first()
    if not user:
        return redirect('login')

   
    exam_form =get_object_or_404(Examform, id=form_id, user_profile=user)

   
    if req.method == 'POST':
        exam_form.name = req.POST.get('name', '').strip()
        exam_form.enrollment_no = req.POST.get('enrollment', '').strip()
        exam_form.semester = req.POST.get('semester')
        exam_form.year = req.POST.get('year')
        exam_form.subject = req.POST.get('subject', '').strip()
        exam_form.exam_type = req.POST.get('exam_type')

       
        exam_form.save()

        messages.success(req, "Exam Form successfully update ho gaya!")
        return redirect('show_details') 

   
    context = {
        'form': exam_form,
        'user':user,
        'semesters': Examform.SEMESTER_CHOISES,
        'years': Examform.YEAR_CHOISES,

    }
    return render(req, 'dashboard/edit_form.html', context)


  






       


def delete_exam_form_view(req,form_id):
    user_id=req.session.get('user_id')
    if not user_id:
        return redirect('login')
    

    user=UserProfile.objects.filter(id=user_id).first()
    if not user:
        return redirect('login')

    exam_form=get_object_or_404(Examform,id=form_id,user_profile=user)

    exam_form.delete()
    messages.success(req,'Exam form successfully deleted')
    return redirect('show_details')




    



def download_exam_form_view(req,form_id):
    user_id=req.session.get('user_id')
    if not user_id:
        return redirect('login')

    user=UserProfile.objects.filter(id=user_id).first()
    if not user:
        return redirect('login')

    exam_form=get_object_or_404(Examform,id=form_id, user_profile=user)

    return render(req,'dashboard/download_form.html' ,{'form':exam_form})
   


