from home.models import Company

def company_context(request):
    company = Company.objects.first()
    
    return {
        'company': company
    }