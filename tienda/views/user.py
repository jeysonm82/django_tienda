# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.views.generic import TemplateView
from tienda import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from tienda.models import StoreUser
from tienda.forms import RegisterForm, UpdateUserForm
from django.views.generic import TemplateView, FormView, ListView

class RegisterUserView(FormView):
    template_name = ''
    success_url = ''
    form_class = RegisterForm

    def form_valid(self, form):
        #Registrarlo
        data = form.cleaned_data
        self.create_user(form.cleaned_data)
        self.preserve_sessiondata()
        #Autenticarlo
        user = authenticate(username=data['email'], password=data['password'])
        #Loguearlo
        login(self.request, user)
        # TODO enviar email
        return super(RegisterUserView, self).form_valid(form)

    def preserve_sessiondata(self):
        #Toca copiar la data de la sesion actual antes del login y restaurarla despues
        data_session = {k: v for k, v in self.request.session.iteritems()}
        for k, v in data_session.iteritems():
            self.request.session[k] = v

    def create_user(self, data):
        user = StoreUser.objects.create_user(email=data['email'], password=data['password'],
                                        name=data['name'], last_name=data['last_name'],
                                        gov_id=data['gov_id'])
        return user

class RegisterAndLoginView(TemplateView):
    """Vista de login y registro usada para acceder a otras vistas que requieran
    una sesion de usuario activa.
    - Login: El usuario existente se puede loguear. Una vez logueado lo redirecciona a
    la vista especificada en next (GET['next']).
    -Register: El usuario nuevo se registra y el sistema lo loguea y aplica los mismos pasos.
    Si ya hay una sesion iniciada se procede de inmediato a next.
    """
    template_name = 'web_shop/login.html'
    login_form, register_form = None, None

    def get_context_data(self, **kwargs):
        context = super(RegisterAndLoginView, self).get_context_data(**kwargs)
        context['form'] = self.login_form or forms.LoginForm()
        context['form_register'] = self.register_form or forms.RegisterForm()
        #El next se usa para saber adonde ir despues de que el form procese
        # correctamente (login o register).
        # El next puede estar en la url (GET)  o en el form (POST)
        if 'next' in self.request.GET:
            context['next'] = self.request.GET['next']
        elif 'next' in self.request.POST:
            context['next'] = self.request.POST['next']

        return context

    def dispatch(self, request, *args, **kwargs):
        #El dispatch es lo primero que se llama. Este llama a get o a post segun el request
        if request.user.is_authenticated():
            #El user de la sesion esta autenticado?
            #Ir a next inmediatamente.
            next_ = self.request.GET['next'] if 'next' in request.GET else ''
            if next_ == 'checkout':
                #volver al checkout
                return redirect('checkout_index')
            elif next_ == 'logout':
                logout(request)
                return redirect('home')
            else:
                return redirect('home')

        return super(RegisterAndLoginView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.POST or None     # lo que posteo el usuario
        form_name = data['form_name'] if 'form_name' in data else ''

        if(form_name == 'login'):
            result = self.do_login(request, data)
        elif(form_name == 'register'):
            result = self.do_register(request, data)
        else:
            result = False

        if result:
            next_ = data['next']
            # redir a donde? depende
            if next_ == 'checkout':
                #volver al checkout
                return redirect('checkout_index')
            else:
                #TODO redir a panel de usuario?
                return redirect('home')
        return super(RegisterAndLoginView, self).get(request, *args, **kwargs)

    def do_register(self, request, data):
        self.register_form = forms.RegisterForm(data=data)
        if self.register_form.is_valid():
            #Registrarlo
            data = self.register_form.cleaned_data
            user = StoreUser.objects.create_user(email=data['email'], password=data['password'],
                                            name=data['name'], last_name=data['last_name'])
            #Toca copiar la data de la sesion actual antes del login y restaurarla despues
            data_session = {k: v for k, v in request.session.iteritems()}

            #Autenticarlo
            user = authenticate(username=data['email'], password=data['password'])
            #Loguearlo
            login(request, user)
            for k, v in data_session.iteritems():
                request.session[k] = v
            return True
        

    def do_login(self, request, data):
        self.login_form = forms.LoginForm(request, data=data)
        if self.login_form.is_valid(): #El authenticate se hace adentro cuando se llama is valid
            #Loguearlo a la sesion
            login(request, self.login_form.get_user())
            return True


class ChangePersonalDataView(FormView):
    """Vista para actualizar datos personales (nombres, contraseña o email).
    El Form debe tener un campo adicional donde se ingresa la contraseña actual
    """

    template_name = 'web_shop/control_panel/account_settings.html'
    form_class = UpdateUserForm
    success_url = 'account_settings'

    def get_form(self, form_class=None):
        form = super(ChangePersonalDataView, self).get_form(form_class)
        form.request = self.request
        form.fields['name'].initial = self.request.user.user.name
        form.fields['last_name'].initial = self.request.user.user.last_name
        form.fields['email'].initial = self.request.user.user.email
        form.fields['repeat_email'].initial = self.request.user.user.email
        return form

    def get_context_data(self, **kwargs):
        context = super(
            ChangePersonalDataView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        """Este metodo se llama si la validacion del form fue exitosa"""
        user = self.request.user.user
        data = self.request.POST
        changes = False
        # TODO actualizar datos de user
        # Password con set_password y luego save al final
        if user.name != data['name']:
            user.name = data['name']
            changes = True
        if user.last_name != data['last_name']:
            user.last_name = data['last_name']
            changes = True
        if user.email != data['email']:
            user.email = data['email']
            changes = True
        if data['password'] != '' and not user.check_password(data['password']):
            user.set_password(data['password'])
            changes = True
        user.save()
        if changes:
            messages.success(self.request, 'Sus datos han sido actualizados con éxito')
        return super(ChangePersonalDataView, self).form_valid(form)
