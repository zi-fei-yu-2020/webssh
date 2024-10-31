from django.urls import path
from . import views

urlpatterns = [
    path('terminal/list', views.list_terminal_servers),
    path('terminal/create', views.create_terminal_server),
    path('terminal/retrieve/<int:pk>', views.retrieve_terminal_server),
    path('terminal/update/<int:pk>', views.update_terminal_server),
    path('terminal/delete/<int:pk>', views.delete_terminal_server),
    path('terminal/multiple_delete', views.multiple_delete_terminal_servers),
]
