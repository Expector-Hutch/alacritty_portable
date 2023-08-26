import os
import requests
import zipfile


def download():
    requests.packages.urllib3.disable_warnings()
    r = requests.get(
        "https://github.com/alacritty/alacritty/archive/refs/tags/"
        + requests.get(
            "https://api.github.com/repos/alacritty/alacritty/releases/latest",
            verify=False,
        ).json()["tag_name"]
        + ".zip",
        stream=True,
        verify=False,
    )

    with open("./alacritty.zip", "wb") as f:
        for chunk in r.iter_content(chunk_size=512):
            f.write(chunk)

    zip_file = zipfile.ZipFile("./alacritty.zip")

    for names in zip_file.namelist():
        zip_file.extract(names, "./")
    zip_file.close()

    os.remove("./alacritty.zip")
    os.rename(
        "alacritty-"
        + requests.get(
            "https://api.github.com/repos/alacritty/alacritty/releases/latest",
            verify=False,
        ).json()["tag_name"][1:],
        "alacritty",
    )


def rewrite():
    with open("./alacritty/alacritty/src/config/mod.rs", "r") as f:
        mod = f.readlines()

    mod = (
        mod[: mod.index("#[cfg(windows)]\n") + 1]
        + [
            "fn installed_config() -> Option<PathBuf> {\n",
            '    let fallback = env::current_dir().expect("REASON")'+
            '.join("alacritty.yml");\n',
            "    if fallback.exists() {\n",
            "        Some(fallback)\n",
            "    } else {\n",
            "        None\n",
            "    }\n",
            "}\n",
        ]
        + mod[
            mod[mod.index("#[cfg(windows)]\n"):].index("}\n")
            + mod.index("#[cfg(windows)]\n") + 1:
        ]
    )

    with open("./alacritty/alacritty/src/config/mod.rs", "w") as f:
        for line in mod:
            f.write(line)


def build():
    os.system("cd alacritty & cargo build --release")
    os.rename("./alacritty/target/release/alacritty.exe", "./alacritty.exe")
    os.system('powershell -Command "rm -r alacritty"')


def main():
    download()
    rewrite()
    build()


if __name__ == "__main__":
    main()
