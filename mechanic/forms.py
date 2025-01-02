from django import forms

from shared.models import *


# Form for Item Request details
class ItemRequestForm(forms.ModelForm):
    class Meta:
        model = Item_Request
        fields = [
            'item_req_approved_by',
            'item_req_date_requested',
            'item_req_description',
            'item_req_status',
            'bus_unit_num',  # Bus unit field
        ]
        labels = {
            'item_req_approved_by': 'Approved By',
            'item_req_date_requested': 'Date Requested',
            'item_req_description': 'Description',
            'item_req_status': 'Status',
            'bus_unit_num': 'Bus Unit',
        }
        widgets = {
            'item_req_approved_by': forms.Select(attrs={'class': 'form-select'}),
            'item_req_date_requested': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'item_req_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'item_req_status': forms.Select(attrs={'class': 'form-select', 'disabled': 'disabled'}),  # Disabled for read-only
            'bus_unit_num': forms.Select(attrs={'class': 'form-select', 'disabled': 'disabled'}),  # Disabled for read-only
        }

    def __init__(self, *args, **kwargs):
        job_order = kwargs.pop('job_order', None)
        super(ItemRequestForm, self).__init__(*args, **kwargs)

        # Set default value for item_req_status
        self.fields['item_req_status'].initial = 'Waiting'
        self.fields['item_req_status'].required = False  # Make sure the field is not required in the form

        if job_order:
            # Prepopulate the bus_unit_num field with the actual Bus object from the job order
            self.fields['bus_unit_num'].initial = job_order.j_o_bus_unit_num  # Using the Bus object here

            # Ensure that the queryset for bus_unit_num only includes the bus associated with the job_order
            self.fields['bus_unit_num'].queryset = Bus.objects.filter(bus_unit_num=job_order.j_o_bus_unit_num.bus_unit_num)

        # Limit the 'Approved By' dropdown to only employees who have roles related to approval
        self.fields['item_req_approved_by'].queryset = Employee.objects.filter(emp_role__icontains='Manager')

        # Optional: Add a fallback to include all employees if no 'Manager' found
        if not self.fields['item_req_approved_by'].queryset.exists():
            self.fields['item_req_approved_by'].queryset = Employee.objects.all()
