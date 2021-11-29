
async def smart_print(ctx, message: str, data: list = None):

    count = message.count('%s')
    length = 0 if data is None else len(data)

    if data is None and count > 0:
        raise KeyError('Expecting values but none were provided.')

    if count != length:
        raise KeyError(
            'Values to insert do not match the expected amount. '
            f'Expected: {count}, Provided: {length}')

    splits = message.split('%s')
    message = ''.join(f'{splits[i]}{data[i]}' for i in range(0, count))
    message += splits[count]

    await ctx.send(f'> {message}')


async def block_print(ctx, message: str, data: list = None):
    pass
