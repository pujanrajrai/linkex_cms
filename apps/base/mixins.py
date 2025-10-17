class CaseSensitiveFieldsMixin:
    """
    Mixin to define which fields should preserve their case.
    Fields that should remain in their original case:
    - username
    - email
    - password
    - contact numbers
    - document numbers
    - reference numbers
    - URLs
    - file paths
    """
    CASE_SENSITIVE_FIELDS = {
        'username',
        'email',
        'password',
        'contact_no',
        'contact_no_1',
        'contact_no_2',
        'phone_number',
        'document_number',
        'reference_number',
        'reference_no',
        'url',
        'file_path',
        'logo',
        'company_pan_vat',
        'citizenship_front',
        'citizenship_back',
        'passport',
        'box_label',
        'label_1',
        'label_2',
        'label_3',
        'label_4',
        'label_5',
    }
