"""Geo-pixel utilities and image compositing helpers.

GeoTransformer converts between GPS coordinates and pixel positions on a
satellite-image map. overlay_image_alpha composites a rotated BGRA overlay
onto a BGR background.
"""

import math

import cv2
import config


class GeoTransformer:
    """Convert between GPS coordinates and map pixel positions.

    Uses the WGS-84 latitude/longitude scale factors to project geographic
    coordinates onto a flat pixel grid anchored at (config.REF_LAT, config.REF_LON).

    The latitude scale factor accounts for Earth's oblateness:
        lat_m = 111132.954 - 559.822 * cos(2 * lat)   [metres per degree latitude]
    The longitude scale factor contracts toward the poles:
        lon_m = 111132.954 * cos(lat)                  [metres per degree longitude]

    Parameters
    ----------
    map_w_px : int
        Width of the map image in pixels. Used together with config.MAP_WIDTH_METERS
        to compute the pixels-per-metre ratio.
    """

    def __init__(self, map_w_px: int) -> None:
        self.pix_per_m: float = map_w_px / config.MAP_WIDTH_METERS

    def gps_to_pixels(self, lat: float, lon: float) -> tuple[int, int]:
        """Convert a GPS position to map pixel coordinates.

        The pixel origin (0, 0) corresponds to the reference point
        (config.REF_LAT, config.REF_LON) at the top-left of the map.

        Parameters
        ----------
        lat, lon : float
            GPS position in decimal degrees.

        Returns
        -------
        tuple[int, int]
            (x, y) pixel coordinates on the map. x increases eastward,
            y increases southward (standard image convention).
        """
        lat_m = 111132.954 - 559.822 * math.cos(2 * math.radians(lat))
        lon_m = 111132.954 * math.cos(math.radians(lat))
        dy = -(lat - config.REF_LAT) * lat_m
        dx = (lon - config.REF_LON) * lon_m
        return int(dx * self.pix_per_m), int(dy * self.pix_per_m)

    def pixels_to_gps(self, x: int, y: int) -> tuple[float, float]:
        """Convert map pixel coordinates back to a GPS position.

        Inverse of gps_to_pixels(). Scale factors are evaluated at the
        reference latitude (config.REF_LAT) for the inverse transform.

        Parameters
        ----------
        x, y : int
            Pixel coordinates on the map (origin at top-left).

        Returns
        -------
        tuple[float, float]
            (lat, lon) in decimal degrees.
        """
        dx = x / self.pix_per_m
        dy = y / self.pix_per_m
        lat_m = 111132.954 - 559.822 * math.cos(2 * math.radians(config.REF_LAT))
        lon_m = 111132.954 * math.cos(math.radians(config.REF_LAT))
        d_lat = -(dy / lat_m)
        d_lon = dx / lon_m
        return config.REF_LAT + d_lat, config.REF_LON + d_lon


def overlay_image_alpha(
    background,
    overlay,
    x: int,
    y: int,
    target_w: int,
    target_h: int,
    rotation_deg: float = 0,
) -> None:
    """Composite a BGRA overlay onto a BGR background with alpha blending and rotation.

    The overlay is resized to (target_w, target_h), padded to its bounding diagonal,
    rotated, then alpha-blended onto the background centred at (x, y). Regions that
    fall outside the background are clipped silently.

    If target_w is 0 it is computed from target_h to preserve the overlay aspect ratio.

    Parameters
    ----------
    background : numpy.ndarray
        BGR image (H x W x 3) to draw onto. Modified in place.
    overlay : numpy.ndarray or None
        BGRA image (H x W x 4) to composite. If None or invalid size, returns immediately.
    x, y : int
        Centre position on the background where the overlay is placed.
    target_w, target_h : int
        Desired width and height in pixels after resize. If target_w is 0, it is
        auto-computed from target_h while preserving aspect ratio.
    rotation_deg : float, optional
        Counter-clockwise rotation in degrees (default 0).
    """
    if overlay is None:
        return
    h_src, w_src = overlay.shape[:2]

    # Auto-compute width from height if width is zero
    if target_w == 0:
        scale = target_h / h_src
        target_w = int(w_src * scale)
    if target_w <= 0 or target_h <= 0:
        return

    try:
        resized = cv2.resize(overlay, (target_w, target_h))
    except Exception:
        return

    # Pad to bounding diagonal so rotation doesn't clip corners
    diag = int(math.sqrt(target_w ** 2 + target_h ** 2))
    pad_x = (diag - target_w) // 2
    pad_y = (diag - target_h) // 2
    padded = cv2.copyMakeBorder(
        resized, pad_y, pad_y, pad_x, pad_x, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0)
    )

    # Rotate around centre
    h_pad, w_pad = padded.shape[:2]
    rot_matrix = cv2.getRotationMatrix2D((w_pad // 2, h_pad // 2), rotation_deg, 1.0)
    rotated = cv2.warpAffine(padded, rot_matrix, (w_pad, h_pad))

    # Compute placement bounds and clip to background
    y1 = y - h_pad // 2
    y2 = y1 + h_pad
    x1 = x - w_pad // 2
    x2 = x1 + w_pad
    h_bg, w_bg = background.shape[:2]
    y1_c = max(0, y1)
    y2_c = min(h_bg, y2)
    x1_c = max(0, x1)
    x2_c = min(w_bg, x2)
    if y1_c >= y2_c or x1_c >= x2_c:
        return

    # Corresponding region in the rotated overlay
    ov_y1 = y1_c - y1
    ov_y2 = ov_y1 + (y2_c - y1_c)
    ov_x1 = x1_c - x1
    ov_x2 = ov_x1 + (x2_c - x1_c)
    overlay_crop = rotated[ov_y1:ov_y2, ov_x1:ov_x2]
    bg_crop = background[y1_c:y2_c, x1_c:x2_c]

    # Alpha blend (per-channel): out = (1 - alpha) * bg + alpha * overlay
    if overlay_crop.shape[2] == 4:
        alpha = overlay_crop[:, :, 3] / 255.0
        for c in range(3):
            bg_crop[:, :, c] = (1.0 - alpha) * bg_crop[:, :, c] + alpha * overlay_crop[:, :, c]
    else:
        background[y1_c:y2_c, x1_c:x2_c] = overlay_crop
