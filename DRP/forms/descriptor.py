"""Forms for the django admin for custom descriptors."""

from django import forms
from django.core.exceptions import ValidationError
from DRP.models import CatRxnDescriptor, OrdRxnDescriptor, NumRxnDescriptor, BoolRxnDescriptor
from DRP.models import CategoricalDescriptorPermittedValue, CategoricalDescriptor


class DescriptorAdmin(forms.ModelForm):
    """A mixin for behaviours common to all descriptor admin forms."""

    def clean(self, *args, **kwargs):
        """Method is purely desingned to stop the overwriting of plugin descriptors."""
        cleaned_data = super(DescriptorAdmin, self).clean(*args, **kwargs)
        if self.instance.id is not None and self.instance.calculatorSoftware != 'manual':
            raise ValidationError(
                'This descriptor is not a manual descriptor, and thus cannot be edited using the django admin', 'not_manual')
        return cleaned_data

    def save(self, commit=True, *args, **kwargs):
        """Save the new descriptor, forcing it to be manual."""
        descriptor = super(DescriptorAdmin, self).save(
            commit=False, *args, **kwargs)
        descriptor.calculatorSoftware = 'manual'
        descriptor.calculatorSoftwareVersion = '0'
        if commit:
            descriptor.save()
        return descriptor


class CatRxnDescriptorForm(DescriptorAdmin):
    """An admin form for custom Categorical Reaction Descriptors."""

    class Meta:
        fields = ('heading', 'name')
        model = CatRxnDescriptor


class CatDescPermittedValueForm(forms.ModelForm):
    """A mechanism to create permitted values for custom Categorical Reaction descriptors."""

    class Meta:
        model = CategoricalDescriptorPermittedValue
        fields = ('descriptor', 'value')

    def clean(self, *args, **kwargs):
        """Ensure that the manual descriptor is actually custom."""
        cleaned_data = super(CatDescPermittedValueForm,
                             self).clean(*args, **kwargs)
        if self.cleaned_data.get('descriptor') is not None:
            if not CategoricalDescriptor.objects.filter(calculatorSoftware='manual', id=self.cleaned_data.get('descriptor').id).exists():
                raise ValidationError(
                    'You may only edit descriptor values for your own custom descriptors')
            return cleaned_data

    def __init__(self, *args, **kwargs):
        """Limit the set of related valid descirptors."""
        super(CatDescPermittedValueForm, self).__init__(*args, **kwargs)
        self.fields['descriptor'].queryset = CategoricalDescriptor.objects.filter(
            calculatorSoftware='manual')


class OrdRxnDescriptorForm(DescriptorAdmin):
    """An admin form for creating custom Ordinal reaction descriptors."""

    class Meta:
        fields = ('heading', 'name', 'minimum', 'maximum')
        model = OrdRxnDescriptor


class NumRxnDescriptorForm(DescriptorAdmin):
    """An admin form for creating custom numeric reaction descriptors."""

    class Meta:
        fields = ('heading', 'name', 'minimum', 'maximum')
        model = NumRxnDescriptor


class BoolRxnDescriptorForm(DescriptorAdmin):
    """An admin form for creating custom boolean reaction descriptors."""

    class Meta:
        fields = ('heading', 'name')
        model = BoolRxnDescriptor
