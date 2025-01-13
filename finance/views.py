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
import json
from django.views.decorators.csrf import csrf_exempt





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
# def mechanic_req(request):
#     # Retrieve all material requests but exclude both approved and denied ones
#     item_requests = Material_Requested.objects.select_related(
#         'mat_code__mat_category', 'item_req_num__bus_unit_num', 'item_req_num__item_req_approved_by'
#     ).exclude(mat_req_status__in=['Approved', 'Denied'])  # Exclude both approved and denied materials

#     # Fetch all categories for the dropdown (optional, if needed)
#     categories = Material_Category.objects.all()

#     context = {
#         'item_requests': item_requests,
#         'categories': categories,
#     }

#     return render(request, 'finance/mechanic/auto_parts_req.html', context)
def mechanic_req(request):
    # Retrieve all material requests but exclude both approved and denied ones
    item_requests = Material_Requested.objects.select_related(
        'mat_code__mat_category', 'item_req_num__bus_unit_num', 'item_req_num__item_req_approved_by'
    ).exclude(mat_req_status__in=['Approved', 'Denied'])  # Exclude both approved and denied materials

    # Retrieve all material orders
    material_orders = Material_Order.objects.select_related(
        'mat_category', 'purchase_order'
    ).all()

    context = {
        'item_requests': item_requests,
        'material_orders': material_orders,
    }

    return render(request, 'finance/mechanic/auto_parts_req.html', context)


@csrf_exempt
def approve_material(request, mat_req_id):
    if request.method == "POST":
        try:
            material_request = get_object_or_404(Material_Requested, pk=mat_req_id)

            if material_request.mat_req_status == 'Approved':
                return JsonResponse({'success': False, 'error': 'Material already approved'})

            with transaction.atomic():
                material_request.mat_req_status = 'Approved'
                material_request.save()

                # Create record in Material_Approved
                Material_Approved.objects.create(
                    mat_req_id=material_request,
                    ir_num=material_request.item_req_num,
                    mat_approved_qty=material_request.mat_req_qty,
                    mat_approved_code=material_request.mat_code,
                )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@csrf_exempt
def deny_material(request, mat_req_id):
    if request.method == "POST":
        try:
            material_request = get_object_or_404(Material_Requested, pk=mat_req_id)

            if material_request.mat_req_status == 'Denied':
                return JsonResponse({'success': False, 'error': 'Material already denied'})

            with transaction.atomic():
                material_request.mat_req_status = 'Denied'
                material_request.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

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

def get_material_details(request, mat_odr_id):
    if request.method == 'GET':
        try:
            material = Material_Order.objects.get(pk=mat_odr_id)  
            data = {
                'mat_odr_qty': material.mat_odr_qty,
                'mat_odr_brand': material.mat_odr_brand,
                'mat_odr_measurement': material.mat_odr_measurement,
                'mat_category': material.mat_category_id, 
            }
            return JsonResponse(data)
        except Material_Order.DoesNotExist:
            return JsonResponse({'error': 'Material not found'}, status=404)

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

    # Get the current status of the purchase order
    current_status = purchase_order.postat_id.postat_status

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

        # Status-specific field restrictions
        if current_status == 'Ongoing':
            # If the status is Ongoing, make all fields readonly except 'postat_id'
            for field in form.fields:
                if field != 'postat_id':  # Exclude 'postat_id' (status) from being readonly
                    form.fields[field].widget.attrs['readonly'] = True

        elif current_status == 'Done':
            # If the status is Done, make all fields readonly, including 'postat_id'
            for field in form.fields:
                form.fields[field].widget.attrs['readonly'] = True

        elif current_status == 'Waiting':
            # If the status is Waiting, all fields are editable, no restrictions
            for field in form.fields:
                form.fields[field].widget.attrs['readonly'] = False

        # Allow editing 'postat_id' only if status is 'Waiting' or 'Ongoing'
        if current_status in ['Waiting', 'Ongoing']:
            form.fields['postat_id'].widget.attrs['disabled'] = False

        # Disable 'postat_id' if the status is 'Done'
        if current_status == 'Done':
            form.fields['postat_id'].widget.attrs['readonly'] = True
            form.fields['postat_id'].widget.attrs['disabled'] = 'disabled'

    return render(request, 'finance/purchase_odr/edit_purchase_odr.html', {
        'form': form,
        'purchase_order': purchase_order,
        'related_materials': related_materials,  # Pass related materials to the template
    })

def delete_purchase_order(request, po_num):
    # Get the purchase order object by PO number
    purchase_order = get_object_or_404(Purchase_Order, po_num=po_num)
    
    # Check if the status is "Ongoing"
    if purchase_order.postat_id.postat_status == "Ongoing":
        messages.error(request, "Cannot delete a purchase order with 'Ongoing' status.")
        return redirect('finance:purchase_odr')

    # Delete the purchase order
    purchase_order.delete()
    messages.success(request, "Purchase order deleted successfully.")
    return redirect('finance:purchase_odr')
#____________________________________AR_____________________________________________________________

def ack_rep(request):
    receipts = Acknowledgment_Receipt.objects.prefetch_related(
        'material_approved_set' 
    )
    return render(request, 'finance/ack_rep/ack_rep.html', {'receipts': receipts})

def create_ack_rep(request):
    if request.method == 'POST':
        form = AcknowledgmentReceiptForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    # Save acknowledgment receipt
                    acknowledgment_receipt = form.save()

                    # Process and validate selected materials
                    selected_materials = json.loads(request.POST.get('selected_materials', '[]'))
                    for material_data in selected_materials:
                        material_approved = Material_Approved.objects.get(pk=material_data['id'])
                        material = material_approved.mat_approved_code  # Get linked Material object

                        # Check if enough quantity is available in inventory
                        if material.mat_quantity < material_approved.mat_approved_qty:
                            raise ValueError(f"Not enough stock for {material.mat_name}. Available: {material.mat_quantity}, Required: {material_approved.mat_approved_qty}")

                        # Deduct the approved quantity from inventory
                        material.mat_quantity -= material_approved.mat_approved_qty
                        material.save()

                        # Link material to acknowledgment receipt
                        material_approved.ar_num = acknowledgment_receipt
                        material_approved.save()

                    # Redirect on success
                    messages.success(request, "Acknowledgment receipt created successfully!")
                    return redirect('finance:ack_rep')

            except ValueError as e:
                messages.error(request, str(e))
                transaction.rollback()

            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                transaction.rollback()

        else:
            messages.error(request, "Invalid form data. Please check the inputs.")

    else:
        form = AcknowledgmentReceiptForm()

        # Filter materials to exclude those already linked to an acknowledgment receipt
        available_materials = Material_Approved.objects.filter(ar_num__isnull=True)  # Exclude materials with an acknowledgment receipt
        form.fields['item_approved_id'].queryset = available_materials

    return render(request, 'finance/ack_rep/create_ack_rep.html', {'form': form})

def logout_view(request):
    # Clear the session (log out the user)
    logout(request)
    
    # Redirect to the login page after logout
    return redirect('login:login')  # Make sure the 'login' URL name matches the one in your URL configuration