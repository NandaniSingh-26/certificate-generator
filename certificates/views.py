import csv
import os
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from .models import Certificate
from .forms import UploadCSVForm
from PIL import Image, ImageDraw, ImageFont
import qrcode

def generate_certificates(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            certificate_type = form.cleaned_data['certificate_type']
            csv_file = form.cleaned_data['csv_file']

            # Ensure the media directory exists
            media_dir = os.path.join('media')
            if not os.path.exists(media_dir):
                os.makedirs(media_dir)

            # Read the CSV file
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            certificates_paths = []  # List to store paths of generated certificates

            for row in reader:
                name = row['name']
                father_name = row['father_name']
                certificate_number = row['certificate_number']
                roll_no = row['roll_no']

                # Save certificate details in the database
                certificate = Certificate.objects.create(
                    name=name,
                    father_name=father_name,
                    certificate_number=certificate_number,
                    roll_no=roll_no,
                    certificate_type=certificate_type
                )

                # Generate QR code with verification URL
                qr_url = request.build_absolute_uri(certificate.get_absolute_url())
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_url)
                qr.make(fit=True)
                qr_img = qr.make_image(fill='black', back_color='white')
                qr_code_path = os.path.join(media_dir, f"qr_{certificate.id}.png")
                qr_img.save(qr_code_path)

                # Create certificate image based on the type
                if certificate_type == 'A':
                    template_path = 'certificates/templates/images/certificate-template.jpg'
                elif certificate_type == 'B':
                    template_path = 'certificates/templates/images/certificate-template2.jpg'
                else:
                    template_path = 'certificates/templates/images/certificate-template3.jpg'

                image = Image.open(template_path)
                draw = ImageDraw.Draw(image)
                font = ImageFont.truetype("arial.ttf", 40)

                # Add text to certificate
                draw.text((200, 150), f"Name: {name}", fill="black", font=font)
                draw.text((200, 200), f"Father Name: {father_name}", fill="black", font=font)
                draw.text((200, 250), f"Certificate Number: {certificate_number}", fill="black", font=font)
                draw.text((200, 300), f"Roll No: {roll_no}", fill="black", font=font)

                # Add QR code to certificate
                qr_image = Image.open(qr_code_path)
                qr_image = qr_image.resize((150, 150))
                image.paste(qr_image, (650, 450))

                # Save certificate
                certificate_path = os.path.join(media_dir, f"certificate_{certificate.id}.png")
                image.save(certificate_path)

                # Append path of generated certificate image
                certificates_paths.append(certificate_path)

            # Provide download links for each certificate
            download_links = [reverse('download_certificate', kwargs={'certificate_id': certificate.id}) for certificate in Certificate.objects.all()]

            return render(request, 'download.html', {'download_links': download_links})

    else:
        form = UploadCSVForm()

    return render(request, 'upload.html', {'form': form})

from django.shortcuts import render, get_object_or_404
from .models import Certificate

def verify_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)
    return render(request, 'verify.html', {'certificate': certificate})

import os
import zipfile
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Certificate

def download_certificate(request, certificate_id=None):
    if certificate_id:
        # Download individual certificate
        certificate = get_object_or_404(Certificate, id=certificate_id)
        certificate_path = os.path.join(settings.MEDIA_ROOT, f'certificate_{certificate.id}.png')

        if os.path.exists(certificate_path):
            with open(certificate_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="image/png")
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(certificate_path)
                return response
        else:
            raise Http404("Certificate image not found")
    else:
        # Download all certificates as ZIP
        certificates = Certificate.objects.all()
        zip_file_path = os.path.join(settings.MEDIA_ROOT, 'certificates.zip')

        try:
            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                for certificate in certificates:
                    certificate_path = os.path.join(settings.MEDIA_ROOT, f'certificate_{certificate.id}.png')
                    if os.path.exists(certificate_path):
                        zipf.write(certificate_path, f'certificate_{certificate.id}.png')

            # Serve the ZIP file for download
            with open(zip_file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/zip")
                response['Content-Disposition'] = 'attachment; filename=certificates.zip'
                return response
        except Exception as e:
            raise Http404("Failed to create ZIP file")
        
import os
import zipfile
from django.http import HttpResponse
from django.conf import settings
from certificates.models import Certificate

def download_all_certificates(request):
    certificates = Certificate.objects.all()
    zip_file_path = os.path.join(settings.MEDIA_ROOT, 'certificates.zip')

    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for certificate in certificates:
            certificate_path = os.path.join(settings.MEDIA_ROOT, f'certificate_{certificate.id}.png')
            if os.path.exists(certificate_path):
                zipf.write(certificate_path, f'certificate_{certificate.id}.png')

    with open(zip_file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename=certificates.zip'
        return response
    

