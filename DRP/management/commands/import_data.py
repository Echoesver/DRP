"""Import data from your target main server."""
from django.utils.encoding import smart_str
from django.contrib.auth.models import User
from django.core import serializers
from django.core.management.base import BaseCommand
from decimal import Decimal, getcontext, InvalidOperation
import requests
from django.conf import settings
import DRP
import logging

logger = logging.getLogger('DRP.management')


class Command(BaseCommand):
    """Import data from your target main server."""

    help = 'synchronises database with the main server'

    def handle(self, reaction_limit=None, *args, **kwargs):
        """Handle the command call."""
        DRP.models.CompoundQuantity.objects.all().delete()
        DRP.models.Compound.objects.all().delete()
        DRP.models.CompoundRole.objects.all().delete()
        DRP.models.ChemicalClass.objects.all().delete()
        DRP.models.ConfirmationCode.objects.all().delete()
        DRP.models.LicenseAgreement.objects.all()
        DRP.models.License.objects.all().delete()
        DRP.models.StatsModel.objects.all().delete()
        DRP.models.DataSet.objects.all().delete()
        DRP.models.DataSet.objects.all().delete()
        DRP.models.PerformedReaction.objects.all().delete()
        DRP.models.CatMolDescriptorValue.objects.all().delete()
        DRP.models.BoolMolDescriptorValue.objects.all().delete()
        DRP.models.NumMolDescriptorValue.objects.all().delete()
        DRP.models.OrdMolDescriptorValue.objects.all().delete()
        DRP.models.LabGroup.objects.all().delete()
        DRP.models.Descriptor.objects.all().delete()
        User.objects.all().delete()
        s = requests.Session()
        s.get(settings.MAIN_SERVER + '/login.html')
        r = s.post(settings.MAIN_SERVER + '/login.html', data={'username': settings.MAIN_SERVER_USER,
                                                               'password': settings.MAIN_SERVER_PASS, 'csrfmiddlewaretoken': s.cookies.get_dict()['csrftoken']}, headers={'referer': settings.MAIN_SERVER + '/login.html'})
        if r.status_code == requests.codes.ok:
            apiUrl = settings.MAIN_SERVER + '/database/import/apiv1/'
            if reaction_limit is None:
                data = {}
            else:
                data = {'limit': int(reaction_limit)}

            r = s.get(apiUrl + 'users.xml', params=data)
            for u in serializers.deserialize('xml', smart_str(r.text)):
                u.save()

            user = User.objects.get(username=settings.MAIN_SERVER_USER)
            user.set_password(settings.MAIN_SERVER_PASS)
            user.save()

            r = s.get(apiUrl + 'licenses.xml', params=data)
            for l in serializers.deserialize('xml', smart_str(r.text)):
                l.save()

            r = s.get(apiUrl + 'license_agreements.xml', params=data)
            for la in serializers.deserialize('xml', smart_str(r.text)):
                la.save()

            r = s.get(apiUrl + 'lab_groups.xml', params=data)
            for lg in serializers.deserialize('xml', smart_str(r.text)):
                lg.save()

            r = s.get(apiUrl + 'chemical_classes.xml', params=data)
            for cc in serializers.deserialize('xml', smart_str(r.text)):
                cc.save()

            r = s.get(apiUrl + 'compounds.xml', params=data)
            for c in serializers.deserialize('xml', smart_str(r.text)):
                c.save()

            r = s.get(apiUrl + 'compound_roles.xml', params=data)
            for cr in serializers.deserialize('xml', smart_str(r.text)):
                cr.save()

            r = s.get(apiUrl + 'reactions.xml', params=data)
            for rr in serializers.deserialize('xml', smart_str(r.text)):
                rr.object.calcDescriptors = False
                rr.save()

            r = s.get(apiUrl + 'performed_reactions.xml', params=data)
            for pr in serializers.deserialize('xml', smart_str(r.text)):
                pr.object.calcDescriptors = False
                pr.object.duplicateOf = None
                pr.save()

            for pr in serializers.deserialize('xml', smart_str(r.text)):
                pr2 = DRP.models.PerformedReaction.objects.get(pk=pr.object.pk)
                try:
                    pr2.duplicateOf = pr.object.duplicateOf
                    pr2.save()
                except DRP.models.PerformedReaction.DoesNotExist as e:
                    pass

            r = s.get(apiUrl + 'compound_quantities.xml', params=data)
            for cq in serializers.deserialize('xml', smart_str(r.text)):
                if hasattr(cq, 'amount'):
                    cq.amount = Decimal('{0:.5f}'.format(cq.amount))
                try:
                    cq.save()
                except InvalidOperation as e:
                    if hasattr(cq, 'amount'):
                        logger.debug(
                            "An invalid decimal conversion occured. Value is: {} from CompoundQuantity object {}".format(cq.amount, cq))
                    raise e
        else:
            print(s.cookies.get_dict())
            print(r.text)
            r.raise_for_status()
