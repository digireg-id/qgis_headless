/******************************************************************************
*  Project: NextGIS GIS libraries
*  Purpose: NextGIS headless renderer
*  Author:  Denis Ilyin, denis.ilyin@nextgis.com
*******************************************************************************
*  Copyright (C) 2020 NextGIS, info@nextgis.ru
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

#include "testlib.h"

#include <QString>
#include <QTest>

#include <lib.h>

TestLib::TestLib(int argc, char **argv, QObject *p)
    : QObject(p)
    , mArgc(argc)
    , mArgv(argv)
{

}

void TestLib::initTestCase()
{
    HeadlessRender::init(mArgc, mArgv);
}

void TestLib::testGetVersion()
{
    QVERIFY(!QString(HeadlessRender::getVersion()).isEmpty());
}

void TestLib::testRenderVector()
{
    QFile styleFile(QString("%1/rgbsmall.qml").arg(TEST_DATA_DIR));
    styleFile.open(QIODevice::ReadOnly);

    QString vectorFilePath = QString("%1/bld.shp").arg(TEST_DATA_DIR);

    auto image = HeadlessRender::renderVector(vectorFilePath.toStdString().c_str(),
                                              styleFile.readAll().data(),
                                              5.0, 10.0, 45.0, 40.0, 800, 600, 4326);

    QVERIFY(image->getData() != nullptr);
    QVERIFY(image->getSize() > 0);
}

void TestLib::testRenderRaster()
{
    QFile styleFile(QString("%1/rgbsmall.qml").arg(TEST_DATA_DIR));
    styleFile.open(QIODevice::ReadOnly);

    QString rasterFilePath = QString("%1/rgbsmall.tif").arg(TEST_DATA_DIR);

    auto image = HeadlessRender::renderRaster(rasterFilePath.toStdString().c_str(),
                                              styleFile.readAll().data(),
                                              -44.84, -23.10, -44.66, -22.93, 800, 600, 4326);

    QVERIFY(image->getData() != nullptr);
    QVERIFY(image->getSize() > 0);
}

void TestLib::cleanupTestCase()
{
    HeadlessRender::deinit();
}
