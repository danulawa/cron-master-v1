import requests
import chardet
from packaging.requirements import Requirement
from packaging.version import Version, InvalidVersion

REQ_FILE = "requirements.txt"


def ensure_utf8(file_path):
    with open(file_path, "rb") as f:
        raw = f.read()
        detected = chardet.detect(raw)
        encoding = detected["encoding"]

    print(f"Detected encoding: {encoding}")

    if encoding is None:
        print("⚠️ Could not detect encoding, assuming UTF-8")
        return

    if encoding.lower() != "utf-8":
        print(f"🔄 Converting from {encoding} to UTF-8...")

        try:
            text = raw.decode(encoding)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

            print("✅ Converted to UTF-8")
        except Exception as e:
            print(f"❌ Conversion failed: {e}")
    else:
        print("✅ Already UTF-8")


def get_latest_version(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        versions = data["releases"].keys()

        stable_versions = []
        for v in versions:
            try:
                ver = Version(v)
                if not ver.is_prerelease:
                    stable_versions.append(ver)
            except InvalidVersion:
                continue

        if not stable_versions:
            return None

        return str(sorted(stable_versions)[-1])

    except Exception as e:
        print(f"Error fetching {package_name}: {e}")
        return None


def parse_requirements(file_path):
    packages = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            try:
                req = Requirement(line)
                packages.append(req.name)
            except Exception:
                print(f"Skipping invalid line: {line}")

    return packages


def update_requirements(file_path):
    packages = parse_requirements(file_path)

    updated_lines = []

    for pkg in packages:
        print(f"Checking {pkg}...")
        latest_version = get_latest_version(pkg)

        if latest_version:
            updated_line = f"{pkg}=={latest_version}"
            print(f"  -> {updated_line}")
        else:
            updated_line = pkg
            print(f"  -> Could not fetch version")

        updated_lines.append(updated_line)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(updated_lines) + "\n")

    print("\n✅ requirements.txt updated successfully!")


if __name__ == "__main__":
    ensure_utf8(REQ_FILE)   # Normalize encoding first
    update_requirements(REQ_FILE)