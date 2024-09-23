def normilize_date(created_at):
    '''Formats the given date to a standard date format.'''
    if created_at is None:
        return None
    return created_at.date()
