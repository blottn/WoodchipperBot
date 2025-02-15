import re
import discord


def chunk_response(response, max_chunk_length=2000, add_spoiler_tags=False):
    if add_spoiler_tags:
        max_chunk_length -= 4

    response_chunks = []

    while len(response) > max_chunk_length:
        breakpoint = re.search(r'(\n+).*$', response[:max_chunk_length])     # note that, by default, '.' does not match '\n'

        if breakpoint:
            response_chunks.append(response[:breakpoint.start(1)])
            response = response[breakpoint.end(1):]
        else:
            break

    if response:
        response_chunks.append(response)

    if add_spoiler_tags:
        response_chunks = [f'||{chunk}||' for chunk in response_chunks]

    return response_chunks


async def send_chunked_response(ctx : discord.ApplicationContext, response : str, **kwargs):
    for chunk in chunk_response(response, **kwargs):
        await ctx.respond(chunk)
