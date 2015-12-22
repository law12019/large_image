#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

from girder import events
from girder.constants import AccessType
from girder.utility.model_importer import ModelImporter

from .rest import TilesItemResource


def _postUpload(event):
    """
    Called when a file is uploaded. We check the parent item to see if it is
    expecting a large image upload, and if so we register this file as the
    result image.
    """
    file = event.info['file']
    if 'itemId' not in file:
        return

    itemModel = ModelImporter.model('item')
    item = itemModel.load(file['itemId'], force=True, exc=True)

    if item.get('expectedLargeImage') and (file['name'].endswith('.tiff') or
            file.get('mimeType') == 'image/tiff'):
        del item['expectedLargeImage']
        item['largeImage'] = file['_id']
        itemModel.save(item)


def load(info):
    TilesItemResource(info['apiRoot'])

    ModelImporter.model('item').exposeFields(
        level=AccessType.READ, fields='largeImage')

    events.bind('data.process', 'large_image', _postUpload)
