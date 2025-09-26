import os
import platform
import click
from jinja2 import Template
from pathlib import Path

DESKTOP_TEMPLATE = Path(__file__).parent / "desktop.jinja2"
INFO_PLIST_TEMPLATE = Path(__file__).parent / "Info.plist.jinja2"
APP_SCRIPT_TEMPLATE = Path(__file__).parent / "app_script.jinja2"


@click.group()
def asapp():
    """Launch websites in app mode."""
    ...


@click.option(
    "--chrome", "-c",
    help="The chromium/google chrome binary to use.",
    default=None,
)
@click.argument("url")
@asapp.command()
def open(chrome, url):
    """Open a url in app mode."""
    if chrome is None:
        chrome = get_default_chrome()
    os.system(f"{chrome} --app={url}")


@click.option(
    "--chrome", "-c",
    help="The chromium/google chrome binary to use.",
    default=None,
)
@click.option(
    "--icon", "-i",
    help="Path to an icon file to use as the icon.",
    default=None,
    type=click.Path(),
)
@click.option(
    "--name",
    prompt="What would you like to name the desktop entry?",
)
@click.argument("url")
@asapp.command()
def shortcut(chrome, url, icon, name):
    """Add a desktop entry for the app version of a given URL."""
    if chrome is None:
        chrome = get_default_chrome()
    
    if icon is None:
        icon = get_default_icon()
    
    if platform.system() == "Darwin":  # macOS
        create_macos_app(chrome, url, icon, name)
    else:  # Linux
        create_linux_desktop_entry(chrome, url, icon, name)
    
    click.secho(f"A desktop entry has been added for {url}", fg="green")


def get_default_chrome():
    """Get the default Chrome binary for the current OS."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"
        ]
    else:  # Linux
        chrome_paths = [
            "chromium-browser",
            "google-chrome",
            "chromium",
            "google-chrome-stable",
            "google-chrome-beta"
        ]
    
    for path in chrome_paths:
        if system == "Darwin":
            if os.path.exists(path):
                return path
        else:
            # Check if command exists
            result = os.system(f"which {path} > /dev/null 2>&1")
            if result == 0:
                return path
    
    # Fallback
    if system == "Darwin":
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    else:
        return "chromium-browser"


def get_default_icon():
    """Get the default icon path for the current OS."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericApplicationIcon.icns"
    else:  # Linux
        return "/usr/share/icons/locolor"


def create_linux_desktop_entry(chrome, url, icon, name):
    """Create a Linux desktop entry."""
    template = Template(DESKTOP_TEMPLATE.read_text())
    rendered = template.render(
        url=url,
        icon=icon,
        chrome=chrome,
        name=name,
    )

    filename = name.replace(" ", "_").lower()
    desktop_path = Path(f"~/.local/share/applications/{filename}.desktop").expanduser()
    desktop_path.write_text(rendered)


def create_macos_app(chrome, url, icon, name):
    """Create a macOS .app bundle."""
    # Create app bundle directory structure
    app_name = name.replace(" ", "_")
    app_path = Path(f"~/Applications/{app_name}.app").expanduser()
    contents_path = app_path / "Contents"
    macos_path = contents_path / "MacOS"
    resources_path = contents_path / "Resources"
    
    # Create directories
    macos_path.mkdir(parents=True, exist_ok=True)
    resources_path.mkdir(parents=True, exist_ok=True)
    
    # Create Info.plist
    bundle_id = f"com.asapp.{app_name.lower()}"
    info_plist_template = Template(INFO_PLIST_TEMPLATE.read_text())
    info_plist_content = info_plist_template.render(
        name=name,
        bundle_id=bundle_id
    )
    (contents_path / "Info.plist").write_text(info_plist_content)
    
    # Create executable script
    script_template = Template(APP_SCRIPT_TEMPLATE.read_text())
    script_content = script_template.render(
        name=name,
        chrome=chrome,
        url=url
    )
    script_path = macos_path / f"{name}.sh"
    script_path.write_text(script_content)
    script_path.chmod(0o755)  # Make executable
    
    # Copy icon if provided and exists
    if icon and os.path.exists(icon):
        icon_ext = Path(icon).suffix
        icon_dest = resources_path / f"icon{icon_ext}"
        import shutil
        shutil.copy2(icon, icon_dest)
        
        # Update Info.plist to reference the icon
        info_plist_content = info_plist_content.replace(
            '<string>????</string>',
            f'<string>icon{icon_ext}</string>'
        )
        (contents_path / "Info.plist").write_text(info_plist_content)
