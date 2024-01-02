
def user_group(request):
    is_customer = request.user.groups.filter(name='customer').exists()
    return {'is_customer': is_customer}