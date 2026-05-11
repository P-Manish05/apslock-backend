from icalendar import Calendar, Event, vText
from datetime import datetime
import pytz


def generate_ics(booking_date, start_time, end_time,
                  attendee_name, attendee_email, meet_link):
    cal = Calendar()
    cal.add('prodid', '-//APSLOCK//Consultation//EN')
    cal.add('version', '2.0')
    cal.add('method', 'REQUEST')

    event = Event()

    ist = pytz.timezone('Asia/Kolkata')
    start_datetime = ist.localize(
        datetime.combine(booking_date, start_time)
    )
    end_datetime = ist.localize(
        datetime.combine(booking_date, end_time)
    )

    event.add('summary', 'APSLOCK Free Consultation Call')
    event.add('dtstart', start_datetime)
    event.add('dtend', end_datetime)
    event.add('description', f"""
Your free consultation call with APSLOCK team.

Meeting Link: {meet_link}

What to expect:
- 45 minute call
- Discuss your requirements
- Our team will show you how we can help
- Completely free, no obligations

See you on the call!
Team APSLOCK
    """)
    event.add('location', meet_link)
    event['organizer'] = vText(f'mailto:{attendee_email}')

    cal.add_component(event)
    return cal.to_ical()