# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from tienda.models import StoreUser
from django.contrib import messages
from collections import OrderedDict


class LoginForm(AuthenticationForm):
    """ Form para el login de usuarios registrados"""
    username = forms.EmailField(max_length=200, label='Email')

    def __init__(self, request=None, *args, **kwargs):
        super(LoginForm, self).__init__(request=request, *args, **kwargs)
        if request:
            email = request.GET.get('email')
            if email:
                self.fields['username'].initial = email


class RegisterForm(forms.Form):

    name = forms.CharField(max_length=200, label='Nombre')
    last_name = forms.CharField(max_length=200, label='Apellido')
    gov_id = forms.IntegerField(label='Gov id')
    email = forms.EmailField(max_length=200, label='Email')
    repeat_email = forms.EmailField(max_length=200, label='Verificar Email')
    city = forms.CharField(max_length=200, label='Ciudad')
    street_address_1 = forms.CharField(max_length=200, label='Direccion')
    city_area = forms.CharField(max_length=200, label='Barrio')
    phone = forms.IntegerField(label='Telefono')
    mobile = forms.IntegerField(label='Celular')
    password = forms.CharField(max_length=200, label='Contraseña', widget=forms.PasswordInput())
    repeat_password = forms.CharField(max_length=200, label='Repetir Contraseña', widget=forms.PasswordInput())

    def clean(self): #llamado por is_valid
        cleaned_data = super(RegisterForm, self).clean()
        #print cleaned_data
        if len(self.errors):
            # no se puede continuar
            return cleaned_data

        if cleaned_data['password'] != cleaned_data['repeat_password']:
            raise forms.ValidationError('La contraseña no coincide', code='invalid_password_verification')
        email = cleaned_data['email']
        verify_email = cleaned_data['repeat_email']
        if email != verify_email:
            raise forms.ValidationError('El email no coincide', code='invalid_email_verification')
        
        if len(StoreUser.objects.filter(email=email)):
            #ya hay un usuario con ese email
            raise forms.ValidationError('El email ya esta siendo usado', code='invalid_email')

        return cleaned_data


class UpdateUserForm(RegisterForm):
    """ El mismo form usado para el registro con un campo añadido
    para seguridad"""
    security_password = forms.CharField(
        label="Contraseña actual", widget=forms.PasswordInput())
    password = forms.CharField(max_length=200, label='Nueva contraseña', widget=forms.PasswordInput(), required=False)
    repeat_password = forms.CharField(max_length=200, label='Repetir Nueva contraseña', widget=forms.PasswordInput(),
                                      required=False)

    def clean(self):
        user = self.request.user
        try:
            cleaned_data = super(UpdateUserForm, self).clean()
            print cleaned_data
        except Exception as e:
            # Si el email ya existe  en bd ignorar si se trata del mismo usuario
            # de la sesion actual
            if e.code == 'invalid_email':
                if (user.email != self.cleaned_data['email']):
                    raise e
            else:
                print e
                messages.error(self.request,
                               'Por favor verifique que haya ingresado correctamente los campos del formulario')
                raise e
        # verificar que security_password sea igual a request.user.password (actual)
        print self.cleaned_data
        if not user.check_password(self.request.POST['security_password']):
            messages.error(self.request,
                           'Por favor verifique que haya ingresado correctamente los campos del formulario')
            raise forms.ValidationError('Contraseña actual incorrecta', code='invalid_password')
        return self.cleaned_data

UpdateUserForm.base_fields = OrderedDict(
    (k, UpdateUserForm.base_fields[k])
    for k in ['name', 'last_name', 'email', 'repeat_email', 'gov_id', 'city', 'street_address_1','city_area', 'phone', 'mobile', 'security_password', 'password', 'repeat_password']
)
