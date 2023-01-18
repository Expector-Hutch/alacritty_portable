import os
import requests
import zipfile

requests.packages.urllib3.disable_warnings()
r = requests.get("https://github.com/alacritty/alacritty/archive/refs/tags/"+requests.get("https://api.github.com/repos/alacritty/alacritty/releases/latest", verify=False).json()["tag_name"]+".zip", stream=True, verify=False)

with open("./alacritty.zip", "wb") as f:
    for chunk in r.iter_content(chunk_size=512):
        f.write(chunk)

zip_file = zipfile.ZipFile("./alacritty.zip")

for names in zip_file.namelist():
    zip_file.extract(names, "./")
zip_file.close()

os.remove('./alacritty.zip')
os.rename('alacritty-'+requests.get("https://api.github.com/repos/alacritty/alacritty/releases/latest", verify=False).json()["tag_name"][1:], 'alacritty')


with open('./alacritty/alacritty/src/config/mod.rs', 'r') as f:
    mod = f.readlines()

# mod = [mod[i][:-1] for i in range(len(mod))]

start = 0
while start < len(mod):
    if mod[start] == '#[cfg(windows)]\n':
        break
    start += 1
else:
    raise Exception("''#[cfg(windows)]' not fond.")

end = start
while end < len(mod):
    if mod[end] == '}\n':
        break
    end += 1

new_code = [
    'fn installed_config() -> Option<PathBuf> {\n',
    '    let fallback = env::current_dir().expect("REASON").join("alacritty.yml");\n',
    '    if fallback.exists() {\n',
    '        Some(fallback)\n',
    '    } else {\n',
    '        None\n',
    '    }\n',
    '}\n'
]

mod = mod[:start + 1] + new_code + mod[end + 1:]

with open('./alacritty/alacritty/src/config/mod.rs', 'w') as f:
    for line in mod:
        f.write(line)

os.system('cd alacritty & cargo build --release')
os.rename('./alacritty/target/release/alacritty.exe', './alacritty.exe')
os.system('powershell -Command "rm -r alacritty"')
