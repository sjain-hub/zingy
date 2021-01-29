from django import forms
from .models import User, Addresses

class CustomerSignUpForm(forms.ModelForm):
	email = forms.CharField(widget=forms.EmailInput(
		attrs={'class': 'form-control', 'placeholder': 'Email'}))
	rpassword = forms.CharField(widget=forms.PasswordInput(
		attrs={'class': 'form-control', 'placeholder': 'Re-enter Password'}))
	password = forms.CharField(widget=forms.PasswordInput(render_value = True,
		attrs={'class': 'form-control', 'placeholder': 'Password'}))
	first_name = forms.CharField(widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': 'First Name'}))
	last_name = forms.CharField(widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
	username = forms.CharField(widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': 'Username'}))
	phone = forms.CharField(widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': 'Phone No.'}))

	class Meta:
		model = User
		fields = ['username', 'email', 'phone', 'password',
					'rpassword', 'first_name', 'last_name']

		def save(self, commit=True):
			user = super().save(commit=False)
			user.is_customer = True
			if commit:
				user.save()
			return user

	def clean(self):
		cleaned_data = super(CustomerSignUpForm, self).clean()
		password = cleaned_data.get("password")
		rpassword = cleaned_data.get("rpassword")
		if password != rpassword:
			raise forms.ValidationError("Passwords didn't Matched.")


class CustomerUserProfileForm(forms.ModelForm):
	email = forms.CharField(widget=forms.EmailInput(
		attrs={'class': 'form-control', 'placeholder': 'Email', 'readonly': 'true'}))
	password = forms.CharField(widget=forms.PasswordInput(render_value = True,
		attrs={'class': 'form-control', 'placeholder': 'Password', 'readonly': 'true'}))
	first_name = forms.CharField(widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': 'First Name', 'readonly': 'true'}))
	last_name = forms.CharField(widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': 'Last Name', 'readonly': 'true'}))
	username = forms.CharField(widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': 'Username', 'readonly': 'true'}))
	phone = forms.CharField(widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': 'Phone No.', 'readonly': 'true'}))

	class Meta:
		model = User
		fields = ['username', 'email', 'phone', 'password', 'first_name', 'last_name']

		def save(self, commit=True):
			user = super().save(commit=False)
			user.is_kitchen = True
			if commit:
				user.save()
			return user


class UserAddressesForm(forms.ModelForm):
	latitude = forms.FloatField(widget=forms.TextInput(
		attrs={'id': 'lat', 'hidden': 'true'}))
	longitude = forms.FloatField(widget=forms.TextInput(
		attrs={'id': 'lon', 'hidden': 'true'}))

	class Meta:
		model = Addresses
		fields = ['place', 'latitude', 'longitude',
					'address', 'floorNo']