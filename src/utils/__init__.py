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
from .customqueue import CustomQueue
from .ttsworker import GTTSWorker
from .messagehandler import smart_print
from .multipageembed import MultiPageEmbed, PageEmbedManager
from .urlresolver import (get_quick_info,
                          get_full_info,
                          resolve_video_urls)

__all__ = ['CustomQueue',
           'GTTSWorker',
           'MultiPageEmbed',
           'PageEmbedManager',
           'get_quick_info',
           'get_full_info',
           'resolve_video_urls',
           'smart_print']
