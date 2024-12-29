


def create_customer(request):
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST, request.FILES)

        if customer_form.is_valid():
            # Extract user data from the request
            email = request.POST.get('email')        # Get email from the form
            password = request.POST.get('password')  # Get password from the form

            # Check if the user already exists
            if user_exists(email):
                messages.error(request, f'A user with this email {email} already exists.' )
                return render(request, 'forms/customer.html', {
                    'customer_form': customer_form,
                })

            # Create the user
            user = User(email=email)
            user.set_password(password)  # Set the password using set_password
            try:
                # user.full_clean()  # Validate the user instance
                user.save()  # Save the user
            except Exception as e:
                print(e)
                messages.error(request, f'Error creating user: {str(e)}')
                return render(request, 'create_customer.html')

            # Authenticate the user
            authenticated_user = authenticate(request, username=email, password=password)

            try:
                customer = customer_form.save(commit=False)
                customer.user = authenticated_user  # Link the authenticated user
                account = create_standalone()
                customer.account = account  # Link the account
                customer.save()
            except Exception as e:
                messages.error(request, 'Error creating customer: ' + str(e))
                print(e)
                return render(request, 'forms/customer.html', {
                    'customer_form': customer_form,
                    'error': 'User  authentication failed.'
                })

            return redirect('sign_out')  
            # if authenticated_user:
                
            #     # Now create the customer with the user and account
            #     try:
            #         customer = customer_form.save(commit=False)
            #         customer.user = authenticated_user  # Link the authenticated user
            #         account = create_standalone()
            #         customer.account = account  # Link the account
            #         customer.save()
            #     except Exception as e:
            #         messages.error(request, 'Error creating customer: ' + str(e))
            #         print(e)
            #         return render(request, 'customer.html', {
            #             'customer_form': customer_form,
            #             'error': 'User  authentication failed.'
            #         })

            #     return redirect('logout')  # Replace with your success URL
        else:
            # Handle authentication failure
            print("authentication error")
            return render(request, 'forms/customer.html', {
                'customer_form': customer_form,
                'error': 'User  authentication failed.'
            })
    else:
        customer_form = CustomerForm()
    
    return render(request, 'forms/customer.html', {
        'customer_form': customer_form,
    })
