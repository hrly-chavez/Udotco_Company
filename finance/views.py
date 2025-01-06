from django.shortcuts import render, redirect,get_object_or_404
from django.forms import modelformset_factory
from datetime import datetime
from shared.models import *
from .forms import *
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.db import transaction
def finance(request):
    return render(request, 'finance/base.html')
#___________________________________________MATERIALS____________________________________________________

def materials(request):
    search_query = request.GET.get('search', '')  # Get the search query from the URL
    category_query = request.GET.get('category', '')  # Get the category filter from the URL

    # Filter materials by search and/or category
    materials = Material.objects.all()

    # Apply search filter
    if search_query:
        materials = materials.filter(
            models.Q(mat_name__icontains=search_query) |  
            models.Q(mat_brand__icontains=search_query) |
            models.Q(mat_category__mat_name__icontains=search_query)
        )

    # Apply category filter
    if category_query:
        materials = materials.filter(mat_category__mat_name__icontains=category_query)

    # Sort materials by 'updated_at' in descending order
    materials = materials.order_by('-updated_at')  # Show recently updated materials at the top

    # Fetch all categories for the dropdown filter
    categories = Material_Category.objects.all()

    return render(
        request,
        'finance/material/materials.html',{'materials': materials,'categories': categories,'selected_category': category_query,},
    )

def add_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            # Extract form data
            mat_name = form.cleaned_data['mat_name']
            mat_quantity = form.cleaned_data['mat_quantity']
            mat_brand = form.cleaned_data['mat_brand']
            mat_measurement = form.cleaned_data['mat_measurement']
            mat_category = form.cleaned_data['mat_category']

            # Check if a material with the same attributes already exists
            existing_material = Material.objects.filter(
                mat_name=mat_name,
                mat_brand=mat_brand,
                mat_measurement=mat_measurement,
                mat_category=mat_category
            ).first()

            if existing_material:
                # Increment quantity if material already exists
                existing_material.mat_quantity += mat_quantity
                existing_material.save(update_fields=['mat_quantity', 'updated_at'])
                messages.success(request, "Material updated successfully. Quantity incremented.")
            else:
                # Save new material if no match is found
                form.save()
                messages.success(request, "New material added successfully.")

            return redirect('finance:materials')  # Redirect after adding material
    else:
        form = MaterialForm()

    return render(request, 'finance/material/add_material.html', {'form': form})

def delete_material(request, mat_code):
    if request.method == 'POST':
        material = get_object_or_404(Material, mat_code=mat_code)
        material.delete()
        return redirect('finance:materials')

def edit_material(request, mat_code):
    material = get_object_or_404(Material, mat_code=mat_code)

    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            return redirect('finance:materials')
    else:
        form = MaterialForm(instance=material)

    return render(request, 'finance/material/edit_material.html', {'form': form})

#____________________________________MECHANIC_____________________________________________________________

def mechanic_req(request):
    # Retrieve all material requests but exclude approved ones
    item_requests = Material_Requested.objects.select_related(
        'mat_code__mat_category', 'item_req_num__bus_unit_num', 'item_req_num__item_req_approved_by'
    ).exclude(item_req_num__item_req_status='Approved')  # Exclude approved items

    # Fetch all categories for the dropdown (optional, if you still want to display category options)
    categories = Material_Category.objects.all()

    context = {
        'item_requests': item_requests,
        'categories': categories,  # Remove this if you no longer need categories
    }

    return render(request, 'finance/mechanic/auto_parts_req.html', context)

def approve_material(request, mat_req_id):
    if request.method == "POST":
        try:
            # Fetch material request
            material_request = get_object_or_404(Material_Requested, pk=mat_req_id)

            # Check if the item has already been approved
            if material_request.item_req_num.item_req_status == 'Approved':
                return JsonResponse({'success': False, 'error': 'Item has already been approved'})

            # Use a transaction to ensure atomicity
            with transaction.atomic():
                # Update the item request status
                item_request = material_request.item_req_num
                item_request.item_req_status = 'Approved'
                item_request.save()

                # Create a new Material_Approved entry
                Material_Approved.objects.create(
                    mat_req_id=material_request,
                    ir_num=item_request,
                    mat_approved_qty=material_request.mat_req_qty,  # Approved quantity
                    mat_approved_code=material_request.mat_code,    # Approved material
                )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def deny_material(request, mat_req_id):
    if request.method == "POST":
        try:
            # Fetch material request
            material_request = get_object_or_404(Material_Requested, pk=mat_req_id)

            # Delete the material request entry
            material_request.delete()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

#____________________________________PURCHASE ORDER________________________________________________________

def purchase_odr(request, po_num=None):
    if po_num:
        # View a specific purchase order
        purchase_order = get_object_or_404(Purchase_Order, po_num=po_num)
        material_orders = Material_Order.objects.filter(purchase_order=purchase_order)
        context = {
            'purchase_order': purchase_order,
            'material_orders': material_orders,
        }
        return render(request, 'finance/purchase_odr/view_purchase_odr.html', context)
    else:
        # Display all purchase orders
        purchase_orders = Purchase_Order.objects.all()
        statuses = Purchase_Order_Status.STATUS_CHOICES  # Get the status choices
        context = {
            'purchase_orders': purchase_orders,
            'statuses': statuses,  # Add statuses to context
            'selected_status': '',  # Default value for selected status
        }
        return render(request, 'finance/purchase_odr/purchase_odr.html', context)

def filter_purchase_orders(request):
    # Get query parameters
    start_date = request.GET.get('start_date', '')  # Retrieve the date filter
    selected_status = request.GET.get('status', '')  # Retrieve the status filter

    # Base queryset for purchase orders
    purchase_orders = Purchase_Order.objects.all()

    # Apply date filter if a valid date is provided
    if start_date:
        try:
            # Try filtering by the exact date
            exact_date_orders = purchase_orders.filter(po_datemade=start_date)

            if exact_date_orders.exists():
                purchase_orders = exact_date_orders
            else:
                # Fallback: Filter by the same month and year
                date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                purchase_orders = purchase_orders.filter(
                    po_datemade__year=date_obj.year,
                    po_datemade__month=date_obj.month
                )
        except ValueError:
            pass  # Ignore invalid dates

    # Apply status filter if a valid status is provided
    if selected_status:
        purchase_orders = purchase_orders.filter(postat_id__postat_status=selected_status)

    # Prepare context for rendering
    context = {
        'purchase_orders': purchase_orders,
        'statuses': Purchase_Order_Status.STATUS_CHOICES,
        'selected_status': selected_status,
        'form': DateFilterForm(initial={'start_date': start_date}),
    }

    return render(request, 'finance/purchase_odr/purchase_odr.html', context)

def create_purchase_order(request):
    # Create the formset with the ability to delete
    MaterialOrderFormSet = modelformset_factory(Material_Order, form=MaterialOrderForm, extra=1, can_delete=True)

    # Check if a purchase order already exists (you might need to change this if you're editing an existing one)
    purchase_order = None
    is_locked = False

    if request.method == 'POST':
        purchase_order_form = PurchaseOrderForm(request.POST)
        formset = MaterialOrderFormSet(request.POST, queryset=Material_Order.objects.none())

        if purchase_order_form.is_valid() and formset.is_valid():
            purchase_order = purchase_order_form.save(commit=False)

            # Ensure 'postat_id' is set to 'Waiting' if it's not provided (default behavior)
            waiting_status, created = Purchase_Order_Status.objects.get_or_create(postat_status='Waiting')
            purchase_order.postat_id = waiting_status

            # Set po_datemade to the current date if not provided
            if not purchase_order.po_datemade:
                purchase_order.po_datemade = timezone.now().date()

            purchase_order.save()

            # Save associated material orders
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                    material_order = form.save(commit=False)
                    material_order.purchase_order = purchase_order
                    material_order.save()

            return redirect('finance:purchase_odr')
    else:
        purchase_order_form = PurchaseOrderForm()
        formset = MaterialOrderFormSet(queryset=Material_Order.objects.none())

    # Check if the purchase order's status is 'Ongoing' or 'Done'
    # Only lock the form if status is Ongoing or Done, not Waiting
    if purchase_order and purchase_order.postat_id.postat_status in ['Ongoing', 'Done']:
        is_locked = True

    return render(request, 'finance/purchase_odr/make_purchase_odr.html', {
        'purchase_order_form': purchase_order_form,
        'formset': formset,
        'is_locked': is_locked,  # Pass the is_locked flag to the template
    })

def edit_purchase_order(request, po_num):
    # Retrieve the purchase order
    purchase_order = get_object_or_404(Purchase_Order, po_num=po_num)

    # Retrieve related materials
    related_materials = Material_Order.objects.filter(purchase_order=purchase_order)

    # Check if the status is Ongoing or Done
    is_locked = purchase_order.postat_id.postat_status in ['Ongoing', 'Done']

    if request.method == 'POST':
        # Create form with instance of the purchase order to edit
        form = PurchaseOrderForm(request.POST, instance=purchase_order)

        if form.is_valid():
            form.save()
            return redirect('finance:purchase_odr')  # Redirect to the purchase orders list
    else:
        # For GET requests, initialize the form with the purchase order data
        form = PurchaseOrderForm(instance=purchase_order)

        # Make the 'po_datemade' field read-only
        form.fields['po_datemade'].widget.attrs['readonly'] = True

        # If the status is Ongoing or Done, disable all fields in the form
        if is_locked:
            for field in form.fields:
                form.fields[field].widget.attrs['readonly'] = True
                form.fields[field].widget.attrs['disabled'] = 'disabled'

        # Allow editing 'postat_id' if status is 'Waiting'
        if purchase_order.postat_id.postat_status == 'Waiting':
            form.fields['postat_id'].widget.attrs['disabled'] = False

        # Disable 'postat_id' field if the status is 'Done'
        if purchase_order.postat_id.postat_status == 'Done':
            form.fields['postat_id'].widget.attrs['disabled'] = 'disabled'

    return render(request, 'finance/purchase_odr/edit_purchase_odr.html', {
        'form': form,
        'purchase_order': purchase_order,
        'related_materials': related_materials,  # Pass related materials to the template
        'is_locked': is_locked,  # Pass the locked status to the template
    })

def delete_purchase_order(request, po_num):
    # Get the purchase order object by PO number
    purchase_order = get_object_or_404(Purchase_Order, po_num=po_num)

    # Delete the purchase order
    purchase_order.delete()

    # Redirect to the purchase orders list page
    return redirect('finance:purchase_odr')

#____________________________________AR_____________________________________________________________
def ack_rep(request):
    return render(request, 'finance/ack_rep/ack_rep.html')

def create_ack_rep(request):
    if request.method == 'POST':
        form = AcknowledgmentReceiptForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ack_rep_list')  
    else:
        form = AcknowledgmentReceiptForm()

    return render(request, 'finance/ack_rep/create_ack_rep.html', {'form': form})





def logout_view(request):
    # Clear the session (log out the user)
    logout(request)
    
    # Redirect to the login page after logout
    return redirect('login:login')  # Make sure the 'login' URL name matches the one in your URL configuration
