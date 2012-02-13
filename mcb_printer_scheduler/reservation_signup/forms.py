from django import forms 
from datetime import timedelta

from reservation_type.conflict_checker import ConflictChecker
from reservation_type.time_slot_maker import TimeSlot

from calendar_event.models import CalendarEvent, Reservation

from django.contrib.localflavor.us.forms import USPhoneNumberField

class SignupForm(forms.Form):
    """Form used for a regular user to reserve a time."""

    time_slot = forms.DateTimeField(label='Available times', widget=forms.Select)
    session_length = forms.IntegerField(widget=forms.HiddenInput)
    phone_number = USPhoneNumberField(label='Contact Phone')
    email = forms.EmailField(label='Contact Email')
    
    
    def init(self, time_slot_choices, session_length, **kwargs):   
        self.fields['time_slot'].widget.choices = time_slot_choices
        self.fields['session_length'].initial = session_length

        self.fields['email'].initial = kwargs.get('contact_email', '')
        self.fields['phone_number'].initial = kwargs.get('phone', '')



    def get_time_slot_object(self):
        
        time_slot = self.cleaned_data.get('time_slot', None)
        session_length = self.cleaned_data.get('session_length', None)
        
        try:
            end_datetime = time_slot + timedelta(minutes=session_length)
            return TimeSlot(time_slot, end_datetime)
        except:
            return None
            
    def clean(self):
        """Make sure the slot is still available"""
        time_slot = self.cleaned_data.get('time_slot', None)
        session_length = self.cleaned_data.get('session_length', None)

        if time_slot is None:
            self._errors['time_slot'] = self.error_class(['This field is required.'])
            raise forms.ValidationError('Please choose an available time')

        if session_length is None:
            self._errors['session_length'] = self.error_class(['This field is required.'])
            raise forms.ValidationError('Please enter a start time')

        ts_obj = self.get_time_slot_object()
        if ts_obj is None:
            raise forms.ValidationError('The time slot is invalid.  Please try again.')
        
        conflict_checker = ConflictChecker()
        if conflict_checker.does_timeslot_conflict(ts_obj):
             self._errors['time_slot'] = self.error_class(['Please choose a different time.'])
             raise forms.ValidationError('Sorry!  Someone reserved that time slot!  Please choose another one.')
            
        return self.cleaned_data
            
    def get_reservation(self, calendar_user):
        print '>>> get_reservation'
        if calendar_user is None:
            return None
        
        ts_obj = self.get_time_slot_object()
        if ts_obj is None:
            return None
            
        res = Reservation(user=calendar_user\
                        , contact_email=self.cleaned_data.get('email')\
                        , contact_phone=self.cleaned_data.get('phone_number')\
                        , start_datetime = ts_obj.start_datetime\
                        , end_datetime = ts_obj.end_datetime\
                        #, billing_code=self.cleaned_data.get('billing_code', '')\
                        )        
        res.save()          # save the reservation
        
        # update user's contact info
        calendar_user.contact_email = res.contact_email
        calendar_user.phone_number = res.contact_phone
        calendar_user.save()

        return res
              
        #res = CalendarEvent(
        #             start_datetime = ts_obj.start_datetime
        #            , end_datetime = ts_obj.end_datetime
        #        )
        res.save()

        return res
        res = Reservation(user=calendar_user \
                , start_datetime = ts_obj.start_datetime \
                , end_datetime = ts_obj.end_datetime \
                , contact_email=self.cleaned_data.get('email') \
                , contact_phone=self.cleaned_data.get('phone_number') \
                , display_name=str(calendar_user)
        )
        res.save()
        
        return res

        res = CalendarEvent(
                     start_datetime = ts_obj.start_datetime
                    , end_datetime = ts_obj.end_datetime
                )
        res.save()
        return res

       