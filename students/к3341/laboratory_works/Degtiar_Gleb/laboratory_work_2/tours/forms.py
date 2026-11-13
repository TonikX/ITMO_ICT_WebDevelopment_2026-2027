from django import forms
from .models import Tour, Booking, Review, Country, Agency
class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = ['title','agency','country','description','start_date','end_date','payment_terms','price','is_active']
        widgets = {k:forms.DateInput(attrs={'type':'date'}, format='%Y-%m-%d') for k in ('start_date','end_date')}
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['travelers','comment']
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating','text']
class SearchForm(forms.Form):
    q = forms.CharField(label='Поиск', required=False, max_length=160)
    country = forms.ModelChoiceField(label='Страна', queryset=Country.objects.all(), required=False, empty_label='Все страны')
    agency = forms.ModelChoiceField(label='Турагентство', queryset=Agency.objects.all(), required=False, empty_label='Все агентства')
    date_from = forms.DateField(label='Начало не раньше', required=False, widget=forms.DateInput(attrs={'type':'date'}))
    date_to = forms.DateField(label='Начало не позже', required=False, widget=forms.DateInput(attrs={'type':'date'}))
    max_price = forms.DecimalField(label='Цена до, ₽', required=False, min_value=0, max_digits=10, decimal_places=2)
    sort = forms.ChoiceField(label='Сортировка', required=False, choices=[('start_date','Ближайшие'),('price','Дешевле'),('-price','Дороже'),('title','По названию')])
    def clean(self):
        d=super().clean()
        if d.get('date_from') and d.get('date_to') and d['date_from']>d['date_to']:
            raise forms.ValidationError('Проверьте диапазон дат.')
        return d
class BookingSearchForm(forms.Form):
    q = forms.CharField(label='Название тура', required=False, max_length=160)
    status = forms.ChoiceField(label='Статус', required=False, choices=[('','Все статусы')]+Booking.STATUS)
class SalesSearchForm(forms.Form):
    q = forms.CharField(label='Название тура', required=False, max_length=160)
    country = forms.ModelChoiceField(label='Страна', queryset=Country.objects.all(), required=False, empty_label='Все страны')
