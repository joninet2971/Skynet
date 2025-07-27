from django import template

register = template.Library()

@register.simple_tag
def get_seat(seats, row, column):
    for seat in seats:
        if seat.row == row and seat.column == column:
            return seat
    return None