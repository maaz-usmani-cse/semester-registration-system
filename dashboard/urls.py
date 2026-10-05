from django.urls import path
from . import views


urlpatterns=[

    path('',views.dashboard_view,name='dashboard'),
    path('fill_exam_form/',views.fill_exam_form_view,name='fill_exam_form'),
    path('show_details/',views.show_form_view,name='show_details'),
    path('edit_exam-form/<int:form_id>/', views.edit_exam_form_view,name='edit_exam_form'),
    path('delete_exam_form/<int:form_id>/', views.delete_exam_form_view,name='delete_exam_form'),
    path('download_exam_form/<int:form_id>/' , views.download_exam_form_view,name='download_exam_form')

]


