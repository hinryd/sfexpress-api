from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db import transaction
from .models import User, APIKey, CreditBalance, CreditTransaction, Location


# HTML Views for Dashboard

def home(request):
    """
    Home/Welcome page - publicly accessible
    """
    return render(request, 'api/home.html')


def register_view(request):
    """
    User registration page
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Validation
        if not all([username, email, password, password2]):
            messages.error(request, 'All fields are required')
            return render(request, 'api/register.html')

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'api/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'api/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'api/register.html')

        # Create user
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                # Create initial credit balance (100 credits for new users)
                credit_balance = CreditBalance.objects.create(
                    user=user,
                    credits=100,
                    total_earned=100
                )

                # Create transaction record
                CreditTransaction.objects.create(
                    user=user,
                    transaction_type='ADMIN_ADJUSTMENT',
                    amount=100,
                    balance_after=100,
                    description='Welcome bonus'
                )

            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')

        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'api/register.html')

    return render(request, 'api/register.html')


def login_view(request):
    """
    User login page
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not all([username, password]):
            messages.error(request, 'All fields are required')
            return render(request, 'api/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'api/login.html')


@login_required(login_url='login')
def dashboard(request):
    """
    User dashboard - shows credits, API keys, and transactions
    """
    # Get or create credit balance
    credit_balance, _ = CreditBalance.objects.get_or_create(user=request.user)

    # Get API keys
    api_keys = request.user.api_keys.filter(is_active=True).order_by('-created_at')

    # Get recent transactions
    transactions = request.user.credit_transactions.all()[:20]

    context = {
        'credit_balance': credit_balance,
        'api_keys': api_keys,
        'transactions': transactions,
    }

    return render(request, 'api/dashboard.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def create_api_key_dashboard(request):
    """
    Create a new API key from dashboard
    """
    key_name = request.POST.get('key_name', 'API Key')

    try:
        api_key = APIKey.objects.create(
            user=request.user,
            name=key_name
        )
        messages.success(request, f'API key "{key_name}" created successfully!')
    except Exception as e:
        messages.error(request, f'Error creating API key: {str(e)}')

    return redirect('dashboard')


@login_required(login_url='login')
@require_http_methods(["POST"])
def delete_api_key(request, key_id):
    """
    Delete an API key
    """
    try:
        api_key = APIKey.objects.get(id=key_id, user=request.user)
        key_name = api_key.name
        api_key.delete()
        messages.success(request, f'API key "{key_name}" deleted successfully!')
    except APIKey.DoesNotExist:
        messages.error(request, 'API key not found')
    except Exception as e:
        messages.error(request, f'Error deleting API key: {str(e)}')

    return redirect('dashboard')


def logout_view(request):
    """
    Logout user
    """
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('home')


# JSON API Endpoints (for API key authentication)

@require_http_methods(["GET"])
def locations(request):
    """
    Get SF Express locations - requires API key authentication
    Costs 5 credits per request
    """
    # Get credit balance
    credit_balance, _ = CreditBalance.objects.get_or_create(user=request.user)

    # Check if user has enough credits
    cost = 5
    if credit_balance.credits < cost:
        return JsonResponse({
            'error': 'Insufficient credits',
            'required': cost,
            'available': credit_balance.credits
        }, status=402)

    # Get query parameters
    location_type = request.GET.get('type')  # 'LOCKER' or 'SHOP'
    district = request.GET.get('district')
    search = request.GET.get('search')

    # Build query
    queryset = Location.objects.filter(is_active=True)

    if location_type:
        queryset = queryset.filter(location_type=location_type.upper())

    if district:
        queryset = queryset.filter(district__icontains=district)

    if search:
        queryset = queryset.filter(name__icontains=search)

    # Get locations
    locations_list = list(queryset.values(
        'id', 'location_type', 'name', 'address', 'district',
        'latitude', 'longitude', 'phone', 'opening_hours'
    ))

    # Deduct credits
    with transaction.atomic():
        if credit_balance.deduct_credits(cost):
            CreditTransaction.objects.create(
                user=request.user,
                transaction_type='API_CALL',
                amount=-cost,
                balance_after=credit_balance.credits,
                description=f'Location query: {len(locations_list)} results'
            )

    return JsonResponse({
        'count': len(locations_list),
        'locations': locations_list,
        'credits_used': cost,
        'credits_remaining': credit_balance.credits
    })
