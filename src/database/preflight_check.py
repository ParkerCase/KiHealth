"""
Pre-Flight Checklist for StarX Therapeutics Analysis
Validates that everything is ready before proceeding with analysis

Run this before starting any major analysis work!
"""

import os
import sys
from pathlib import Path
from datetime import datetime


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{text}{Colors.ENDC}")
    print("=" * 70)


def print_check(passed, message, details=""):
    if passed:
        symbol = f"{Colors.OKGREEN}✅{Colors.ENDC}"
        status = f"{Colors.OKGREEN}PASS{Colors.ENDC}"
    else:
        symbol = f"{Colors.FAIL}❌{Colors.ENDC}"
        status = f"{Colors.FAIL}FAIL{Colors.ENDC}"

    print(f"{symbol} [{status}] {message}")
    if details:
        print(f"         {details}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def check_directory_structure():
    """Check that all required directories exist"""
    print_header("1. Directory Structure")

    base_dir = Path(__file__).parent.parent.parent

    required_dirs = {
        "data/raw/depmap": "DepMap data files",
        "data/processed": "Processed analysis results",
        "notebooks": "Jupyter notebooks",
        "outputs/reports": "Analysis reports",
        "outputs/figures": "Visualizations",
        "src/analysis": "Analysis scripts",
        "src/database": "Database scripts",
        "src/dashboard": "Dashboard files",
    }

    all_good = True
    for dir_path, description in required_dirs.items():
        full_path = base_dir / dir_path
        exists = full_path.exists()
        print_check(exists, f"{dir_path}", description)
        if not exists:
            all_good = False

    return all_good


def check_depmap_files():
    """Check that all required DepMap files are downloaded"""
    print_header("2. DepMap Data Files")

    base_dir = Path(__file__).parent.parent.parent
    depmap_dir = base_dir / "data" / "raw" / "depmap"

    required_files = {
        "CRISPRGeneEffect.csv": (400, 600),  # Expected size range in MB
        "CRISPRGeneDependency.csv": (400, 600),
        "Model.csv": (0.5, 10),
        "OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv": (300, 600),
        "OmicsCNGeneWGS.csv": (80, 400),
        "OmicsSomaticMutationsMatrixDamaging.csv": (30, 250),
        "OmicsSomaticMutationsMatrixHotspot.csv": (5, 40),
    }

    all_good = True
    total_size = 0

    for filename, (min_mb, max_mb) in required_files.items():
        filepath = depmap_dir / filename
        exists = filepath.exists()

        if exists:
            size_mb = filepath.stat().st_size / (1024 * 1024)
            total_size += size_mb

            if min_mb <= size_mb <= max_mb:
                print_check(True, filename, f"{size_mb:.1f} MB")
            else:
                print_check(
                    False, filename, f"{size_mb:.1f} MB (expected {min_mb}-{max_mb} MB)"
                )
                all_good = False
        else:
            print_check(False, filename, "File not found")
            all_good = False

    print(f"\n   Total size: {total_size:.1f} MB (~{total_size/1024:.1f} GB)")

    return all_good


def check_python_environment():
    """Check Python version and key packages"""
    print_header("3. Python Environment")

    # Python version
    py_version = sys.version_info
    version_ok = py_version.major == 3 and py_version.minor >= 8
    print_check(
        version_ok,
        f"Python {py_version.major}.{py_version.minor}.{py_version.micro}",
        "Requires Python 3.8+",
    )

    # Key packages
    packages = {
        "pandas": "Data manipulation",
        "numpy": "Numerical computing",
        "matplotlib": "Plotting",
        "seaborn": "Statistical visualization",
        "sklearn": "Machine learning",
        "requests": "HTTP requests",
        "xata": "Xata database client",
        "Bio": "Bioinformatics tools",
        "jupyter": "Notebooks",
    }

    all_good = version_ok
    for package, description in packages.items():
        try:
            __import__(package)
            print_check(True, package, description)
        except ImportError:
            print_check(False, package, f"{description} (pip install {package})")
            all_good = False

    return all_good


def check_environment_variables():
    """Check .env file configuration"""
    print_header("4. Environment Variables")

    from dotenv import load_dotenv

    load_dotenv()

    required_vars = {
        "XATA_API_KEY": "Xata API authentication",
        "XATA_DB_URL": "Xata database URL",
    }

    all_good = True
    for var, description in required_vars.items():
        value = os.getenv(var)

        if value and value != f"your_{var.lower()}_here":
            # Check if it looks valid
            if var == "XATA_API_KEY" and value.startswith("xau_"):
                print_check(True, var, description)
            elif var == "XATA_DB_URL" and "xata.sh" in value:
                print_check(True, var, description)
            elif var not in ["XATA_API_KEY", "XATA_DB_URL"]:
                print_check(True, var, description)
            else:
                print_check(False, var, f"{description} (looks invalid)")
                all_good = False
        else:
            print_check(False, var, f"{description} (not configured)")
            all_good = False

    return all_good


def check_database_schema():
    """Check that Xata schema file exists and is valid"""
    print_header("5. Database Schema")

    base_dir = Path(__file__).parent
    schema_file = base_dir / "xata_schema.json"

    if not schema_file.exists():
        print_check(False, "xata_schema.json", "Schema file not found")
        return False

    print_check(True, "xata_schema.json", "Schema file exists")

    # Load and validate schema
    try:
        import json

        with open(schema_file, "r") as f:
            schema = json.load(f)

        tables = schema.get("tables", [])
        print_check(True, f"Schema valid", f"{len(tables)} tables defined")

        # Check expected tables
        expected_tables = [
            "papers",
            "cancer_indications",
            "multi_target_dependencies",
            "combination_predictions",
            "genetic_vulnerabilities",
            "depmap_cell_lines",
        ]

        table_names = [t["name"] for t in tables]
        for expected in expected_tables:
            exists = expected in table_names
            print_check(exists, f"Table: {expected}")

        return True

    except Exception as e:
        print_check(False, "Schema validation", f"Error: {e}")
        return False


def check_target_genes_in_data():
    """Verify target genes exist in DepMap data"""
    print_header("6. Target Gene Validation")

    base_dir = Path(__file__).parent.parent.parent
    effect_file = base_dir / "data" / "raw" / "depmap" / "CRISPRGeneEffect.csv"

    if not effect_file.exists():
        print_check(False, "Cannot validate", "CRISPRGeneEffect.csv not found")
        return False

    try:
        import pandas as pd

        # Read just the header
        df = pd.read_csv(effect_file, nrows=0)
        columns = df.columns.tolist()

        # Extract gene names from columns (format: "GENE (ID)")
        genes_in_data = set()
        for col in columns:
            if " " in col:
                gene = col.split(" ")[0]
                genes_in_data.add(gene)

        # Check target genes
        target_genes = ["STK17A", "MYLK4", "TBK1", "CLK4", "XPO1", "BTK"]

        all_found = True
        for gene in target_genes:
            found = gene in genes_in_data
            print_check(
                found,
                f"Target: {gene}",
                "Found in DepMap" if found else "NOT FOUND in DepMap",
            )
            if not found:
                all_found = False

        return all_found

    except Exception as e:
        print_check(False, "Validation failed", f"Error: {e}")
        return False


def check_disk_space():
    """Check available disk space"""
    print_header("7. Disk Space")

    import shutil

    base_dir = Path(__file__).parent.parent.parent
    stats = shutil.disk_usage(base_dir)

    total_gb = stats.total / (1024**3)
    used_gb = stats.used / (1024**3)
    free_gb = stats.free / (1024**3)

    print_info(f"Total: {total_gb:.1f} GB")
    print_info(f"Used: {used_gb:.1f} GB")
    print_info(f"Free: {free_gb:.1f} GB")

    # Warn if less than 5GB free
    has_space = free_gb >= 5
    print_check(
        has_space,
        "Free space check",
        f"{free_gb:.1f} GB available" if has_space else "WARNING: Less than 5 GB free",
    )

    return has_space


def generate_summary():
    """Generate overall summary"""
    print_header("Pre-Flight Summary")

    checks = {
        "Directory Structure": check_directory_structure(),
        "DepMap Files": check_depmap_files(),
        "Python Environment": check_python_environment(),
        "Environment Variables": check_environment_variables(),
        "Database Schema": check_database_schema(),
        "Target Genes": check_target_genes_in_data(),
        "Disk Space": check_disk_space(),
    }

    passed = sum(checks.values())
    total = len(checks)

    print(f"\n Overall Status: {passed}/{total} checks passed")

    if passed == total:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ ALL SYSTEMS GO!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}You're ready to start analysis work.{Colors.ENDC}")
        print("\n Next Steps:")
        print("   1. Run: python migrate_v2.py --setup (if not done)")
        print("   2. Run: python migrate_v2.py --create")
        print("   3. Start notebooks/01_explore_depmap.ipynb")
    else:
        print(f"\n{Colors.WARNING}⚠️  Some checks failed.{Colors.ENDC}")
        print(
            f"{Colors.WARNING}Please fix the issues above before proceeding.{Colors.ENDC}"
        )

        # List failures
        print("\n❌ Failed Checks:")
        for check, passed in checks.items():
            if not passed:
                print(f"   • {check}")

    return passed == total


def main():
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║         Pre-Flight Checklist - StarX Therapeutics Analysis       ║")
    print("║                                                                   ║")
    print("║  This validates your environment before starting analysis work   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    print(f"Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    all_good = generate_summary()

    print("\n" + "=" * 70)

    return 0 if all_good else 1


if __name__ == "__main__":
    sys.exit(main())
