from django import forms

class UploadCSVForm(forms.Form):
    certificate_type = forms.ChoiceField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C')])
    csv_file = forms.FileField()
