from django import forms
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

from lists.models import Item

EMPTY_ITEM_ERROR_MESSAGE = 'You can\'t have an empty list item'
DUPLICATE_ITEM_ERROR_MESSAGE = "You've already got this in your list"


class ItemForm(forms.models.ModelForm):
    class Meta:
        model = Item
        fields = ('text',)
        widgets = {
            'text': forms.fields.TextInput(attrs={
                'placeholder': 'Enter a to-do item',
                'class': 'form-control form-control-lg'}
            )
        }
        error_messages = {
            'text': {'required': EMPTY_ITEM_ERROR_MESSAGE}
        }

    def save(self, for_list):
        self.instance.list = for_list
        return super(ItemForm, self).save()


class ExistingListItemForm(ItemForm):
    def __init__(self, for_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.list = for_list

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            e.error_dict = {'text': [DUPLICATE_ITEM_ERROR_MESSAGE]}
            self._update_errors(e)

    def save(self):
        return forms.models.ModelForm.save(self)

