from django import forms

from accounts.models import User


class InquiryFilterForm(forms.Form):
    q = forms.CharField(required=False)
    from_date = forms.DateField(required=False)
    to_date = forms.DateField(required=False)
    platform = forms.CharField(required=False)


class InquiryAssignForm(forms.Form):
    assigned_to = forms.ModelChoiceField(queryset=User.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = User.objects.exclude(role="customer").order_by("first_name", "last_name", "username")


class InquiryNoteForm(forms.Form):
    note = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), max_length=2000)


class ProductCsvImportForm(forms.Form):
    csv_file = forms.FileField()

    def clean_csv_file(self):
        file_obj = self.cleaned_data["csv_file"]
        filename = file_obj.name.lower()
        if not filename.endswith(".csv"):
            raise forms.ValidationError("Upload a CSV file.")
        return file_obj
