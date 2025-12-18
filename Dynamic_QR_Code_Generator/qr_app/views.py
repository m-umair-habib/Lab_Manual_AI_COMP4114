import string
import random
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Dynamic_QR, ScanLog
from .forms import QRCodeForm, UpdateQRForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@login_required
def create_qr(request):
    if request.method == 'POST':
        form = QRCodeForm(request.POST)
        if form.is_valid():
            qr_obj = form.save(commit=False)
            qr_obj.user = request.user
            qr_obj.short_id = generate_short_id()

            # Generate QR image
            qr_code = qrcode.make(f"http://127.0.0.1:8000/r/{qr_obj.short_id}")
            buffer = BytesIO()
            qr_code.save(buffer, format='PNG')
            qr_obj.qr_image.save(f'{qr_obj.short_id}.png', ContentFile(buffer.getvalue()), save=True)

            qr_obj.save()
            return redirect('dashboard')
    else:
        form = QRCodeForm()

    return render(request, 'qr_app/create_qr.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def dashboard(request):
    user_qrs = Dynamic_QR.objects.filter(user=request.user)
    return render(request, 'qr_app/dashboard.html', {'qrs': user_qrs})

def redirect_qr(request, short_id):
    qr_obj = get_object_or_404(Dynamic_QR, short_id=short_id)

    ScanLog.objects.create(
        qr=qr_obj,
        user_agent=request.META.get('HTTP_USER_AGENT', 'unknown'),
        ip_address=request.META.get('REMOTE_ADDR')
    )

    return redirect(qr_obj.redirect_url)

@login_required
def qr_stats(request, short_id):
    qr_obj = get_object_or_404(Dynamic_QR, short_id=short_id, user=request.user)
    logs = ScanLog.objects.filter(qr=qr_obj)

    data = {
        'short_id': qr_obj.short_id,
        'redirect_url': qr_obj.redirect_url,
        'total_scans': logs.count(),
        'scans': [
            {'timestamp': l.timestamp, 'ip': l.ip_address, 'device': l.user_agent} for l in logs
        ]
    }
    return JsonResponse(data)

@login_required
def update_qr(request, short_id):
    # Ensure the QR belongs to the logged-in user
    qr_obj = get_object_or_404(Dynamic_QR, short_id=short_id, user=request.user)

    if request.method == 'POST':
        form = UpdateQRForm(request.POST, instance=qr_obj)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # redirect to dashboard after update
    else:
        form = UpdateQRForm(instance=qr_obj)

    return render(request, 'qr_app/update_qr.html', {'form': form, 'qr': qr_obj})

@login_required
def dashboard(request):
    qrs = Dynamic_QR.objects.filter(user=request.user)
    qr_data = []

    for qr in qrs:
        total_scans = ScanLog.objects.filter(qr=qr).count()
        qr_data.append({
            'short_id': qr.short_id,
            'redirect_url': qr.redirect_url,
            'qr_image_url': qr.qr_image.url if qr.qr_image else '',
            'total_scans': total_scans
        })

    return render(request, 'qr_app/dashboard.html', {'qr_data': qr_data})

@login_required
def dashboard(request):
    query = request.GET.get('q', '')  # Get search input
    qrs = Dynamic_QR.objects.filter(user=request.user)

    if query:
        qrs = qrs.filter(short_id__icontains=query) | qrs.filter(redirect_url__icontains=query)

    qr_data = []
    for qr in qrs:
        total_scans = ScanLog.objects.filter(qr=qr).count()
        qr_data.append({
            'short_id': qr.short_id,
            'redirect_url': qr.redirect_url,
            'qr_image_url': qr.qr_image.url if qr.qr_image else '',
            'total_scans': total_scans
        })

    return render(request, 'qr_app/dashboard.html', {'qr_data': qr_data, 'query': query})
