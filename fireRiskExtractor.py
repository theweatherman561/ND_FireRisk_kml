from PIL import Image
import xml.etree.ElementTree as ET
import requests
from io import BytesIO

# Web URL to your PNG
PNG_URL = "https://gis.des.nd.gov/NDDESFireIndex.png"

# Fetch the image from the web
response = requests.get(PNG_URL)
response.raise_for_status()  # Will raise an error if download fails

# Load into PIL from bytes
img = Image.open(BytesIO(response.content)).convert("RGB")

# Access pixels as usual
pixels = img.load()

# CONFIGURATION
KML_IN = "northDakotaCounties.kml"
KML_OUT = "northDakotaFireRisk.kml"

# Define your manual mapping here: polygon ID → (x, y) pixel
pixel_map = {
    "38023": (369, 139),  # Divide County
    "38105": (369, 207),  # Williams County
    "38053": (374, 331),  # McKenzie County
    "38025": (411, 408),  # Dunn County
    "38033": (254, 471),  # Golden Valley County
    "38007": (325, 471),  # Billings County
    "38087": (354, 620),  # Slope County
    "38011": (351, 699),  # Bowman County
    "38001": (405, 691),  # Adams County
    "38041": (479, 618),  # Hettinger County
    "38089": (475, 549),  # Stark County
    "38061": (475, 231),  # Mountrail County
    "38013": (487, 119),  # Burke County
    "38075": (572, 124),  # Renville County
    "38101": (610, 316),  # Ward County
    "38055": (563, 377),  # McLean County
    "38057": (571, 436),  # Mercer County
    "38065": (656, 507),  # Oliver County
    "38059": (667, 616),  # Morton County
    "38037": (567, 629),  # Grant County
    "38085": (697, 683),  # Sioux County
    "38029": (779, 715),  # Emmons County
    "38015": (746, 488),  # Burleigh County
    "38083": (764, 373),  # Sheridan County
    "38049": (721, 304),  # McHenry County
    "38009": (745, 126),  # Bottineau County
    "38079": (825, 124),  # Rolette County
    "38069": (805, 219),  # Pierce County
    "38103": (875, 370),  # Wells County
    "38043": (842, 489),  # Kidder County
    "38047": (917, 619),  # Logan County
    "38051": (927, 690),  # McIntosh County
    "38021": (1073, 686),  # Dickey County
    "38045": (1065, 615),  # LaMoure County
    "38093": (978, 488),  # Stutsman County
    "38031": (997, 410),  # Foster County
    "38027": (997, 371),  # Eddy County
    "38005": (890, 261),  # Benson County
    "38095": (915, 131),  # Towner County
    "38019": (1047, 124),  # Cavalier County
    "38071": (1008, 224),  # Ramsey County
    "38063": (1070, 294),  # Nelson County
    "38067": (1156, 116),  # Pembina County
    "38099": (1171, 214),  # Walsh County
    "38035": (1179, 291),  # Grand Forks County
    "38039": (1069, 397),  # Griggs County
    "38091": (1137, 397),  # Steele County
    "38097": (1223, 394),  # Traill County
    "38003": (1102, 500),  # Barnes County
    "38017": (1228, 493),  # Cass County
    "38073": (1178, 610),  # Ransom County
    "38081": (1189, 693),  # Sargent County
    "38077": (1249, 636),  # Richland County
}

def rgb_to_kml_color(r, g, b):
    """Convert RGB to KML color format: aabbggrr."""
    return f"ff{b:02x}{g:02x}{r:02x}"

# Load and parse KML
tree = ET.parse(KML_IN)
root = tree.getroot()
ns = {'kml': 'http://www.opengis.net/kml/2.2'}
ET.register_namespace('', ns['kml'])

document = root.find("kml:Document", ns)
style_cache = {}

# Iterate placemarks
for placemark in document.findall(".//kml:Placemark", ns):
    fips_elem = placemark.find(".//kml:SimpleData[@name='FIPS']", ns)
    if fips_elem is None:
        continue

    fips = fips_elem.text.strip()

    if fips in pixel_map:
        x, y = pixel_map[fips]
        r, g, b = pixels[x, y]
        kml_color = rgb_to_kml_color(r, g, b)
        style_id = f"style_{r}_{g}_{b}"

        if style_id not in style_cache:
            # Add <Style> only once per unique color
            style = ET.Element("Style", id=style_id)
            poly = ET.SubElement(style, "PolyStyle")
            ET.SubElement(poly, "color").text = kml_color
            ET.SubElement(poly, "fill").text = "1"
            ET.SubElement(poly, "outline").text = "0"
            document.append(style)
            style_cache[style_id] = True

        # Add <styleUrl> to Placemark
        style_url = ET.Element("styleUrl")
        style_url.text = f"#{style_id}"
        placemark.append(style_url)
    else:
        print(f"Skipping FIPS {fips}: no pixel mapping found.")

# Save output
tree.write(KML_OUT, encoding="utf-8", xml_declaration=True)
