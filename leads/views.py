from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import LinkedInLead


class LinkedInLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkedInLead
        fields = [
            "id", "full_name", "email", "phone", "linkedin_url",
            "job_title", "company", "city", "country",
            "engagement_type", "post_url", "status", "notes",
            "dm_sent", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


@api_view(["POST"])
def create_lead(request):
    serializer = LinkedInLeadSerializer(data=request.data)
    if serializer.is_valid():
        lead = serializer.save()
        return Response(
            {"status": "ok", "id": lead.id, "name": lead.full_name},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def list_leads(request):
    lead_status = request.query_params.get("status")
    engagement = request.query_params.get("engagement_type")

    qs = LinkedInLead.objects.all()
    if lead_status:
        qs = qs.filter(status=lead_status)
    if engagement:
        qs = qs.filter(engagement_type=engagement)

    serializer = LinkedInLeadSerializer(qs, many=True)
    return Response({"count": qs.count(), "leads": serializer.data})


@api_view(["PATCH"])
def update_lead_status(request, pk):
    try:
        lead = LinkedInLead.objects.get(pk=pk)
    except LinkedInLead.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    allowed_fields = {"status", "notes", "dm_sent", "dm_sent_at"}
    data = {k: v for k, v in request.data.items() if k in allowed_fields}
    serializer = LinkedInLeadSerializer(lead, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
