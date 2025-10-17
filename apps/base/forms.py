# from django import forms


# class BaseModelForm(forms.ModelForm):
#     """Base Form with Tailwind Styling and Unique ID Prefix"""
#     tailwindclass = 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'

#     def __init__(self, *args, **kwargs):
#         # Use class name as default prefix
#         prefix = kwargs.pop('prefix', self.__class__.__name__.lower())
#         super().__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             # Only apply Tailwind classes to text-related input fields
#             if isinstance(field.widget, (forms.TextInput, forms.Textarea)):
#                 field_id = f"{prefix}_{field_name}"
#                 field.widget.attrs.update({
#                     'class': self.tailwindclass,
#                     'placeholder': field.label.upper(),  # Convert placeholder to uppercase
#                     'id': field_id,
#                     'style': 'text-transform: uppercase;'  # Force input text to uppercase in UI
#                 })

#     def clean(self):
#         """Ensure all text fields are stored in uppercase"""
#         cleaned_data = super().clean()
#         for field_name, field in self.fields.items():
#             if isinstance(field.widget, (forms.TextInput, forms.Textarea)):
#                 cleaned_data[field_name] = cleaned_data.get(
#                     field_name, "").upper()  # Convert to uppercase
#         return cleaned_data
