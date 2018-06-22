from __future__ import unicode_literals

import re
import json
import logging

from django.conf import settings
from django.core.files import File
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.static import serve

from froide.helper.utils import render_400, render_403
from froide.helper.redaction import redact_file

from ..models import FoiRequest, FoiMessage, FoiAttachment
from ..auth import (can_read_foirequest, can_read_foirequest_authenticated,
                    can_write_foirequest, is_attachment_public)


logger = logging.getLogger(__name__)

X_ACCEL_REDIRECT_PREFIX = getattr(settings, 'X_ACCEL_REDIRECT_PREFIX', '')


def has_attachment_access(request, foirequest, attachment):
    if not can_read_foirequest(foirequest, request):
        return False
    if not attachment.approved:
        # allow only approved attachments to be read
        # do not allow anonymous authentication here
        allowed = can_read_foirequest_authenticated(
            foirequest, request, allow_code=False
        )
        if not allowed:
            return False
    return True


def show_attachment(request, slug, message_id, attachment_name):
    foirequest = get_object_or_404(FoiRequest, slug=slug)
    message = get_object_or_404(FoiMessage, id=int(message_id),
                                request=foirequest)
    attachment = get_object_or_404(FoiAttachment, belongs_to=message,
                                   name=attachment_name)
    if not has_attachment_access(request, foirequest, attachment):
        return render_403(request)
    return render(request, 'foirequest/attachment/show.html', {
        'attachment': attachment,
        'message': message,
        'foirequest': foirequest
    })


@require_POST
def approve_attachment(request, slug, attachment):
    foirequest = get_object_or_404(FoiRequest, slug=slug)

    if not can_write_foirequest(foirequest, request):
        return render_403(request)
    att = get_object_or_404(FoiAttachment, id=int(attachment))
    if not att.can_approve and not request.user.is_staff:
        return render_403(request)
    att.approve_and_save()
    messages.add_message(request, messages.SUCCESS,
            _('Attachment approved.'))
    if request.is_ajax():
        return render(
            request, 'foirequest/snippets/attachment.html',
            {'attachment': att, 'object': foirequest}
        )
    return redirect(att.get_anchor_url())


@require_POST
def create_document(request, slug, attachment):
    foirequest = get_object_or_404(FoiRequest, slug=slug)

    if not can_write_foirequest(foirequest, request):
        return render_403(request)
    att = get_object_or_404(FoiAttachment, id=int(attachment))
    if not att.can_approve and not request.user.is_staff:
        return render_403(request)

    if att.document is not None:
        return render_400(request)

    att.create_document()
    messages.add_message(request, messages.SUCCESS,
            _('Document created.'))

    if request.is_ajax():
        return render(
            request, 'foirequest/snippets/attachment.html',
            {'attachment': att, 'object': foirequest}
        )
    return redirect(att.get_anchor_url())


def auth_message_attachment(request, message_id, attachment_name):
    '''
    nginx auth view
    '''
    message = get_object_or_404(FoiMessage, id=int(message_id))
    attachment = get_object_or_404(FoiAttachment, belongs_to=message,
        name=attachment_name)
    foirequest = message.request

    if settings.FOI_MEDIA_TOKENS:
        return auth_attachment_with_token(request, foirequest, attachment)

    if not has_attachment_access(request, foirequest, attachment):
        return render_403(request)

    if not settings.USE_X_ACCEL_REDIRECT:
        if not settings.DEBUG:
            logger.warn('Django should not serve files in production!')
        return serve(request, attachment.file.path, settings.MEDIA_ROOT)

    return send_attachment_file(attachment)


def auth_attachment_with_token(request, foirequest, attachment):
    if request.get_host() not in settings.SITE_URL:
        # media domain internal NGINX check
        result = attachment.check_token(request)
        if not result:
            if result is None:
                # Redirect back to get new signature
                return redirect(attachment.get_absolute_domain_file_url())
            return render_403(request)
        return send_attachment_file(attachment)
    else:
        # main domain: always deny or redirect
        # in order not to render content on main domain
        if is_attachment_public(foirequest, attachment):
            url = attachment.get_absolute_file_url(authenticated=False)
            return redirect(settings.FOI_MEDIA_DOMAIN + url)

        if not has_attachment_access(request, foirequest, attachment):
            # Deny access early
            return render_403(request)

        url = attachment.get_absolute_file_url(authenticated=True)
        return redirect(settings.FOI_MEDIA_DOMAIN + url)


def send_attachment_file(attachment):
    response = HttpResponse()
    response['Content-Type'] = ""
    response['X-Accel-Redirect'] = X_ACCEL_REDIRECT_PREFIX + attachment.get_internal_url()
    return response


def redact_attachment(request, slug, attachment_id):
    foirequest = get_object_or_404(FoiRequest, slug=slug)
    if not can_write_foirequest(foirequest, request):
        return render_403(request)
    attachment = get_object_or_404(FoiAttachment, pk=int(attachment_id),
            belongs_to__request=foirequest)
    already = None
    if attachment.redacted:
        already = attachment.redacted
    elif attachment.is_redacted:
        already = attachment

    if request.method == 'POST':
        # Python 2.7/3.5 requires str for json.loads
        instructions = json.loads(request.body.decode('utf-8'))
        path = redact_file(attachment.file.file, instructions)
        if path is None:
            return render_400(request)
        name = attachment.name.rsplit('.', 1)[0]
        name = re.sub(r'[^\w\.\-]', '', name)
        pdf_file = File(open(path, 'rb'))
        if already:
            att = already
        else:
            att = FoiAttachment(
                belongs_to=attachment.belongs_to,
                name=_('%s_redacted.pdf') % name,
                is_redacted=True,
                filetype='application/pdf',
                approved=True,
                can_approve=True
            )
        att.file = pdf_file
        att.size = pdf_file.size
        att.approve_and_save()
        if not attachment.is_redacted:
            attachment.redacted = att
            attachment.can_approve = False
            attachment.approved = False
            attachment.save()
        return JsonResponse({'url': att.get_anchor_url()})
    return render(request, 'foirequest/redact.html', {
        'foirequest': foirequest,
        'attachment': attachment
    })
