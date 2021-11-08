# -*- coding: utf-8 -*-
'''
Copyright (c) 2021 Oliver Clarke.

This file is part of HermesBot.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from youtube_dl import YoutubeDL

ytdlopts = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
ytdl = YoutubeDL(ytdlopts)


def get_quick_info(url):
    """Extract quick information from YouTube.
    This request does not process the url.
    """
    return ytdl.extract_info(url, download=False, process=False)


def get_full_info(url):
    """Extract the full information from YouTube.
    This request processes the url or search.
    """
    return ytdl.extract_info(url, download=False, process=True)


def resolve_video_urls(list):
    """
    Resolve video information from a list of urls.
    This uses you `YoutubeDL.extract_info()` to retrieve
    video information.

    :param list: The list of urls to resolve
    :return: List of resolved urls
    """
    results = []
    for item in list:
        res = get_full_info(item['search'])  # Perform the search

        # Handle cases where a list is returned
        if('entries' in res):
            en_list = list(res.get('entries'))
            if(len(en_list) >= 1):
                res = res.get('entries')[0]
            else:
                res = {'title': 'None'}

        results.append(res)
    return results
