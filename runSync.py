from pathlib import Path
import toml

include_files = [
    "LICENSE.txt",
    "__update_version__.py",
    ".pre-commit-config.yaml",
    "ruff.toml",
    "makefile",
    ".gptignore",
    ".gitignore",
]

def main():
    base_path = Path(__file__).parent.parent
    src_path = Path(__file__).parent / "templates"

    # list the directories in the base path
    for i in base_path.iterdir():
        if not i.is_dir():
            continue

        sync_file = i / ".python_repo_template.toml"
        if not sync_file.exists():
            continue

        pyproject_file = i / "pyproject.toml"
        pyproject_config = toml.load(pyproject_file)

        # fix the pyproject file
        fix_pyproject(pyproject_file, pyproject_config)

        template_config = toml.load(sync_file)
        exclude = template_config.get("exclude", [])

        for include_file in include_files:
            if include_file in exclude:
                continue

            src = src_path / include_file
            dest = i / include_file

            src_text = src.read_text()
            dest_text = ""
            if dest.exists():
                dest_text = dest.read_text()

            if include_file == "makefile":
                src_text = generate_makefile(pyproject_config, src_text)

            if not dest.exists() or src_text != dest_text:
                dest.write_text(src_text)
                print(f"Synced {include_file} to {i}")

def generate_makefile(pyproject_config, src_text) -> str:
    src_text = src_text.replace("{{project_name}}", pyproject_config["tool"]["poetry"]["name"])

    # find scripts and add them to the makefile
    if "scripts" in pyproject_config["tool"]["poetry"]:
        scripts = pyproject_config["tool"]["poetry"]["scripts"]
        
        phony_script_lines = []
        echo_script_lines = []
        scripts_lines = []
        
        for script_name, script_cmd in scripts.items():
            phony_script_lines.append(f"{script_name}")
            echo_script_lines.append(f'@echo "  {script_name.ljust(27)}Run {script_cmd}"')
            scripts_lines.append(f"{script_name}:\n\tpoetry run {script_name}")

        src_text = src_text.replace("{{scripts_phony}}", "\n".join(phony_script_lines))
        src_text = src_text.replace("{{scripts_echo}}", "\n".join(echo_script_lines))
        src_text = src_text.replace("{{scripts}}", "\n\n".join(scripts_lines))

    else:
        src_text = src_text.replace(" {{scripts_phony}}", "")
        src_text = src_text.replace("\n\t{{scripts_echo}}", "")
        src_text = src_text.replace("\n\n{{scripts}}", "")

    return src_text

def fix_pyproject(pyproject_file, pyproject_config):
    if "group" not in pyproject_config["tool"]["poetry"]:
        pyproject_config["tool"]["poetry"]["group"] = {}
    if "dev" not in pyproject_config["tool"]["poetry"]["group"]:
        pyproject_config["tool"]["poetry"]["group"]["dev"] = {}
        pyproject_config["tool"]["poetry"]["group"]["dev"]["dependencies"] = {}
    if "test" not in pyproject_config["tool"]["poetry"]["group"]:
        pyproject_config["tool"]["poetry"]["group"]["test"] = {}
        pyproject_config["tool"]["poetry"]["group"]["test"]["dependencies"] = {}

    dev_dependencies = pyproject_config["tool"]["poetry"]["group"]["dev"]["dependencies"]
    if "pre-commit" not in dev_dependencies:
        dev_dependencies["pre-commit"] = "^3.7.0"
    if "ruff" not in dev_dependencies:
        dev_dependencies["ruff"] = "^0.4.3"
    if "lazydocs" not in dev_dependencies:
        dev_dependencies["lazydocs"] = "^0.4.8"
    if "gptrepo" not in dev_dependencies:
        dev_dependencies["gptrepo"] = "^1.0.3"

    test_dependencies = pyproject_config["tool"]["poetry"]["group"]["test"]["dependencies"]
    if "pytest" not in test_dependencies:
        test_dependencies["pytest"] = "^8.2.0"
    if "pytest-cov" not in test_dependencies:
        test_dependencies["pytest-cov"] = "^3.0.0"
    if "pytest-xdist" not in test_dependencies:
        test_dependencies["pytest-xdist"] = "^3.6.1"
    if "nbmake" not in test_dependencies:
        test_dependencies["nbmake"] = "^1.5.3"
    if "mypy" not in test_dependencies:
        test_dependencies["mypy"] = "^1.10.0"

    project_name = pyproject_config["tool"]["poetry"]["name"]
    # tool.pytest.ini_options
    if "pytest" not in pyproject_config["tool"]:
        pyproject_config["tool"]["pytest"] = {}
    if "ini_options" not in pyproject_config["tool"]["pytest"]:
        pyproject_config["tool"]["pytest"]["ini_options"] = {}
        # testpaths = [ "tests",]
        pyproject_config["tool"]["pytest"]["ini_options"]["testpaths"] = ["tests"]
        pyproject_config["tool"]["pytest"]["ini_options"]["addopts"] = [f"--cov={project_name}"]
    
    toml.dump(pyproject_config, open("pyproject.toml", "w"))

if __name__ == "__main__":
    main()