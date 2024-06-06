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
                src_text = src_text.replace("{{project_name}}", pyproject_config["tool"]["poetry"]["name"])

            if not dest.exists() or src_text != dest_text:
                dest.write_text(src_text)
                print(f"Synced {include_file} to {i}")

if __name__ == "__main__":
    main()