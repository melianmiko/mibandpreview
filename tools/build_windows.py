import os
import shutil
import site
import subprocess

WINDOWS_PYINSTALLER_ARGS = {
    "name": "mibandpreview",
    "icon": r"..\mibandpreview_qt\res\icon.ico",
    "windowed": True,
    "hidden-import": [
        "certifi"
    ],
    "add-data": [
        r"..\mibandpreview\res;mibandpreview\res",
        r"..\mibandpreview_qt\res;mibandpreview_qt\res",
        r"..\mibandpreview_qt\qt;mibandpreview_qt\qt"
    ]
}


def make_win32():
    base_wd = os.getcwd()
    args = mk_args(WINDOWS_PYINSTALLER_ARGS)
    path = base_wd + "\\tools\\win32-entrypoint.py"

    os.environ["PYTHONPATH"] = base_wd

    # Go to builddir
    if not os.path.isdir(os.getcwd() + "/builddir"):
        os.mkdir(os.getcwd() + "/builddir")
    if os.path.isdir("builddir/dist"):
        shutil.rmtree("builddir/dist")

    # Make Qt parts
    print("-- make qt")
    os.chdir(base_wd + "/mibandpreview_qt")
    subprocess.Popen(["pyside2-uic", "qt/app.ui", "-o", "ui_frames.py"]).wait()
    os.chdir(base_wd + "/mibandpreview_qt/qt")
    subprocess.Popen(["pyside2-lupdate", "app.pro"]).wait()

    # Build command and run
    command = ["pyinstaller"] + args + [path]
    print("-- starting", command)
    os.chdir(base_wd + "/builddir")
    subprocess.Popen(command).wait()

    # Run nsis
    shutil.copy(base_wd + "/tools/installer.nsi", base_wd + "/builddir/dist/installer.nsi")
    print("-- makensis...")
    os.chdir(base_wd + "/builddir/dist")
    subprocess.Popen([r"C:\Program Files (x86)\NSIS\Bin\makensis", "installer.nsi"]).wait()

    os.chdir(base_wd)


def mk_args(args):
    out = []
    for prop in args:
        value = args[prop]
        if isinstance(value, bool) and value:
            out.append("--" + prop)
        elif isinstance(value, list):
            for b in value:
                out.append("--" + prop)
                out.append(b)
        else:
            out.append("--" + prop + "=" + str(value))
    return out


if __name__ == "__main__":
    make_win32()
