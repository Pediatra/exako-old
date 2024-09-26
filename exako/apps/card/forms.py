from django import forms
from django.utils.translation import gettext as _


from exako.apps.card.models import CardSet
from exako.apps.term.constants import Language


class CardSetForm(forms.ModelForm):
    class Meta:
        model = CardSet
        fields = ['name', 'language']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500',
                    'placeholder': 'Nome do conjunto de cartões',
                }
            ),
            'language': forms.Select(
                attrs={
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.label_attrs = {
                'class': 'block mb-2 text-sm font-medium text-gray-700'
            }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise forms.ValidationError(_('O nome deve ter pelo menos 3 caracteres.'))
        return name

    def clean_language(self):
        language = self.cleaned_data.get('language')
        if language is None:
            return 
        try:
            Language(language)
        except ValueError:
            raise forms.ValidationError(_('Língua não encontrada.'))
        return language
