from django import forms
from django.utils.translation import gettext_lazy as _

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(
        label=_("Excel File"),
        required=True,
        help_text=_("Select an Excel file (.xlsx) with the correct format."),
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls'})
    )

    def clean_excel_file(self):
        file = self.cleaned_data['excel_file']
        if not file.name.endswith(('.xlsx', '.xls')):
            raise forms.ValidationError(_("File must be .xlsx or .xls."))
        if file.size > 5 * 1024 * 1024:  # 5MB limit
            raise forms.ValidationError(_("File too large. Maximum size is 5MB."))
        return file