# from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

import osgeo
from osgeo import osr

from .utils import TypeRegistry

if TYPE_CHECKING:
    from .config import Config
    from .lint import Lint
    from .orders import Order
    from .pygen import PyGen

log = logging.getLogger("postprocess")


class Postprocessors(TypeRegistry["Postprocessor"]):
    """
    Registry of available Postprocessor implementations
    """

    def lint(self, *, lint: "Lint", name: str, defined_in: str, **kwargs):
        cls = self.registry.get(name)
        if cls is None:
            lint.warn_postprocessor(f"postprocessor {name!r} not found", defined_in=defined_in, name=name)
            return
        cls.lint(lint=lint, name=name, defined_in=defined_in, **kwargs)


postprocessors = Postprocessors()


class Postprocessor:
    def __init__(self, *, config: "Config", **kwargs):
        self.config = config

    @classmethod
    def lint(cls, lint: "Lint", *, name: str, defined_in: str, type: Optional[str] = None, **kwargs):
        """
        Consistency check the given input arguments
        """
        for k, v in kwargs.items():
            lint.warn_input(f"Unknown parameter: {k!r}", defined_in=defined_in, name=name)

    @classmethod
    def create(cls, name: str, **kwargs):
        try:
            impl_cls = postprocessors.by_name(name)
        except KeyError as e:
            raise KeyError(
                f"flavour requires unknown postprocessor {name}."
                f" Available: {', '.join(postprocessors.registry.keys())}"
            ) from e
        return impl_cls(**kwargs)

    def static_path(self, path: Path) -> Path:
        """
        Resolve path into an absolute path
        """
        for static_dir in self.config.static_dir:
            if not static_dir.is_dir():
                continue
            abspath = (static_dir / path).absolute()
            cp = Path(os.path.commonpath((abspath, static_dir)))
            if not cp.samefile(static_dir):
                raise RuntimeError(f"{path} leads outside the static directory")
            if not abspath.exists():
                continue
            return abspath
        raise RuntimeError(f"{path} does not exist inside {self.config.static_dir}")

    def add_python(self, order: "Order", full_relpath: str, gen: "PyGen") -> str:
        """
        Add a python function to postprocess the image at ``full_relpath``.

        Return the new value for ``full_relpath`` after the postprocessing
        """
        pass


@postprocessors.register
class Watermark(Postprocessor):
    """
    Write a string on the image.

    Parameters:

    * ``message``: text string to write
    * ``font``: name of a .ttf file to use as a font. The .ttf file needs to be
      found inside the static data directory
    * ``x``: horizontal coordinates (in pixel) of the beginning of the text. A
      negative value is the number of pixels from the right margin of the image
    * ``y``: vertical coordinates (in pixel) of the beginning of the text. A
      negative value is the number of pixels from the bottom margin of the image
    * ``anchor``: The text anchor alignment. See
      https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html#text-anchors
    * ``size``: font size in pixels (default: 10)
    * ``color``: color name as defined in
      https://pillow.readthedocs.io/en/stable/reference/ImageColor.html#color-names
      Default: "#fff0"
    """

    def __init__(
        self,
        *,
        message: str,
        font: str,
        size: int = 10,
        x: int,
        y: int,
        anchor: str = "la",
        color: str = "#fff0",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.message = message
        self.font: Path = self.static_path(Path(font))
        log.info("%s resolved as %s", font, self.font)
        self.x = x
        self.y = y
        self.anchor = anchor
        self.size = size
        self.color = color
        # TODO: text angle?

    @classmethod
    def lint(
        cls,
        lint: "Lint",
        *,
        message: str,
        font: str,
        size: int = 10,
        x: int,
        y: int,
        anchor: str = "la",
        color: Union[str, List[str]] = "#fff0",
        **kwargs,
    ):
        super().lint(lint, **kwargs)
        if not isinstance(message, str):
            lint.warn_input(f"message is not a string: {message!r}", **kwargs)
        if not isinstance(font, str):
            # TODO: try to resolve it?
            lint.warn_input(f"font is not a string: {font!r}", **kwargs)
        if not isinstance(size, int):
            lint.warn_input(f"size is not an integer: {size!r}", **kwargs)
        if not isinstance(x, int):
            lint.warn_input(f"x is not an integer: {x!r}", **kwargs)
        if not isinstance(y, int):
            lint.warn_input(f"y is not an integer: {y!r}", **kwargs)
        if not isinstance(anchor, str):
            lint.warn_input(f"anchor is not a string: {anchor!r}", **kwargs)
        if not isinstance(color, str):
            lint.warn_input(f"color is not a string: {color!r}", **kwargs)

    def add_python(self, order: "Order", full_relpath: str, gen: "PyGen") -> str:
        gen.import_("Image", "ImageDraw", "ImageFont", from_="PIL")
        gen.line(f"with Image.open(os.path.join(workdir, {full_relpath!r})) as im:")
        with gen.nested() as sub:
            sub.line("draw = ImageDraw.Draw(im)")
            sub.line(f"fnt = ImageFont.truetype({self.font!r}, size={self.size})")
            # Convert negative coordinates into coordinates relative to image size
            if self.x >= 0:
                x = str(self.x)
            else:
                x = f"im.width - {-self.x}"
            if self.y >= 0:
                y = str(self.y)
            else:
                y = f"im.height - {-self.y}"
            sub.line(f"draw.text(({x}, {y}), {self.message!r}, font=fnt, fill={self.color!r}, anchor={self.anchor!r})")
            sub.line(f"im.save(os.path.join(workdir, {full_relpath!r}))")
        return full_relpath


@postprocessors.register
class CutShape(Postprocessor):
    """
    Make the image transparent when outside a given shapefile

    Parameters:

    * ``shapefile``: name of the shapefile to use. The file needs to be found
      inside the static data directory
    """

    def __init__(self, *, shapefile: str, **kwargs):
        super().__init__(**kwargs)
        self.shapefile: Path = self.static_path(Path(shapefile))
        log.info("%s resolved as %s", shapefile, self.shapefile)

    @classmethod
    def lint(cls, lint: "Lint", **kwargs):
        shapefile = kwargs.pop("shapefile", None)
        if not isinstance(shapefile, str):
            # TODO: try to resolve it?
            lint.warn_input(f"shapefile is not a string: {shapefile!r}", **kwargs)
        super().lint(lint, **kwargs)

    def add_python(self, order: "Order", full_relpath: str, gen: "PyGen") -> str:
        georef = order.georeference()
        if georef is None:
            log.warning("%s: Order cannot be georeferenced: skipping CutShape postprocessing", order)
            return

        # Convert bounding box to map coordinates
        bbox = self.convert_magics_bbox_to_epsg(georef["bbox"], georef["epsg"])

        gen.import_("osgeo")
        gen.import_("gdal", "osr", from_="osgeo")

        # Open the shapefile in the script preamble, to open it only once
        # FIXME: there can be ambiguity if two shapefiles are used in the same
        # script, with the same basename and different paths. It doesn't seem
        # relevant, and if it becomes so we can change the mangling strategy
        shape_id = gen.to_identifier(os.path.basename(self.shapefile))
        # NOTA: ogr.Open non va bene perché gdal.Rasterize vuole un tipo GDALDatasetShadow
        # NOTA: Non serve riproiettare il vettoriale (che è in EPSG:32632, diversa dal raster)
        gen.preamble(shape_id, f"{shape_id} = gdal.OpenEx({self.shapefile!r}, gdal.OF_VECTOR)")

        # Open the PNG file and add georeferencing
        gen.line(f"ds_png = gdal.Open(os.path.join(workdir, {full_relpath!r}))")
        gen.line("srs = osr.SpatialReference()")
        gen.line(f"srs.ImportFromEPSG({georef['epsg']})")
        gen.line("ds_png.SetProjection(srs.ExportToWkt())")
        gen.line(
            "ds_png.SetGeoTransform(["
            f"{bbox[0]}, {bbox[2]-bbox[0]}/ds_png.RasterXSize, 0,"
            f" {bbox[3]}, 0, {bbox[1]-bbox[3]}/ds_png.RasterYSize])"
        )

        # Converto il PNG in un GeoTIFF in memoria usando il virtual FS di GDAL
        # https://gdal.org/user/virtual_file_systems.html#vsimem-in-memory-files
        # NOTA: si potrebbe anche usare il driver MEM e copiare a mano tutti i
        # metadati e dati, ma non offre vantaggi se non quello di non dover
        # fare l'unlink del file virtuale associato (vedi in fondo).
        # NOTA: il file è visibile all'interno del processo, quindi in caso di
        # multiprocesso non è un problema, ma nel caso di multithreading si
        # deve generare un nome univoco (e.g. con threading.get_ident())
        tif_path = "/vsimem/input.tif"
        gen.line(f"ds_tif = gdal.Translate({tif_path!r}, ds_png, format='GTiff')")
        # Ritaglio il GeoTIFF, scrivendo su tutte le bande
        gen.line(
            f"gdal.Rasterize(ds_tif, {shape_id}, inverse=True, bands=list(range(1, ds_tif.RasterCount + 1)),"
            " burnValues=(0,) * ds_tif.RasterCount)"
        )
        # Salvo il GeoTiff (alla fine di tutti i postprocessing)
        gen.line(f"gdal.Translate(os.path.join(workdir, {full_relpath!r}), ds_tif)")
        # NOTA: il file un memoria va chiuso manualmente. Si potrebbe fare una classe RAII
        gen.line(f"gdal.Unlink({tif_path!r})")

        return full_relpath

    @staticmethod
    def convert_magics_bbox_to_epsg(
        bbox: Tuple[float, float, float, float], epsg_out: int
    ) -> Tuple[float, float, float, float]:
        """
        Metodo per la conversione del bounding box di Magics (in EPSG:4326 e
        nella forma [LONMIN, LATMIN, LONMAX, LATMAX]).
        """
        srs_src = osr.SpatialReference()
        srs_src.ImportFromEPSG(4326)
        srs_dst = osr.SpatialReference()
        srs_dst.ImportFromEPSG(epsg_out)
        transform = osr.CoordinateTransformation(srs_src, srs_dst)
        # NOTA: in GDAL < 3 non viene rispettato l'ordine degli assi e viene
        # sempre usato l'ordine lon,lat. Vedi https://gdal.org/tutorials/osr_api_tut.html#crs-and-axis-order
        #
        # EPSG:4326 usa invece l'ordine lat,lon Se tutte le operazioni
        # successive con il bbox risultante sono delegate a GDAL (e.g.
        # SetGeoTransform) non importa più l'ordine in quanto è consistente con
        # la versione di GDAL stessa.
        # Non posso usare osgeo.gdal_version perché il simbolo è stato introdotto dalla versione 3.3.0
        if int(osgeo.__version__.split(".")[0]) < 3:
            lr = transform.TransformPoint(bbox[0], bbox[1])
            ul = transform.TransformPoint(bbox[2], bbox[3])
        else:
            lr = transform.TransformPoint(bbox[1], bbox[0])
            ul = transform.TransformPoint(bbox[3], bbox[2])

        return [lr[0], lr[1], ul[0], ul[1]]
