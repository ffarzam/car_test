from rest_framework import serializers

from car.models import Part, File, Car


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"

        # TODO: Check why this doesn't work

        # def get_fields(self):
        #     fields = super().get_fields()
        #     exclude_fields = self.context.get('exclude_fields', [])
        #     for field in exclude_fields:
        #         fields.pop(field, default=None)
        #
        #     return fields


class PartsSerializer(serializers.ModelSerializer):
    part_file = FileSerializer(read_only=True, many=True)

    class Meta:
        model = Part
        fields = ('part_name', 'part_file',)


class CarSerializer(serializers.ModelSerializer):
    parts = PartsSerializer(read_only=True, many=True)

    class Meta:
        model = Car
        fields = "__all__"
