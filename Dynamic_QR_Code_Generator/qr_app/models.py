from django.db import models
from django.contrib.auth.models import User

class Dynamic_QR(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    short_id = models.CharField(max_length=20, unique=True)
    redirect_url = models.URLField()
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.short_id

class ScanLog(models.Model):
    qr = models.ForeignKey(Dynamic_QR, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"Scan for {self.qr.short_id} at {self.timestamp}"
