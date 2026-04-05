def split_index(string: str, start, available_width, delim) -> int:
    split_index = string.rfind(delim, start, available_width)
    if split_index == -1:
        split_index = string.find(delim, available_width)
        if split_index == -1:
            split_index = available_width
    return split_index

def next_head(long_str: str, columns: int) \
        -> tuple[str | None, str | None]:
    index = split_index(long_str, 0, columns, ' ')
    head = long_str[ :index ].rstrip()
    remains = long_str[ index: ].lstrip()
    return head, remains

def partition_to_column(long_str: str, columns: int) -> str:
    head, remains = next_head(long_str, columns)
    if len(remains) <= columns:
        return '\n'.join((head, remains))
    else:
        return head + '\n' + partition_to_column(remains, columns)
