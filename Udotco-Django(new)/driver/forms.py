from django import forms
from shared.models import *


class JobOrderForm(forms.ModelForm):
    class Meta:
        model = JobOrder
        fields = [
            'j_o_date_requested',
            'j_o_work_description',
            'j_o_bus_unit_num',
        ]  
        widgets = {
            'j_o_date_requested': forms.DateInput(attrs={'type': 'date'}),
            'j_o_work_description': forms.Textarea(attrs={'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        super(JobOrderForm, self).__init__(*args, **kwargs)
        # Prepopulate the job order number field from the selected JobOrder instance
        if self.instance and self.instance.pk:
            self.fields['j_o_number'].initial = self.instance.j_o_number
            self.fields['j_o_bus_unit_num'].initial = self.instance.j_o_bus_unit_num.id