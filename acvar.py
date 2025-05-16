import sys
import re
from binstar_client.inspect_package import pypi
from binstar_client.inspect_package.uitls import extract_first
from binstar_client.utils import detect
from anaconda_cli_base.cli import app
from variantlib.constants import METADATA_VARIANT_HASH_HEADER
from variantlib.constants import METADATA_VARIANT_PROPERTY_HEADER
import zipfile


def inspect_pypi_package_whl_variant(filename, fileobj):
    # took it directly from: https://github.com/wheelnext/variantlib/blob/main/variantlib/commands/analyze_wheel.py#L69-L87 
    # later we can use variantlib, once it provide API for inspecting pypi package
    package_data, release_data, file_data = pypi.inspect_pypi_package_whl(filename, fileobj)

    data = extract_first(zipfile.ZipFile(fileobj), '*.dist-info/METADATA')

    hash_match = re.search(rf"{METADATA_VARIANT_HASH_HEADER}: (\w+)", data)
    hash_value = hash_match.group(1) if hash_match else None
    if hash_value:
        variant_matches = re.findall(
            rf"{METADATA_VARIANT_PROPERTY_HEADER}: (.+)", data
        )
        if variant_matches:
            file_data['attrs']['variant_hash'] = hash_value
            file_data['attrs']['variant_properties'] = variant_matches

    print(f"Uploaded file attributes: {file_data['attrs']}")
    return package_data, release_data, file_data


def inspect_pypi_package_with_variant(filename, fileobj, *args, **kwargs):
    if filename.endswith('.whl'):
        return inspect_pypi_package_whl_variant(filename, fileobj)
    else:
        return pypi.inspect_pypi_package(filename, fileobj)

detect.INSPECTORS[detect.PackageType.STANDARD_PYTHON] = inspect_pypi_package_with_variant


if __name__ == '__main__':
    sys.exit(app())
