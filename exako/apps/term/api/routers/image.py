from django.shortcuts import get_object_or_404
from ninja import File, Router, UploadedFile

from exako.apps.core import schema as core_schema
from exako.apps.core.permissions import is_admin, permission_required
from exako.apps.term.api import schema
from exako.apps.term.models import TermImage
from exako.apps.user.auth.token import AuthBearer

image_router = Router()


@image_router.post(
    path='',
    response={
        201: schema.TermImageView,
        401: core_schema.NotAuthenticated,
        403: core_schema.PermissionDenied,
        404: core_schema.NotAuthenticated,
    },
    summary='Criação de imagem para termo.',
    description='Endpoint utilizado para enviar imagens que serão associadas com termos existentes.',
    auth=AuthBearer(),
)
@permission_required([is_admin])
def create_term_image(
    request,
    exercise_schema: schema.TermImageSchema,
    image: UploadedFile = File(...),
):
    return 201, TermImage.objects.create(image=image, **exercise_schema.model_dump())


@image_router.get(
    path='/{term_id}',
    response={
        200: schema.TermImageView,
        404: core_schema.NotAuthenticated,
    },
    summary='Criação de imagem para termo.',
    description='Endpoint utilizado para enviar imagens que serão associadas com termos existentes.',
)
def get_term_image(request, term_id: int):
    return get_object_or_404(TermImage, term_id=term_id)
