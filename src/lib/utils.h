/******************************************************************************
*  Project: NextGIS GIS libraries
*  Purpose: NextGIS headless renderer
*  Author:  Denis Ilyin, denis.ilyin@nextgis.com
*******************************************************************************
*  Copyright (C) 2021 NextGIS, info@nextgis.ru
*
*   This program is free software: you can redistribute it and/or modify
*   it under the terms of the GNU General Public License as published by
*   the Free Software Foundation, either version 3 of the License, or
*   (at your option) any later version.
*   This program is distributed in the hope that it will be useful,
*   but WITHOUT ANY WARRANTY; without even the implied warranty of
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*   GNU General Public License for more details.
*
*   You should have received a copy of the GNU General Public License
*   along with this program.  If not, see <http://www.gnu.org/licenses/>.
******************************************************************************/

#ifndef QGIS_HEADLESS_UTILS_H
#define QGIS_HEADLESS_UTILS_H

#include <qgswkbtypes.h>
#include <QVariant>
#include "layer.h"

namespace HeadlessRender
{
    QgsWkbTypes::Type layerGeometryTypeToQgsWkbType( HeadlessRender::Layer::GeometryType geometryType );
    QVariant::Type layerAttributeTypetoQVariantType( HeadlessRender::Layer::AttributeType attributeType );
}

#endif // QGIS_HEADLESS_UTILS_H
