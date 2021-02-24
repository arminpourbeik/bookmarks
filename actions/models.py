from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Action(models.Model):
    user = models.ForeignKey(
        to='auth.User',
        related_name='actions',
        db_index=True,
        on_delete=models.CASCADE
    )
    verb = models.CharField(max_length=255)
    # A ForeignKey field that points to the ContentType model
    target_ct = models.ForeignKey(to=ContentType,
                                  blank=True,
                                  null=True,
                                  related_name='target_obj',
                                  on_delete=models.CASCADE,)
    # A field for storing the primary key of the related object
    target_id = models.PositiveIntegerField(blank=True,
                                            null=True,
                                            db_index=True)
    # A field to the related object based on the combination of the two previous fields
    target = GenericForeignKey('target_ct', 'target_id')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)

