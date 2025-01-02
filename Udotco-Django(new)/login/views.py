from django.shortcuts import render, redirect
from django.contrib import messages
from shared.models import *

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Fetch the account with the given username
            account = Accounts.objects.select_related('user_id__dept_id').get(username=username)

            # Check if the provided password matches the stored password
            if password == account.password:
                # Save the user ID in the session for authentication
                request.session['user_id'] = account.user_id.emp_id

                # Get the department name
                department = account.user_id.dept_id.dept_name.lower()

                # Redirect based on department and show success message
                if department == 'finance department':
                    messages.success(request, "Congratulations! You have logged in successfully.")
                    return redirect('finance:mechanic_req')
                elif department == 'vehicle maintenance department':
                    messages.success(request, "Congratulations! You have logged in successfully.")
                    return redirect('mechanic:joborder_list')
                elif department == 'i.t. department':
                    messages.success(request, "Congratulations! You have logged in successfully.")
                    return redirect('it:department')
                elif department == 'transportation department':
                    messages.success(request, "Congratulations! You have logged in successfully.")
                    return redirect('driver:driver_request')
                else:
                    messages.error(request, "Invalid department.")
            else:
                # Password mismatch
                messages.error(request, "Invalid username or password.")
        except Accounts.DoesNotExist:
            # Account does not exist
            messages.error(request, "Account does not exist.")
        except AttributeError as e:
            # Account setup incomplete
            messages.error(request, "Account setup is incomplete. Please contact support.")

    return render(request, 'login_ui/login.html')

