import os.path
from binascii import a2b_hex
from packaging import version

import pytest

from qgis_headless import (
    MapRequest, CRS, Layer, Style, set_svg_paths, get_qgis_version,
    StyleTypeMismatch,
)
from qgis_headless.util import to_pil, image_stat, render_vector, render_raster, EXTENT_ONE

QGIS_VERSION = version.parse(get_qgis_version().split('-')[0])

WKB_MSC = a2b_hex('01010000005070B1A206CF42409CDCEF5014E04B40')  # POINT (37.61739 55.75062)
EPSG_4326_WKT = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AXIS["Latitude",NORTH],AXIS["Longitude",EAST],AUTHORITY["EPSG","4326"]]'  # NOQA
EPSG_3395_WKT = 'PROJCS["WGS 84 / World Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","3395"]]'  # NOQA


def test_contour(shared_datadir, reset_svg_paths):
    data = shared_datadir / 'contour.geojson'
    style = (shared_datadir / 'contour-rgb.qml').read_text()

    extent = (9757454.0, 6450871.0, 9775498.0, 6465163.0)

    img = render_vector(data, style, extent, 1024, svg_resolver=lambda x: x)
    # img.save('test_contour.png')

    stat = image_stat(img)

    assert stat.alpha.min == 0, "There are no transparent pixels found"
    assert stat.red.max == 255, "Labels aren't visible"
    assert stat.green.max == 255, "Primary lines aren't visible"
    assert stat.blue.max == 255, "Primary lines aren't visible"

    assert 3 < stat.red.mean < 4
    assert 12 < stat.green.mean < 13
    assert 29 < stat.blue.mean < 30


def test_opacity(shared_datadir, reset_svg_paths):
    data = shared_datadir / 'contour.geojson'
    style = (shared_datadir / 'contour-opacity.qml').read_text()

    extent = (9757454.0, 6450871.0, 9775498.0, 6465163.0)

    img = render_vector(data, style, extent, 1024)
    # img.save('test_opacity.png')

    stat = image_stat(img)

    assert stat.alpha.min == 0, "There are no transparent pixels found"
    assert stat.alpha.max == 127, "Maximum alpha must be 127 (50%)"


def test_rule_based_labeling(shared_datadir, reset_svg_paths):
    data = shared_datadir / 'contour.geojson'
    style = (shared_datadir / 'contour-rbl.qml').read_text()

    extent = (9757454.0, 6450871.0, 9775498.0, 6465163.0)

    img = render_vector(data, style, extent, 1024)
    # img.save('test_rule_based_labeling.png')

    stat = image_stat(img)
    assert stat.green.max == 255, "Green labels aren't visible"
    assert stat.blue.max == 255, "Blue labels aren't visible"


def test_marker_simple(shared_datadir, reset_svg_paths):
    data = shared_datadir / 'zero.geojson'
    style = (shared_datadir / 'zero-marker.qml').read_text()

    set_svg_paths([str(shared_datadir / 'marker-blue'), ])
    img = render_vector(data, style, EXTENT_ONE, 256)
    # img.save('test_marker_simple.png')

    stat = image_stat(img)

    assert stat.red.max == stat.green.max == 0, "Unexpected data in red or green channel"
    assert stat.blue.max == 255, "Blue marker is missing"


def test_marker_change(shared_datadir, reset_svg_paths):
    data = shared_datadir / 'zero.geojson'
    style = (shared_datadir / 'zero-marker.qml').read_text()

    # Render with blue marker in SVG paths
    set_svg_paths([str(shared_datadir / 'marker-blue'), ])
    img = render_vector(data, style, EXTENT_ONE, 256)
    assert image_stat(img).blue.max == 255, "Blue marker is missing"

    # Render with green marker in SVG paths
    set_svg_paths([str(shared_datadir / 'marker-green'), ])
    img = render_vector(data, style, EXTENT_ONE, 256)
    assert image_stat(img).green.max == 255, "Green marker is missing"


@pytest.mark.skipif(not os.path.exists('/usr/share/qgis/svg'),
                    reason="Builtin SVG icons are missing")
def test_svg_builtin(shared_datadir, reset_svg_paths):
    data = shared_datadir / 'zero.geojson'
    style = (shared_datadir / 'zero-builtin.qml').read_text()

    set_svg_paths(['/usr/share/qgis/svg', ])

    layer = Layer.from_ogr(str(data))
    style = Style.from_string(style)

    img = render_vector(layer, style, EXTENT_ONE, 256)
    assert image_stat(img).red.max == 255, "Red marker is missing"


def test_svg_resolver(shared_datadir, reset_svg_paths):
    data = shared_datadir / 'zero.geojson'
    style_marker = (shared_datadir / 'zero-marker.qml').read_text()

    color = None
    resolved = list()

    def _resolver(source):
        target = str((shared_datadir / 'marker-{}'.format(color) / source).resolve())
        resolved.append(source)
        return target

    color = 'blue'
    resolved.clear()

    img = render_vector(
        data, style_marker, EXTENT_ONE, 256,
        svg_resolver=_resolver)
    assert resolved == ['marker.svg'], "Marker isn't resolved"
    assert image_stat(img).blue.max == 255, "Blue marker is missing"

    color = 'green'
    resolved.clear()

    img = render_vector(
        data, style_marker, EXTENT_ONE, 256,
        svg_resolver=_resolver)
    assert resolved == ['marker.svg'], "Marker isn't resolved"
    assert image_stat(img).green.max == 255, "Green marker is missing"

    color = 'missing'
    resolved.clear()

    img = render_vector(
        data, style_marker, EXTENT_ONE, 256,
        svg_resolver=_resolver)

    stat = image_stat(img)
    assert resolved == ['marker.svg'], "Marker isn't resolved"
    assert stat.red.min == stat.green.min == stat.blue.min == 0, "Black question mark is missing"

    style_svg_fill = (shared_datadir / 'zero-svg-fill.qml').read_text()

    color = 'blue'
    resolved.clear()

    img = render_vector(
        data, style_svg_fill, EXTENT_ONE, 256,
        svg_resolver=_resolver)
    assert resolved == ['marker.svg'], "Marker isn't resolved"
    assert image_stat(img).blue.max == 255, "Blue marker is missing"


@pytest.mark.skipif(
    QGIS_VERSION < version.parse('3.14'),
    reason="Fetching marker by URL may fail in QGIS < 3.14",
)
def test_marker_url(shared_datadir, reset_svg_paths, capfd):
    data = shared_datadir / 'zero.geojson'
    style = (shared_datadir / 'zero-marker-url.qml').read_text()

    img = render_vector(data, style, EXTENT_ONE, 256)
    # img.save('test_marker_url.png')

    assert capfd.readouterr().out.strip() == '', "QGIS stdout output was captured"
    assert capfd.readouterr().err.strip() == '', "QGIS stderr output was captured"
    assert image_stat(img).red.max == 255, "Red marker is missing"


def test_svg_cache(shared_datadir, reset_svg_paths):
    data = shared_datadir / 'zero.geojson'
    style = (shared_datadir / 'zero-marker.qml').read_text()
    marker = (shared_datadir / 'marker-blue' / 'marker.svg').resolve()

    layer = Layer.from_ogr(str(data))
    style = Style.from_string(style, svg_resolver=lambda _: str(marker))

    req = MapRequest()
    req.set_crs(CRS.from_epsg(3857))
    req.add_layer(layer, style)

    rendered_image = req.render_image(EXTENT_ONE, (256, 256))
    img = to_pil(rendered_image)
    assert image_stat(img).blue.max == 255, "Blue marker is missing"

    marker.unlink()  # Remove marker file from directory

    # And render again
    rendered_image = req.render_image(EXTENT_ONE, (256, 256))
    img = to_pil(rendered_image)
    assert image_stat(img).blue.max == 255, "Marker is missing in same MapRequest"

    # Recreata MapRequest with same Layer and Style
    req = MapRequest()
    req.set_crs(CRS.from_epsg(3857))
    req.add_layer(layer, style)

    # And render again
    rendered_image = req.render_image(EXTENT_ONE, (256, 256))
    img = to_pil(rendered_image)
    assert image_stat(img).blue.max == 255, "Marker is missing in new MapRequest"


def test_legend(shared_datadir, reset_svg_paths):
    data = shared_datadir / 'contour.geojson'
    style = (shared_datadir / 'contour-rgb.qml').read_text()

    req = MapRequest()
    req.set_dpi(96)
    req.set_crs(CRS.from_epsg(3857))

    req.add_layer(
        Layer.from_ogr(str(data)),
        Style.from_string(style),
        label="Contour")

    rendered_legend = req.render_legend()
    img = to_pil(rendered_legend)
    # img.save('test_legend.png')

    assert img.size == (223, 92), "Expected size is 223 x 92"

    stat = image_stat(img)
    assert stat.green.max == 255, "Primary lines aren't visible"
    assert stat.blue.max == 255, "Primary lines aren't visible"
    assert stat.red.mean == 0
    assert 1 < stat.green.mean < 3
    assert 1 < stat.blue.mean < 3

    req.set_dpi(2 * 96)
    rendered_legend = req.render_legend()
    hdpi_img = to_pil(rendered_legend)

    assert img.size[0] < hdpi_img.size[0] and img.size[1] < hdpi_img.size[1], \
        "Higher DPI should produce bigger legend"


def test_legend_svg_path(shared_datadir, reset_svg_paths):
    data = shared_datadir / 'zero.geojson'
    style = (shared_datadir / 'zero-marker.qml').read_text()

    set_svg_paths([str(shared_datadir / 'marker-blue'), ])

    req = MapRequest()
    req.set_dpi(96)
    req.set_crs(CRS.from_epsg(3857))

    req.add_layer(
        Layer.from_ogr(str(data)),
        Style.from_string(style),
        label="Marker")

    rendered_legend = req.render_legend()
    img = to_pil(rendered_legend)
    # img.save('test_legend_svg_path.png')

    stat = image_stat(img)
    assert stat.blue.max == 255, "Blue marker is missing"


def test_legend_svg_resolver(shared_datadir, reset_svg_paths):
    data = shared_datadir / 'zero.geojson'
    style = (shared_datadir / 'zero-marker.qml').read_text()
    marker = (shared_datadir / 'marker-blue' / 'marker.svg').resolve()

    req = MapRequest()
    req.set_dpi(96)
    req.set_crs(CRS.from_epsg(3857))

    req.add_layer(
        Layer.from_ogr(str(data)),
        Style.from_string(style, svg_resolver=lambda _: str(marker)),
        label="Marker")

    rendered_legend = req.render_legend()
    img = to_pil(rendered_legend)
    # img.save('test_legend_svg_resolver.png')

    stat = image_stat(img)
    assert stat.blue.max == 255, "Blue marker is missing"


@pytest.mark.parametrize('crs, extent, extent_empty', (
    pytest.param(CRS.from_epsg(4326), (37.60, 55.74, 37.62, 55.76),
                                      (37.60, 57.74, 37.62, 57.76), id='from EPSG:4326'),
    pytest.param(CRS.from_wkt(EPSG_4326_WKT), (37.60, 55.74, 37.62, 55.76),
                 (37.60, 57.74, 37.62, 57.76), id='from WKT EPSG:4326'),
    pytest.param(CRS.from_epsg(3857), (4187547.0, 7508930.0, 4187549.0, 7508932.0),
                 (4187547.0, 7473582.0, 4187549.0, 7473584.0), id='from EPSG:3857'),
    pytest.param(CRS.from_wkt(EPSG_3395_WKT), (4187547.0, 7473582.0, 4187549.0, 7473584.0),
                 (4187547.0, 7508930.0, 4187549.0, 7508932.0), id='from WKT EPSG:3395'),
))
def test_render_crs(shared_datadir, crs, extent, extent_empty):
    source_crs = CRS.from_epsg(4326)
    layer = Layer.from_data(Layer.GT_POINT, source_crs, tuple(), (
        (1, WKB_MSC, tuple()),
    ))

    style = (shared_datadir / 'zero-red-circle.qml').read_text()

    img = render_vector(layer, style, extent, 1024, crs=crs)

    stat = image_stat(img)
    assert stat.green.max == stat.blue.max == 0, "Unexpected data in blue or green channel"
    assert stat.red.max == 255, "Red marker is missing"

    img_empty = render_vector(layer, style, extent_empty, 256, crs=crs)
    stat = image_stat(img_empty)
    assert stat.red.max == stat.green.max == stat.blue.max == 0, "Unexpected non-empty image"


def test_attribute_color(shared_datadir):
    data = shared_datadir / 'landuse' / 'landuse.geojson'
    layer = Layer.from_ogr(str(data))

    style = (shared_datadir / 'landuse' / 'landuse.qml').read_text()

    img = render_vector(layer, style, (4189314.0, 7505071.0, 4190452.0, 7506101.0),
                        svg_resolver=lambda x: x)

    stat = image_stat(img)

    assert stat.red.max == 255, "Red polygon is missing"
    assert stat.green.max == 255, "Green polygon is missing"
    assert stat.blue.max == 0, "Blue band is not expected"


def test_style_25d(shared_datadir):
    data = shared_datadir / 'poly.geojson'
    layer = Layer.from_ogr(str(data))

    style = (shared_datadir / '25d' / 'poly_25d.qml').read_text()

    img = render_vector(layer, style, (7298419.0, 7795268.0, 7298536.0, 7795397.0))

    stat = image_stat(img)

    assert stat.red.max == 255, "Shadow is missing"
    assert stat.blue.max == 255, "Roof is missing"
    assert stat.green.max == pytest.approx(255, abs=1), "Walls are missing"


def test_raster(shared_datadir):
    layer = Layer.from_gdal(str(shared_datadir / 'raster' / 'rounds.tif'))
    style = Style.from_file(str(shared_datadir / 'raster' / 'rounds.qml'))

    img = render_raster(layer, style, (251440.0, 5977974.0, 1978853.0, 7505647.0))
    stat = image_stat(img)
    assert (stat.red.max, stat.green.max, stat.blue.max) == (255, 0, 0), "Red colour missing"

    img = render_raster(layer, style, (3848936.0, 5977974.0, 5503915.0, 7505647.0))
    stat = image_stat(img)
    assert (stat.red.max, stat.green.max, stat.blue.max) == (0, 255, 0), "Green colour missing"

    img = render_raster(layer, style, (251440.0, 2556073.0, 1978853.0, 4158374.0))
    stat = image_stat(img)
    assert (stat.red.max, stat.green.max, stat.blue.max) == (0, 0, 255), "Blue colour missing"

    img = render_raster(layer, style, (3848936.0, 2556073.0, 5503915.0, 4158374.0))
    stat = image_stat(img)
    assert (stat.red.max, stat.green.max, stat.blue.max) == (0, 0, 0), "Black colour missing"


def test_raster_layer_vector_style(shared_datadir):
    layer = Layer.from_gdal(str(shared_datadir / 'raster' / 'rounds.tif'))
    style = Style.from_file(str(shared_datadir / 'point-style.qml'))

    mreq = MapRequest()
    with pytest.raises(StyleTypeMismatch):
        mreq.add_layer(layer, style)


def test_vector_layer_raster_style(shared_datadir):
    layer = Layer.from_ogr(str(shared_datadir / 'poly.geojson'))
    style = Style.from_file(str(shared_datadir / 'raster' / 'rounds.qml'))

    mreq = MapRequest()
    with pytest.raises(StyleTypeMismatch):
        mreq.add_layer(layer, style)