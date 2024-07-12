
from django.urls import path
from . import views
urlpatterns = [
    path("",views.index,name='index'),
    path("pdf-summarize/",views.pdf_summarize,name='pdf-summarize'),
    
]
