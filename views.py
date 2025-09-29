from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from .forms import ImageUploadForm
from .models import UserImage, ShirtImage
from PIL import Image
import cv2
import numpy as np
import os
from django.conf import settings

def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            user_image = form.save()
            return redirect('swap_shirt', image_id=user_image.id)
    else:
        form = ImageUploadForm()
    return render(request, 'upload.html', {'form': form})

def swap_shirt(request, image_id):
    user_image = get_object_or_404(UserImage, id=image_id)
    shirts = ShirtImage.objects.all()
    error = None
    if request.method == 'POST':
        shirt_id = request.POST.get('shirt_id')
        shirt = get_object_or_404(ShirtImage, id=shirt_id)
        user_img_path = os.path.join(settings.MEDIA_ROOT, user_image.image.name)
        shirt_img_path = os.path.join(settings.MEDIA_ROOT, shirt.image.name)

        # Debug: print shirt image path and existence
        print(f"Trying to load shirt image from: {shirt_img_path}")
        if not os.path.exists(shirt_img_path):
            print(f"ERROR: Shirt image file does not exist: {shirt_img_path}")
        else:
            print(f"Shirt image file exists: {shirt_img_path}")

        user_img = cv2.imread(user_img_path)
        if user_img is None or user_img.size == 0:
            error = "User image not found or empty."
        else:
            shirt_img = cv2.imread(shirt_img_path, cv2.IMREAD_UNCHANGED)
            if shirt_img is None or shirt_img.size == 0:
                print(f"ERROR: Could not load shirt image with OpenCV: {shirt_img_path}")
                return render(request, 'swap.html', {
                    'user_image': user_image,
                    'shirts': shirts,
                    'error': "Shirt image not found or empty."
                })
            else:
                try:
                    shirt_img = cv2.resize(shirt_img, (user_img.shape[1], user_img.shape[0]))
                    if len(shirt_img.shape) == 3 and shirt_img.shape[2] == 4:
                        shirt_rgb = shirt_img[:, :, :3]
                        alpha_mask = shirt_img[:, :, 3] / 255.0
                        alpha_mask = np.clip(alpha_mask, 0, 1)
                        alpha_mask_3c = np.repeat(alpha_mask[:, :, np.newaxis], 3, axis=2)
                        result = (shirt_rgb * alpha_mask_3c + user_img * (1 - alpha_mask_3c)).astype(np.uint8)
                    elif len(shirt_img.shape) == 3 and shirt_img.shape[2] == 3:
                        result = cv2.addWeighted(user_img, 0.5, shirt_img, 0.5, 0)
                    else:
                        result = user_img
                    # Ensure results directory exists
                    result_dir = os.path.join(settings.MEDIA_ROOT, 'results')
                    os.makedirs(result_dir, exist_ok=True)
                    result_path = os.path.join(result_dir, f'result_{image_id}.png')
                    cv2.imwrite(result_path, result)
                    request.session['result_path'] = f'results/result_{image_id}.png'
                    return render(request, 'result.html', {'user_image': user_image, 'result_path': f'media/results/result_{image_id}.png'})
                except cv2.error as e:
                    error = "Error resizing shirt image."
    return render(request, 'swap.html', {
        'user_image': user_image,
        'shirts': shirts,
        'error': error
    })

def download_result(request):
    result_path = request.session.get('result_path')
    if result_path:
        full_path = os.path.join(settings.MEDIA_ROOT, result_path)
        with open(full_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename=result_image.png'
            return response
    return redirect('upload_image')
