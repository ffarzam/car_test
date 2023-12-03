from datetime import timedelta

from django.db import transaction
from django.http import FileResponse, StreamingHttpResponse, HttpResponse

from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.authentication import AccessTokenAuthentication
from accounts.tasks import send_mail
from car.models import Car, File, Part
from car.serializer import PartsSerializer, FileSerializer, CarSerializer
import io
import zipfile
from wsgiref.util import FileWrapper

from car.utils import minio_client


# Create your views here.


class CarPartsListView(APIView):
    serializer_class = PartsSerializer

    def get(self, request, car_id):
        car = Car.objects.get(id=car_id)
        parts = car.parts.all()
        serialized_data = self.serializer_class(parts, many=True)
        return Response(serialized_data.data, status=status.HTTP_200_OK)


class FileUploadView(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def put(self, request, car_model, part_name):
        user = request.user
        # TODO: check if celery improve performance or not
        file_obj = request.FILES
        file_objs = [File(file=request.FILES[k]) for k, v in file_obj.items()]
        try:
            with transaction.atomic():
                files = File.objects.bulk_create(file_objs)
                part, _ = Part.objects.get_or_create(part_name=part_name)
                part.part_file.add(*files)
                car = Car.objects.get(model=car_model)
                car.parts.add(part)
        except Exception as e:
            for file in files:
                minio_client.remove_object('local-media', file.file.name)
            raise e

        file_id_list = []
        for file in files:

            file_id_list.append(file.id)
        send_mail.delay(user.email, file_id_list, car.id, part.id, request.unique_id)

        return Response(CarSerializer(car).data, status=status.HTTP_204_NO_CONTENT)


class FileDownloadView(APIView):

    def get(self, request, file_id):
        file_obj = File.objects.get(id=file_id)
        return FileResponse(file_obj.file.open(), as_attachment=True, filename=file_obj.file.name)


class PartFilesDownloadView(APIView):

    def get(self, request, part_id):
        part = Part.objects.prefetch_related("part_file").get(id=part_id)
        files = part.part_file.all()

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
            for file_obj in files:
                file_data = minio_client.get_object('local-media', file_obj.file.name).read()
                zip_file.writestr(f"{part.part_name}_{file_obj.file.name}", file_data)

        zip_buffer.seek(0)
        zip_buffer.getvalue()
        response = StreamingHttpResponse(FileWrapper(zip_buffer), content_type="application/zip", )
        response['Content-Disposition'] = f'attachment; filename={part.part_name}.zip'
        return response


class CarPartsFilesDownloadView(APIView):

    def get(self, request, part_id):
        car = Car.objects.prefetch_related("parts__part_file").get(id=part_id)
        parts = car.parts.all()

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
            for part_obj in parts:
                files = part_obj.part_file.all()
                for file_obj in files:
                    file_data = minio_client.get_object('local-media', file_obj.file.name).read()
                    zip_file.writestr(f"{part_obj.part_name}_{file_obj.file.name}", file_data)

        zip_buffer.seek(0)
        zip_buffer.getvalue()
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={car.model}.zip'
        return response
