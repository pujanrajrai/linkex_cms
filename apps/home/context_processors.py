from home.models import MyCompany

def company_context(request):
    company = MyCompany.objects.first()
    
    return {
        'company': company
    }