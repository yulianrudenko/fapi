def generate_id(clubs) -> int:
    if clubs:
        return clubs[-1].id + 1
    else:
        return 1
