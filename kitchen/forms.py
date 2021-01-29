from django import forms
from .models import Kitchens, Categories, Items, SubItems, Menus
from MainApp.models import User


class KitchenSignUpForm(forms.ModelForm):
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
			user.is_kitchen = True
			if commit:
				user.save()
			return user

	def clean(self):
		cleaned_data = super(KitchenSignUpForm, self).clean()
		password = cleaned_data.get("password")
		rpassword = cleaned_data.get("rpassword")
		if password != rpassword:
			raise forms.ValidationError("Passwords didn't Matched.")


class KitchenUserProfileForm(forms.ModelForm):
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


class KitchenForm(forms.ModelForm):
	latitude = forms.FloatField(widget=forms.TextInput(
		attrs={'id': 'lat', 'readonly': 'true'}))
	longitude = forms.FloatField(widget=forms.TextInput(
		attrs={'id': 'lon', 'readonly': 'true'}))
	# video = forms.FileField(help_text='Only Mp4 is supported')

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user',None)
		super(KitchenForm, self).__init__(*args, **kwargs)
		if self.user.kit_Created:
			if self.user.kitchens.approved:
				self.fields['kitName'].widget.attrs['readonly'] = True
				self.fields['address'].widget.attrs['readonly'] = True
				self.fields['city'].widget.attrs['disabled'] = True
				self.fields['city'].required = False
				self.fields['landmark'].widget.attrs['readonly'] = True
				self.fields['postalCode'].widget.attrs['readonly'] = True
				self.fields['floorNo'].widget.attrs['readonly'] = True
				self.fields['video'].widget.attrs['disabled'] = True
				self.fields['fssaiLicNo'].widget.attrs['readonly'] = True
				self.fields['fssaiName'].widget.attrs['readonly'] = True
				self.fields['fssaiAdd'].widget.attrs['readonly'] = True
				self.fields['fssaiExpiry'].widget.attrs['readonly'] = True
				self.fields['fssaiCerti'].widget.attrs['disabled'] = True
				self.fields['kyc'].widget.attrs['disabled'] = True

	def clean_city(self):
		if self.instance and self.instance.pk:
			return self.instance.city
		else:
			return self.cleaned_data['city']

	class Meta:
		model = Kitchens
		fields = ['kitName', 'mode', 'acceptAdvcOrders', 'deliveryTime', 'visibilityRadius', 'pureVeg', 'address', 'city', 'landmark', 'postalCode', 'floorNo', 'latitude',
					'longitude', 'dp', 'video', 'fssaiLicNo', 'fssaiName', 'fssaiAdd', 'fssaiExpiry', 'fssaiCerti', 'kyc', 'degree']


class CategoryForm(forms.ModelForm):
	class Meta:
		model = Categories
		fields = ['category']


class ItemForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user',None)
		super(ItemForm, self).__init__(*args, **kwargs)
		self.fields['category'].queryset = Categories.objects.filter(kit=self.user.kitchens.id)

	class Meta:
		model = Items
		fields = ['category', 'itemName', 'itemType', 'price', 'image', 'condition', 'itemDesc']
		widgets={
			'category': forms.Select(attrs={'class':'form-control'}),
			'itemName': forms.TextInput(attrs={'class':'form-control'}),
			'itemType': forms.Select(attrs={'class':'form-control'}),
			'price': forms.TextInput(attrs={'class':'form-control'}),
			'condition': forms.Textarea(attrs={'class':'form-control', 'rows':2}),
			'itemDesc': forms.Textarea(attrs={'class':'form-control', 'rows':2}),
		}


class SubItemForm(forms.ModelForm):
	class Meta:
		model = SubItems
		fields = ['name', 'price', 'item']
		widgets={
			'name': forms.TextInput(attrs={'class':'form-control'}),
			'price': forms.TextInput(attrs={'class':'form-control'}),
		}


class MenuForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user',None)
		super(MenuForm, self).__init__(*args, **kwargs)
		self.fields['item'].queryset = Items.objects.filter(kit=self.user.kitchens.id)

	class Meta:
		model = Menus
		fields = ['item', 'offer', 'out_of_stock', 'minOrder']
		widgets={
			'item': forms.Select(attrs={'class':'form-control'}),
			'offer': forms.TextInput(attrs={'class':'form-control'}),
			'minOrder': forms.TextInput(attrs={'class':'form-control'}),
		}