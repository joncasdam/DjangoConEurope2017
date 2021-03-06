# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from conference.cfp.models import Submission, WorkshopSubmission


class Slot(models.Model):
    """
    Model for conference time slots. It can be for a talk, a workshop, or a custom time slot (i. e. coffee break)
    """
    talk = models.ForeignKey(Submission, related_name='talks', limit_choices_to={'selected': True},
                             null=True, blank=True)
    workshop = models.ForeignKey(WorkshopSubmission, related_name='workshops', limit_choices_to={'selected': True},
                                 null=True, blank=True)
    name = models.CharField(_('Name'), max_length=250, null=True, blank=True,
                            help_text=_('Field for time slots that does not relate to a Talk or a Workshop.'))
    day = models.DateField(_('Date'))
    start = models.TimeField(_('Start'))
    duration = models.DurationField(_('Duration'))

    class Meta:
        verbose_name = _('Time slot')
        verbose_name_plural = _('Time slots')
        ordering = ('day', 'start')

    def clean(self):
        # ensure talk and workshop are NOT filled at the same time
        if self.talk and self.workshop:
            message = _('Please, select either a Talk or a Workshop, not both.')
            raise ValidationError({
                'talk': ValidationError(message=message, code='invalid'),
                'workshop': ValidationError(message=message, code='invalid'),
            })

    @property
    def title(self):
        if self.talk:
            return self.talk.proposal_title
        elif self.workshop:
            return self.workshop.proposal_title
        elif self.name:
            return self.name
        return ''

    @property
    def author(self):
        if self.talk:
            return self.talk.author
        elif self.workshop:
            return self.workshop.author
        return ''

    @property
    def abstract(self):
        if self.talk:
            return self.talk.proposal_abstract
        elif self.workshop:
            return self.workshop.proposal_abstract
        return ''

    @property
    def parsed_duration(self):
        minutes = self.duration.seconds//60
        hours = minutes//60
        if hours:
            minutes = minutes - (hours * 60)
            if minutes:
                return '{}h {}min'.format(hours, minutes)
            return '{}h'.format(hours)
        return '{}min'.format(minutes)

    def is_talk(self):
        return True if self.talk else False
    is_talk.short_description = _('Talk')
    is_talk.boolean = True

    def is_workshop(self):
        return True if self.workshop else False
    is_workshop.short_description = _('Workshop')
    is_workshop.boolean = True

    def is_custom(self):
        return True if self.name else False
    is_custom.short_description = _('Custom')
    is_custom.boolean = True
