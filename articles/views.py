from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy, reverse
from .models import Article
from .forms import CommentForm

class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = "article_list.html"

class CommentGet(DetailView):
    model = Article
    template_name = "article_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context

'''
SingleObjectMixin: Proporciona métodos para obtener el objeto sobre el cual operará la vista. 
                   Por ejemplo, get_object() se utiliza para recuperar el objeto basado en la 
                   URL o en otros parámetros.
'''
class CommentPost(SingleObjectMixin, FormView):
    model = Article
    form_class = CommentForm
    template_name = "article_detail.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()     #get_object() para obtener un objeto específico con pk según los parámetros de la URL
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        comment = form.save(commit=False)   #Se crea una instancia del modelo Comment a partir de los datos del formulario pero no se guarda en la BD aun (commit=False)
        comment.article = self.object   #Se asigna el artículo asociado al comentario
        comment.author = self.request.user  #Se asigna el autor del comentario, que es el usuario actual que realizó la solicitud
        comment.save()
        return super().form_valid(form)
    
    '''
    cuando llamamos super().form_valid(form) dentro del método form_valid, estamos invocando al método form_valid de la clase base (FormView). Esto es parte de la herencia de clases en Python.
    El método form_valid() de la clase FormView es responsable de manejar la lógica cuando un formulario es válido. Al llamar super().form_valid(form), estamos delegando esa lógica a la implementación proporcionada por la clase base (FormView).
    Esta llamada tiene un propósito importante: permite que la lógica adicional de FormView se ejecute después de nuestra propia lógica personalizada en form_valid. La clase base FormView se encarga de tareas como redireccionamiento, mensajes de éxito o cualquier otra lógica definida en ella.
    En resumen, al llamar a super().form_valid(form), se ejecuta el código en la clase FormView asociado al manejo de formularios válidos. Esto asegura que cualquier funcionalidad adicional proporcionada por FormView o sus clases base se ejecute después de la lógica personalizada definida en form_valid dentro de la vista CommentPost.
    '''
    
    def get_success_url(self):
        article = self.object
        return reverse("article_detail", kwargs={"pk": article.pk})

class ArticleDetailView(LoginRequiredMixin, View):
    
    def get(self, request, *args, **kwargs):
        view = CommentGet.as_view()
        return view(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        view = CommentPost.as_view()
        return view(request, *args, **kwargs)

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    fields = (
        "title",
        "body",
    )
    template_name = "article_edit.html"

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = "article_delete.html"
    success_url = reverse_lazy('article_list')

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    template_name = "article_new.html"
    fields = (
        "title",
        "body",
    )

    def form_valid(self, form): # Metodo que se utiliza para procesar un formulario cuando todos los datos son validos.
        form.instance.author = self.request.user    #Esta línea asigna el usuario actual (self.request.user) al campo author del objeto de instancia asociado al formulario
        return super().form_valid(form)