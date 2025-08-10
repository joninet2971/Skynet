from datetime import date, datetime

def get_time_data(request):
    return {
        'current_year': date.today().year,
        'current_date': date.today()
    }

def user_name(request):
    if request.user.is_authenticated:
        return {"current_user_name": request.user.username}
    return {"current_user_name": None}