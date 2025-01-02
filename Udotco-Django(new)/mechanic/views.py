from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from shared.models import *
from .forms import *
from django.db.models import Q
from django.contrib.auth import logout
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from itertools import groupby
from operator import attrgetter

def dashboard(request):
    return render(request, 'mechanic/index.html')

# ___________________________________________JOB ORDER_________________________________________________________
# def joborder_list(request):
#     # Define statuses and statuses to disable
#     statuses = ['Pending', 'Ongoing', 'Done']
#     statuses_to_disable = ['Ongoing', 'Done']

#     # Extract filter parameters from the request
#     status_filter = request.GET.get('status', '')

#     # Initialize query filters
#     filters = Q()

#     # Apply filter for status
#     if status_filter:
#         filters &= Q(j_o_status=status_filter)

#     # Fetch filtered job orders
#     job_orders = JobOrder.objects.filter(filters).select_related('j_o_bus_unit_num')

#     # Check if any job order has the status "Pending"
#     has_pending_status = job_orders.filter(j_o_status="Pending").exists()

#     # Check if all job orders have the status "Done"
#     all_done = job_orders.filter(j_o_status='Done').count() == job_orders.count()

#     # Fetch employees from the Vehicle Maintenance Department
#     vehicle_maintenance_employees = Employee.objects.filter(dept_id__dept_name="Vehicle Maintenance Department")

#     # Render template with context
#     return render(request, 'mechanic/manage_jo/joborder_list.html', {
#         'statuses': statuses,
#         'job_orders': job_orders,
#         'statuses_to_disable': statuses_to_disable,
#         'employees': vehicle_maintenance_employees,
#         'has_pending_status': has_pending_status,  # Add this variable to the context
#         'all_done': all_done,  # Add this variable to the context
#     })

# @csrf_exempt
# def update_job_status(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         job_order_id = data.get("job_order_id")
#         next_status = data.get("next_status")
#         assigned_mechanic_id = data.get("assigned_mechanic")

#         try:
#             job_order = JobOrder.objects.get(j_o_number=job_order_id)

#             if next_status == "Ongoing" and not assigned_mechanic_id:
#                 return JsonResponse({"success": False, "error": "Mechanic must be assigned before updating to Ongoing."})

#             if next_status == "Ongoing" and assigned_mechanic_id:
#                 job_order.j_o_checked_by_id = assigned_mechanic_id

#             job_order.j_o_status = next_status
#             job_order.save()

#             return JsonResponse({"success": True, "message": f"Status updated to {next_status} successfully."})
#         except JobOrder.DoesNotExist:
#             return JsonResponse({"success": False, "error": "Job order not found."})
#     return JsonResponse({"success": False, "error": "Invalid request method."})

def joborder_list(request):
    # Define statuses and statuses to disable
    statuses = ['Pending', 'Ongoing', 'Done']
    statuses_to_disable = ['Ongoing', 'Done']

    # Extract filter parameters from the request
    status_filter = request.GET.get('status', '')

    # Initialize query
    filters = Q()

    # Apply filter for status
    if status_filter:
        filters &= Q(j_o_status=status_filter)

    # Fetch filtered job orders
    job_orders = JobOrder.objects.filter(filters).select_related('j_o_bus_unit_num')

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
        job_order_id = data.get("job_order_id")
        next_status = data.get("next_status")
        assigned_mechanic_id = data.get("assigned_mechanic")

        try:
            job_order = JobOrder.objects.get(j_o_number=job_order_id)

            if next_status == "Ongoing" and not assigned_mechanic_id:
                return JsonResponse({"success": False, "error": "Mechanic must be assigned before updating to Ongoing."})

            if next_status == "Ongoing" and assigned_mechanic_id:
                job_order.j_o_checked_by_id = assigned_mechanic_id

            job_order.j_o_status = next_status
            job_order.save()

            return JsonResponse({"success": True, "message": f"Status updated to {next_status} successfully."})
        except JobOrder.DoesNotExist:
            return JsonResponse({"success": False, "error": "Job order not found."})
    return JsonResponse({"success": False, "error": "Invalid request method."})


# ___________________________________________ITEM REQUEST__________________________________________________________

def fetch_materials(request):
    query = request.GET.get('q', '')  # Get search term from request
    materials = Material.objects.filter(mat_name__icontains=query)  # Search by mat_name

    # Format data for Select2
    data = []
    for material in materials:
        data.append({
            'id': material.mat_code,  # Use mat_code as the primary key
            'text': f"Category: {material.mat_category} | Material Name: {material.mat_name} | Qnty Available: {material.mat_quantity} "  # Display code and name
        })

    return JsonResponse({'results': data})


# def view_item_requests(request):
    # # Retrieve search query and selected category from GET parameters
    # search_query = request.GET.get('search', '')
    # selected_category = request.GET.get('category', '')

    # # Filter materials based on search query and category
    # item_requests = Material_Requested.objects.select_related(
    #     'mat_code__mat_category', 'item_req_num__bus_unit_num', 'item_req_num__item_req_approved_by'
    # ).all()

    # if search_query:
    #     item_requests = item_requests.filter(
    #         Q(mat_code__mat_name__icontains=search_query) |
    #         Q(mat_code__mat_brand__icontains=search_query) |
    #         Q(mat_code__mat_category__mat_name__icontains=search_query) |
    #         Q(item_req_num__item_req_description__icontains=search_query)
    #     )

    # if selected_category:
    #     item_requests = item_requests.filter(mat_code__mat_category__mat_category_id=selected_category)

    # # Fetch all categories for the dropdown filter
    # categories = Material_Category.objects.all()

    # context = {
    #     'item_requests': item_requests,
    #     'categories': categories,
    #     'search_query': search_query,
    #     'selected_category': selected_category,
    # }

    # return render(request, 'mechanic/item_req/view_req.html', context)

def view_item_requests(request):
    search_query = request.GET.get('search', '')
    selected_category = request.GET.get('category', '')

    # Fetch and filter item requests based on search query and category
    item_requests = Material_Requested.objects.select_related(
        'mat_code__mat_category', 'item_req_num__bus_unit_num', 'item_req_num__item_req_approved_by'
    ).all()

    if search_query:
        item_requests = item_requests.filter(
            Q(mat_code__mat_name__icontains=search_query) |
            Q(mat_code__mat_brand__icontains=search_query) |
            Q(mat_code__mat_category__mat_name__icontains=search_query) |
            Q(item_req_num__item_req_description__icontains=search_query)
        )

    if selected_category:
        item_requests = item_requests.filter(mat_code__mat_category__mat_category_id=selected_category)

    item_requests = item_requests.order_by('item_req_num__item_req_num')

    # Group item requests by item_req_num
    grouped_requests = groupby(item_requests, key=attrgetter('item_req_num'))

    # Create a list of unique item_req_num objects
    unique_item_requests = [
        {
            'item_req_num': key,
            'requests': list(group)
        }
        for key, group in grouped_requests
    ]

    # Fetch all categories for the dropdown filter
    categories = Material_Category.objects.all()

    context = {
        'unique_item_requests': unique_item_requests,
        'categories': categories,
        'search_query': search_query,
        'selected_category': selected_category,
    }

    return render(request, 'mechanic/item_req/view_req.html', context)



def create_item_req(request, job_order_id):
    # Fetch the related JobOrder
    job_order = get_object_or_404(JobOrder, pk=job_order_id)

    # Filter employees based on the "Vehicle Maintenance" department
    vehicle_maintenance_employees = Employee.objects.filter(dept_id__dept_name="Vehicle Maintenance Department")

    if request.method == "POST":
        form = ItemRequestForm(request.POST, job_order=job_order)  # Pass job_order as a kwarg

        # Retrieve materials from the POST request
        materials = json.loads(request.POST.get("materials", "[]"))
        assigned_mechanic = request.POST.get("item_req_approved_by")  # Get the selected mechanic

        if form.is_valid():
            # Set additional fields and save ItemRequest
            form.instance.item_req_date_requested = timezone.now()
            form.instance.job_order = job_order
            item_request = form.save(commit=False)  # Save the instance but don't commit yet

            # Ensure all required fields are set before saving
            item_request.save()  # Save the ItemRequest instance to the database

            # Create Material_Requested entries
            for material in materials:
                material_id = material["material_id"]
                quantity = int(material["quantity"])

                material_instance = get_object_or_404(Material, pk=material_id)

                # Assign the saved ItemRequest instance to the item_request field
                Material_Requested.objects.create(
                    mat_code=material_instance,
                    mat_req_qty=quantity,
                    item_req_num=item_request,  # Correctly set the item_req_num field here
                )

            # Update JobOrder status and assigned mechanic
            job_order.j_o_status = "Ongoing"
            if assigned_mechanic:
                job_order.j_o_checked_by = Employee.objects.get(emp_id=assigned_mechanic)
            job_order.save()

            # Return success response
            return JsonResponse({"success": True, "message": "Item request created successfully."})
        else:
            # Return form errors
            return JsonResponse({"success": False, "errors": form.errors})

    else:
        # Initialize the form with job_order
        form = ItemRequestForm(job_order=job_order)

    # Render the template
    return render(request, 'mechanic/item_req/create_item_req.html', {
        'job_order': job_order,
        'employees': vehicle_maintenance_employees,  # Filtered list of employees
        'form': form,
    })




# ___________________________________________INVENTORY__________________________________________________________

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

# ___________________________________________ACKNOWLEDGEMENT____________________________________________________
def ack_rec(request):
    return render(request, 'mechanic/ack_rec/ack_rec.html')

def logout_view(request):
    # Clear the session (log out the user)
    logout(request)
    
    # Redirect to the login page after logout
    return redirect('login:login')  # Make sure the 'login' URL name matches the one in your URL configuration



