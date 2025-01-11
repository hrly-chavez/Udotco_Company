from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from shared.models import *
from .forms import *
from django.db.models import Q
from django.contrib.auth import logout
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from collections import defaultdict 
from operator import itemgetter
from django.utils.dateparse import parse_date
from django.core.exceptions import ValidationError  
from django.contrib import messages

 
# __________________________________________JOB ORDER________________________________________________________

def joborder_list(request): 
    # Define statuses and statuses to disable
    statuses = ['Pending', 'Ongoing', 'Done']
    statuses_to_disable = ['Done']

    # Filter by status if provided
    status_filter = request.GET.get('status', '')

    # Apply filters
    filters = Q()
    if status_filter:
        filters &= Q(j_o_status=status_filter)

    # Sort job orders by status and then by job order number
    pending_jobs = JobOrder.objects.filter(filters & Q(j_o_status="Pending")).order_by('j_o_number')
    ongoing_jobs = JobOrder.objects.filter(filters & Q(j_o_status="Ongoing")).order_by('j_o_number')
    completed_jobs = JobOrder.objects.filter(filters & Q(j_o_status="Done")).order_by('j_o_number')

    # Combine results
    job_orders = list(pending_jobs) + list(ongoing_jobs) + list(completed_jobs)

    # Fetch employees from the Vehicle Maintenance Department
    vehicle_maintenance_employees = Employee.objects.filter(dept_id__dept_name="Vehicle Maintenance Department")

    # Render template with context
    return render(request, 'mechanic/manage_jo/joborder_list.html', {
        'statuses': statuses,
        'job_orders': job_orders,
        'statuses_to_disable': statuses_to_disable,
        'employees': vehicle_maintenance_employees,
    })

@csrf_exempt
def update_job_status(request):
    if request.method == "POST":
        data = json.loads(request.body)
        job_order_id = data.get('job_order_id')
        next_status = data.get('next_status')
        assigned_mechanic = data.get('assigned_mechanic', None)

        try:
            job_order = JobOrder.objects.get(j_o_number=job_order_id)

            # Assign mechanic if applicable
            if next_status == "Ongoing" and assigned_mechanic:
                mechanic = Employee.objects.get(emp_id=assigned_mechanic)
                job_order.j_o_checked_by = mechanic

            # Update status and date completed
            job_order.j_o_status = next_status
            if next_status == "Done":
                job_order.j_o_date_completed = now()
            
            job_order.save()
            return JsonResponse({'success': True, 'message': 'Status updated successfully.'})
        except JobOrder.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Job Order not found.'})
        except Employee.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Mechanic not found.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def assign_mat_used(request, item_req_num):
    # Fetch the item request details
    item_request = get_object_or_404(Item_Request, item_req_num=item_req_num)

    # Fetch related materials
    materials = Material_Requested.objects.filter(item_req_num=item_request).select_related(
        'mat_code', 'mat_code__mat_category'
    )

    # Check if materials have been assigned already
    materials_assigned = all(material.mat_req_status == 'Approved' for material in materials)

    context = {
        'job_order': item_request.job_order,
        'materials': materials,
        'item_request': item_request,
        'materials_assigned': materials_assigned,  # Add this flag
    }

    return render(request, 'mechanic/manage_jo/assign_mat_used.html', context)


def assign_material_to_job_order(request, item_req_num):
    if request.method == "POST":
        # Fetch the item request and associated materials
        item_request = get_object_or_404(Item_Request, item_req_num=item_req_num)
        materials = Material_Requested.objects.filter(item_req_num=item_request)

        # Get the job order associated with the item request
        job_order = item_request.job_order
        if not job_order:
            messages.error(request, "No job order is associated with this item request.")
            return redirect('mechanic:assign_mat_used', item_req_num=item_req_num)

        try:
            # Check if any materials have a 'Pending' status
            for material in materials:
                if material.mat_req_status == 'Pending':
                    messages.error(request, f"Cannot assign material(s) because it is still Pending.")
                    return redirect('mechanic:assign_mat_used', item_req_num=item_req_num)

                # Assign materials to the job order if status is not 'Pending'
                Material_Used.objects.create(
                    mat_used_name=material.mat_code.mat_name,
                    mat_used_qty=material.mat_req_qty,
                    mat_used_brand=material.mat_code.mat_brand,
                    mat_used_measurement=material.mat_code.mat_measurement,
                )
                material.mat_req_status = 'Approved'  # Set to 'Approved' for successful assignment
                material.save()

            messages.success(request, "Materials have been successfully assigned to the job order.")
        except Exception as e:
            messages.error(request, f"An error occurred while assigning materials: {e}")
        
        return redirect('mechanic:assign_mat_used', item_req_num=item_req_num)

    messages.error(request, "Invalid request method.")
    return redirect('mechanic:assign_mat_used', item_req_num=item_req_num)




# __________________________________________ITEM REQUEST_________________________________________________________
    

def fetch_approved_materials(request):
    """
    Fetch materials with approved status from the Material_Requested model for the select2 dropdown.
    """
    if request.method == "GET":
        query = request.GET.get('q', '')

        # Fetch approved materials
        materials = Material_Requested.objects.filter(mat_req_status="Approved").select_related('mat_code')

        if query:
            materials = materials.filter(mat_code__mat_name__icontains=query)

        
        # Format results for select2
        results = [
            {
                'id': material.mat_code_id,
                'text': material.mat_code.mat_name,
                'mat_req_qty': material.mat_req_qty,
            }
            for material in materials
        ]
        return JsonResponse({'results': results})
    
def fetch_materials(request):
    material_id = request.GET.get("material_id")
    query = request.GET.get("q", "")  # Get search term from request

    if material_id:
        # Handle fetching details for a specific material
        try:
            material = Material.objects.get(pk=material_id)
            return JsonResponse({
                "mat_max_request": material.mat_max_request,
                "mat_qty_available": material.mat_quantity,
            })
        except Material.DoesNotExist:
            return JsonResponse({"error": "Material does not exist."}, status=404)

    # Handle search functionality for Select2 dropdown
    materials = Material.objects.filter(mat_name__icontains=query)  # Search by mat_name
    data = []
    for material in materials:
        data.append({
            'id': material.mat_code,  # Use mat_code as the primary key
            'text': f"Category: {material.mat_category} | Material Name: {material.mat_name} | Qnty Available: {material.mat_quantity}"
        })

    return JsonResponse({'results': data})

def view_item_requests(request):
    item_req_date_requested = request.GET.get('item_req_date_requested', '').strip()

    # Fetch all item requests with related fields
    item_requests = Material_Requested.objects.select_related(
        'mat_code__mat_category',
        'item_req_num__bus_unit_num',
        'item_req_num__item_req_approved_by',
        'item_req_num__job_order'  # Include JobOrder relationship
    ).order_by('-item_req_num__item_req_date_requested')

    # Apply date filter if provided
    if item_req_date_requested:
        req_date = parse_date(item_req_date_requested)
        if req_date:
            start_of_day = datetime.combine(req_date, datetime.min.time())
            end_of_day = datetime.combine(req_date, datetime.max.time())
            item_requests = item_requests.filter(
                item_req_num__item_req_date_requested__range=(start_of_day, end_of_day)
            )

    # Group by item_req_num
    grouped_requests = defaultdict(lambda: {'details': None, 'items': []})
    for item in item_requests:
        item_req_num = item.item_req_num.item_req_num
        grouped_requests[item_req_num]['details'] = item
        grouped_requests[item_req_num]['items'].append(item)

    # Sort grouped requests
    sorted_grouped_requests = dict(sorted(grouped_requests.items(), key=itemgetter(0), reverse=True))

    context = {
        'grouped_requests': sorted_grouped_requests,
        'item_req_date_requested': item_req_date_requested,
    }

    return render(request, 'mechanic/item_req/view_req.html', context)


def create_item_req(request, job_order_id):
    job_order = get_object_or_404(JobOrder, pk=job_order_id)
    vehicle_maintenance_employees = Employee.objects.filter(dept_id__dept_name="Vehicle Maintenance Department")

    if request.method == "POST":
        form = ItemRequestForm(request.POST, job_order=job_order)
        materials = json.loads(request.POST.get("materials", "[]"))

        if form.is_valid():
            try:
                # Check material quantities
                for material in materials:
                    material_id = material["material_id"]
                    quantity = int(material["quantity"])

                    material_instance = get_object_or_404(Material, pk=material_id)

                    if quantity > material_instance.mat_quantity:
                        raise ValidationError(
                            f"Requested quantity for {material_instance.mat_name} exceeds available stock ({material_instance.mat_quantity})."
                        )
                    if quantity > material_instance.mat_max_request:
                        raise ValidationError(
                            f"Requested quantity for {material_instance.mat_name} exceeds maximum requestable limit ({material_instance.mat_max_request})."
                        )

                # Save item request
                form.instance.item_req_date_requested = timezone.now()
                form.instance.job_order = job_order
                item_request = form.save()

                # Save Material_Requested
                for material in materials:
                    Material_Requested.objects.create(
                        mat_code=Material.objects.get(pk=material["material_id"]),
                        mat_req_qty=int(material["quantity"]),
                        item_req_num=item_request,
                    )

                # Update JobOrder
                job_order.j_o_status = "Ongoing"
                if request.POST.get("item_req_approved_by"):
                    job_order.j_o_checked_by = Employee.objects.get(emp_id=request.POST["item_req_approved_by"])
                job_order.save()

                return redirect('mechanic:joborder_list')

            except ValidationError as e:
                return JsonResponse({"success": False, "errors": str(e)})

        else:
            return JsonResponse({"success": False, "errors": form.errors})

    else:
        form = ItemRequestForm(job_order=job_order)

    return render(request, 'mechanic/item_req/create_item_req.html', {
        'job_order': job_order,
        'employees': vehicle_maintenance_employees,
        'form': form,
    })



# __________________________________________INVENTORY_________________________________________________________

def inventory(request):
    search_query = request.GET.get('search', '')
    selected_category = request.GET.get('category', '')

    # Fetch all categories for the dropdown
    categories = Material_Category.objects.values('mat_category_id', 'mat_name').distinct()

    # Filter materials based on search and category
    materials = Material.objects.all()
    if search_query:
        materials = materials.filter(mat_name__icontains=search_query) 
    if selected_category:
        materials = materials.filter(mat_category_id=selected_category)

    return render(request, 'mechanic/inventory/inventory.html', {
        'materials': materials,
        'categories': categories,
        'search_query': search_query,
        'selected_category': selected_category,
    })

# __________________________________________ACKNOWLEDGEMENT___________________________________________________
def ack_rec(request):
    return render(request, 'mechanic/ack_rec/ack_rec.html')

def logout_view(request):
    # Clear the session (log out the user)
    logout(request)
    
    # Redirect to the login page after logout
    return redirect('login:login')  # Make sure the 'login' URL name matches the one in your URL configuration